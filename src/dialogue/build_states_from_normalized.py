import json
from pathlib import Path

from state import create_empty_state
from state_tracker import update_state

"do it for train and test individually"

INPUT_FILE = Path("data/processed/train_normalized.jsonl")
OUTPUT_FILE = Path("data/processed/train_with_states.jsonl")


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    current_dialogue_id = None
    state = create_empty_state()

    total_records = 0

    with INPUT_FILE.open("r", encoding="utf-8") as infile, OUTPUT_FILE.open(
        "w", encoding="utf-8"
    ) as outfile:
        for line in infile:
            record = json.loads(line)

            dialogue_id = record.get("dialogue_id")

            if dialogue_id != current_dialogue_id:
                current_dialogue_id = dialogue_id
                state = create_empty_state()

            state = update_state(
                current_state=state,
                normalized_slots=record.get("normalized_slots", {}),
                dialogue_id=dialogue_id
            )

            record["dialogue_state"] = state

            outfile.write(json.dumps(record, ensure_ascii=False) + "\n")
            total_records += 1

    print("Done.")
    print(f"Input: {INPUT_FILE}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Records processed: {total_records}")


if __name__ == "__main__":
    main()