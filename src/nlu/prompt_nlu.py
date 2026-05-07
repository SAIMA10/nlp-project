import json
import re

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

from preprocessing.normalize_slots import normalize_slot_value_pairs
from preprocessing.define_intent import define_intents_for_record


MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"


class PromptNLU:
    def __init__(self, model_name=MODEL_NAME):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype="auto",
        )

        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
        )

    def build_prompt(self, message, current_domain=None):
        return f"""
You are an NLU module for a travel booking chatbot.

Extract:
1. domain
2. raw slot-value pairs

Allowed domains:
- hotel
- restaurant
- taxi
- attraction

Allowed raw slots:
hotel/restaurant/attraction:
- area
- pricerange
- stars
- type
- parking
- internet
- name
- food
- bookpeople
- bookday
- bookstay
- booktime

taxi:
- departure
- destination
- leaveat
- arriveby

Current domain, if any: {current_domain}

User message:
{message}

Return ONLY valid JSON in this format:
{{
  "domain": "hotel|restaurant|taxi|attraction|null",
  "slots": {{
    "slot_name": "value"
  }}
}}
"""

    def extract_json(self, text):
        match = re.search(r"\{.*\}", text, re.DOTALL)

        if not match:
            return None

        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

    def parse_user_message(self, message, current_domain=None):
        prompt = self.build_prompt(message, current_domain=current_domain)

        output = self.generator(
            prompt,
            max_new_tokens=256,
            do_sample=False,
            temperature=0.0,
            return_full_text=False,
        )[0]["generated_text"]

        parsed = self.extract_json(output)

        if not parsed:
            return {
                "domain": None,
                "intent": "unknown",
                "raw_slots": {},
                "normalized_slots": {},
                "llm_raw_output": output,
            }

        domain = parsed.get("domain")

        if domain == "null":
            domain = current_domain

        raw_slots = parsed.get("slots", {}) or {}

        normalized_slots = normalize_slot_value_pairs(
            raw_slots,
            default_domain=domain,
        )

        intents = define_intents_for_record(normalized_slots)

        if len(intents) == 1:
            intent = next(iter(intents.values()))
        elif len(intents) > 1:
            intent = "multi_domain"
        else:
            intent = "unknown"

        return {
            "domain": domain,
            "intent": intent,
            "raw_slots": raw_slots,
            "normalized_slots": normalized_slots,
            "llm_raw_output": output,
        }