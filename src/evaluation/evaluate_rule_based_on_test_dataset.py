import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from chat.chat_engine import ChatEngine


# Change this path if your test file is somewhere else
TEST_FILE = PROJECT_ROOT / "data" / "processed" / "test_with_tools.jsonl"
OUTPUT_FILE = PROJECT_ROOT / "src" / "evaluation" / "rule_based_test_dataset_results.json"


def load_jsonl(path):
    records = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    return records


def get_expected_target(record):
    policy_decision = record.get("policy_decision", {})

    return {
        "domain": record.get("domain"),
        "intent": record.get("intent", "unknown"),
        "slots": record.get("normalized_slots", {}),
        "next_action": policy_decision.get("next_action", "fallback"),
        "missing_slots": policy_decision.get("missing_slots", []),
    }


def normalize_expected_slots(slots, domain):
    if not slots:
        return {
            domain: {
                "search_slots": {},
                "booking_slots": {}
            }
        }

    if domain in slots:
        return slots

    search_slots = {}
    booking_slots = {}

    booking_slot_names = {
        "people",
        "day",
        "stay",
        "time",
        "departure",
        "destination",
        "leave_at",
        "arrive_by",
    }

    for slot, value in slots.items():
        if slot in booking_slot_names:
            booking_slots[slot] = str(value).lower()
        else:
            search_slots[slot] = str(value).lower()

    return {
        domain: {
            "search_slots": search_slots,
            "booking_slots": booking_slots
        }
    }


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


def evaluate_record(record):
    chat = ChatEngine(nlu_mode="rule_based")

    utterance = record.get("utterance", "")
    result = chat.process_message(utterance)

    final_state = result["dialogue_state"]
    final_nlu = result["nlu_result"]
    final_policy = result["policy_decision"]
    final_tool_result = result["tool_result"]

    expected = get_expected_target(record)

    expected_domain = expected["domain"]
    expected_intent = expected["intent"]
    expected_action = expected["next_action"]
    expected_missing_slots = expected["missing_slots"]

    expected_slots = normalize_expected_slots(
        expected["slots"],
        expected_domain
    )

    actual_domain = final_policy.get("domain") or final_nlu.get("domain")
    actual_intent = final_nlu.get("intent")
    actual_action = final_policy.get("next_action")
    actual_missing_slots = final_policy.get("missing_slots", [])

    expected_domain_slots = expected_slots.get(expected_domain, {})
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
        "id": record.get("id"),
        "utterance": utterance,

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
        "response": result["response"],
        "final_state": final_state,
    }


def pct(count, total):
    return 0 if total == 0 else 100 * count / total


def print_summary(results):
    total = len(results)

    metrics = {
        "Task completion": sum(1 for r in results if r["task_completed"]),
        "Domain accuracy": sum(1 for r in results if r["domain_correct"]),
        "Intent accuracy": sum(1 for r in results if r["intent_correct"]),
        "Action accuracy": sum(1 for r in results if r["action_correct"]),
        "Slot accuracy": sum(1 for r in results if r["slots_correct"]),
        "Missing-slot accuracy": sum(1 for r in results if r["missing_slots_correct"]),
        "Tool/API success": sum(1 for r in results if r["tool_success"]),
    }

    print("\nRule-Based Baseline Test Dataset Evaluation")
    print("-" * 60)
    print(f"Total records: {total}")

    for name, value in metrics.items():
        print(f"{name}: {value}/{total} = {pct(value, total):.2f}%")

    failed = [r for r in results if not r["task_completed"]]

    print(f"\nFailed cases: {len(failed)}")

    for r in failed[:20]:
        print("=" * 80)
        print("Utterance:", r["utterance"])
        print("Expected:", r["expected_domain"], r["expected_intent"], r["expected_action"])
        print("Actual:", r["actual_domain"], r["actual_intent"], r["actual_action"])
        print("Slot errors:", r["slot_errors"])
        print("Expected missing:", r["expected_missing_slots"])
        print("Actual missing:", r["actual_missing_slots"])


def main():
    if not TEST_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {TEST_FILE}. "
            "Update TEST_FILE to your actual test_with_tools.jsonl path."
        )

    records = load_jsonl(TEST_FILE)

    results = []

    for index, record in enumerate(records):
        if index % 100 == 0:
            print(f"Evaluating {index}/{len(records)}")

        result = evaluate_record(record)
        results.append(result)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print_summary(results)
    print(f"\nSaved detailed results to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()