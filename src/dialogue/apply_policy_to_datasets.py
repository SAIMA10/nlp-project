import json
from pathlib import Path

from policy import decide_next_action


SPLITS = ["train", "dev", "test"]


def apply_policy_for_split(split):
    input_file = Path(f"data/processed/{split}_with_states.jsonl")
    output_file = Path(f"data/processed/{split}_with_policy.jsonl")

    if not input_file.exists():
        print(f"Skipping {split}: missing {input_file}")
        return

    total_records = 0
    records_with_policy = 0

    with input_file.open("r", encoding="utf-8") as infile, output_file.open(
        "w", encoding="utf-8"
    ) as outfile:
        for line in infile:
            line = line.strip()
            if not line:
                continue

            record = json.loads(line)

            dialogue_state = record.get("dialogue_state", {})
            intent = record.get("intent", "unknown")

            policy_decision = decide_next_action(
                dialogue_state=dialogue_state,
                intent=intent,
            )

            record["policy_decision"] = policy_decision

            if policy_decision.get("next_action") != "fallback":
                records_with_policy += 1

            outfile.write(json.dumps(record, ensure_ascii=False) + "\n")
            total_records += 1

    print(f"\nFinished {split}")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print(f"Total records: {total_records}")
    print(f"Records with non-fallback policy: {records_with_policy}")


def main():
    for split in SPLITS:
        apply_policy_for_split(split)


if __name__ == "__main__":
    main()