"""
state_tracker.py
policy.py
tool_router.py
response_templates.py
rule_based_nlu.py
rule_based_nlu → state_tracker → policy → tool_router → response_templates
"""

from dialogue.state import create_empty_state
from dialogue.state_tracker import update_state
from dialogue.policy import decide_next_action
from dialogue.response_templates import generate_response
from nlu.rule_based_nlu import parse_user_message as rule_based_parse
from nlu.prompt_nlu import PromptNLU
from tools.tool_router import run_tool


class ChatEngine:
    def __init__(self, dialogue_id="live_chat", nlu_mode="rule_based"):
        self.dialogue_id = dialogue_id
        self.state = create_empty_state()
        self.nlu_mode = nlu_mode

        if self.nlu_mode == "llm":
            self.llm_nlu = PromptNLU()
        else:
            self.llm_nlu = None

    def reset(self):
        self.state = create_empty_state()

    def parse_message(self, user_message):
        current_domain = self.state.get("active_domain")

        if self.nlu_mode == "llm":
            return self.llm_nlu.parse_user_message(
                user_message,
                current_domain=current_domain,
            )

        return rule_based_parse(
            user_message,
            current_domain=current_domain,
        )

    def process_message(self, user_message):
        nlu_result = self.parse_message(user_message)

        self.state = update_state(
            current_state=self.state,
            normalized_slots=nlu_result.get("normalized_slots", {}),
            dialogue_id=self.dialogue_id,
        )

        intent = nlu_result.get("intent", "unknown")

        policy_decision = decide_next_action(
            dialogue_state=self.state,
            intent=intent,
        )

        tool_result = run_tool(
            policy_decision=policy_decision,
            dialogue_state=self.state,
        )

        response = generate_response(
            policy_decision=policy_decision,
            tool_result=tool_result,
        )

        return {
            "user_message": user_message,
            "nlu_result": nlu_result,
            "dialogue_state": self.state,
            "policy_decision": policy_decision,
            "tool_result": tool_result,
            "response": response,
        }