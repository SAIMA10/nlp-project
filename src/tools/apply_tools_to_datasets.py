import json
from collections import Counter
from pathlib import Path

from tool_router import run_tool


SPLITS = ["train", "dev", "test"]


def apply_tools_for_split(split):
    input_file = Path(f"data/processed/{split}_with_policy.jsonl")
    output_file = Path(f"data/processed/{split}_with_tools.jsonl")

    if not input_file.exists():
        print(f"Skipping {split}: missing {input_file}")
        return

    status_counts = Counter()
    action_counts = Counter()
    total_records = 0

    with input_file.open("r", encoding="utf-8") as infile, output_file.open(
        "w", encoding="utf-8"
    ) as outfile:
        for line in infile:
            line = line.strip()
            if not line:
                continue

            record = json.loads(line)

            policy_decision = record.get("policy_decision", {})
            dialogue_state = record.get("dialogue_state", {})

            tool_result = run_tool(
                policy_decision=policy_decision,
                dialogue_state=dialogue_state,
            )

            record["tool_result"] = tool_result

            action = policy_decision.get("next_action", "missing")
            status = tool_result.get("status", "missing")

            action_counts[action] += 1
            status_counts[status] += 1
            total_records += 1

            outfile.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"\nFinished {split}")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print(f"Total records: {total_records}")
    print(f"Action counts: {dict(action_counts)}")
    print(f"Tool status counts: {dict(status_counts)}")


def main():
    for split in SPLITS:
        apply_tools_for_split(split)


if __name__ == "__main__":
    main()