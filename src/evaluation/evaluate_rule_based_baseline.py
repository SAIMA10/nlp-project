import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

from chat.chat_engine import ChatEngine


EVAL_FILE = PROJECT_ROOT / "src" / "evaluation" / "evaluation_prompts.json"
OUTPUT_FILE = PROJECT_ROOT / "src" / "evaluation" / "rule_based_baseline_results.json"

def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_domain_slots(state, domain):
    return (
        state
        .get("domains", {})
        .get(domain, {
            "search_slots": {},
            "booking_slots": {}
        })
    )


def compare_slots(expected_domain_slots, actual_domain_slots):
    errors = []

    for section in ["search_slots", "booking_slots"]:
        expected_section = expected_domain_slots.get(section, {})
        actual_section = actual_domain_slots.get(section, {})

        for slot, expected_value in expected_section.items():
            actual_value = actual_section.get(slot)

            if str(actual_value).lower() != str(expected_value).lower():
                errors.append({
                    "section": section,
                    "slot": slot,
                    "expected": expected_value,
                    "actual": actual_value,
                })

    return errors


def evaluate_case(case):
    chat = ChatEngine(nlu_mode="rule_based")

    final_result = None

    for message in case["messages"]:
        final_result = chat.process_message(message)

    final_state = final_result["dialogue_state"]
    final_nlu = final_result["nlu_result"]
    final_policy = final_result["policy_decision"]
    final_tool_result = final_result["tool_result"]

    expected_domain = case.get("expected_domain")
    expected_intent = case.get("expected_intent")
    expected_action = case.get("expected_action")
    expected_missing_slots = case.get("expected_missing_slots", [])

    actual_domain = final_policy.get("domain") or final_nlu.get("domain")
    actual_intent = final_nlu.get("intent")
    actual_action = final_policy.get("next_action")
    actual_missing_slots = final_policy.get("missing_slots", [])

    expected_domain_slots = case.get("expected_slots", {}).get(expected_domain, {})
    actual_domain_slots = get_domain_slots(final_state, expected_domain)

    slot_errors = compare_slots(expected_domain_slots, actual_domain_slots)

    domain_correct = actual_domain == expected_domain
    intent_correct = actual_intent == expected_intent
    action_correct = actual_action == expected_action
    slots_correct = len(slot_errors) == 0
    missing_slots_correct = set(actual_missing_slots) == set(expected_missing_slots)

    tool_expected = expected_action not in {"ask_missing_slot", "fallback"}

    if tool_expected:
        tool_success = final_tool_result.get("status") == "success"
    else:
        tool_success = final_tool_result.get("status") in {"skipped", "success"}

    task_completed = (
        domain_correct
        and intent_correct
        and action_correct
        and slots_correct
        and missing_slots_correct
        and tool_success
    )

    return {
        "id": case.get("id"),
        "messages": case.get("messages"),

        "expected_domain": expected_domain,
        "actual_domain": actual_domain,
        "domain_correct": domain_correct,

        "expected_intent": expected_intent,
        "actual_intent": actual_intent,
        "intent_correct": intent_correct,

        "expected_action": expected_action,
        "actual_action": actual_action,
        "action_correct": action_correct,

        "expected_missing_slots": expected_missing_slots,
        "actual_missing_slots": actual_missing_slots,
        "missing_slots_correct": missing_slots_correct,

        "slots_correct": slots_correct,
        "slot_errors": slot_errors,

        "tool_status": final_tool_result.get("status"),
        "tool_success": tool_success,

        "task_completed": task_completed,
        "final_response": final_result["response"],
        "final_state": final_state,
    }


def pct(count, total):
    if total == 0:
        return 0
    return 100 * count / total


def print_summary(results):
    total = len(results)

    completed = sum(1 for r in results if r["task_completed"])
    domain_correct = sum(1 for r in results if r["domain_correct"])
    intent_correct = sum(1 for r in results if r["intent_correct"])
    action_correct = sum(1 for r in results if r["action_correct"])
    slots_correct = sum(1 for r in results if r["slots_correct"])
    missing_correct = sum(1 for r in results if r["missing_slots_correct"])
    tool_success = sum(1 for r in results if r["tool_success"])

    print("\nRule-Based Baseline Evaluation Summary")
    print("-" * 50)
    print(f"Total cases: {total}")
    print(f"Task completion: {completed}/{total} = {pct(completed, total):.2f}%")
    print(f"Domain accuracy: {domain_correct}/{total} = {pct(domain_correct, total):.2f}%")
    print(f"Intent accuracy: {intent_correct}/{total} = {pct(intent_correct, total):.2f}%")
    print(f"Action accuracy: {action_correct}/{total} = {pct(action_correct, total):.2f}%")
    print(f"Slot accuracy: {slots_correct}/{total} = {pct(slots_correct, total):.2f}%")
    print(f"Missing-slot accuracy: {missing_correct}/{total} = {pct(missing_correct, total):.2f}%")
    print(f"Tool/API success: {tool_success}/{total} = {pct(tool_success, total):.2f}%")

    failed = [r for r in results if not r["task_completed"]]

    if failed:
        print("\nFailed cases:")
        for r in failed:
            print("=" * 80)
            print("ID:", r["id"])
            print("Messages:", r["messages"])
            print("Expected action:", r["expected_action"])
            print("Actual action:", r["actual_action"])
            print("Slot errors:", r["slot_errors"])
            print("Expected missing:", r["expected_missing_slots"])
            print("Actual missing:", r["actual_missing_slots"])
            print("Response:", r["final_response"])


def main():
    cases = load_json(EVAL_FILE)

    results = []

    for case in cases:
        result = evaluate_case(case)
        results.append(result)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print_summary(results)
    print(f"\nSaved detailed results to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()