import json
import sys
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))


BASE_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
ADAPTER_DIR = PROJECT_ROOT / "models" / "mistral-travel-chatbot-qlora"


SYSTEM_PROMPT = """You are an NLU and action prediction module for a travel booking chatbot.

Your task is to read the user message and current dialogue state, then return valid JSON with:
- domain
- intent
- slots
- next_action
- missing_slots

Allowed domains:
hotel, restaurant, taxi, attraction

Allowed intents:
search_hotel, book_hotel, search_restaurant, book_restaurant, book_taxi, search_attraction, unknown

Return ONLY valid JSON.
"""


def get_device():
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def load_model():
    device = get_device()
    print(f"Using device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float16 if device == "mps" else torch.float32,
        low_cpu_mem_usage=True,
    )

    model = PeftModel.from_pretrained(base_model, ADAPTER_DIR)
    model.to(device)
    model.eval()

    return tokenizer, model, device


def run_inference(tokenizer, model, device, user_message, current_state=None):
    if current_state is None:
        current_state = {}

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": f"""User message:
{user_message}

Current dialogue state:
{json.dumps(current_state, ensure_ascii=False)}

Return the JSON output.
""",
        },
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    input_length = inputs["input_ids"].shape[1]

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=160,
            do_sample=False,
            repetition_penalty=1.15,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    generated_tokens = outputs[0][input_length:]
    generated_text = tokenizer.decode(generated_tokens, skip_special_tokens=True)

    return generated_text.strip()


def main():
    tokenizer, model, device = load_model()

    test_messages = [
        "I need a cheap hotel in the north with parking.",
        "Book it for 2 people on Friday for 3 nights.",
        "Find me an Italian restaurant in the centre.",
        "I need a taxi from the hotel to the restaurant by 7 pm.",
        "Find me a museum in the centre.",
    ]

    for message in test_messages:
        print("=" * 80)
        print("User:", message)
        output = run_inference(tokenizer, model, device, message)
        print("Model output:")
        print(output)


if __name__ == "__main__":
    main()