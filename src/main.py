import json
from pathlib import Path

from preprocessing.normalize_slots import normalize_slot_value_pairs


INPUT_FILE = Path("data/processed/train.jsonl")
OUTPUT_FILE = Path("data/processed/train_normalized.jsonl")


def extract_raw_slot_values_from_turn(turn):
    raw_slot_values = {}

    for frame in turn.get("frames", []):
        state = frame.get("state", {})
        slot_values = state.get("slot_values", {})

        if isinstance(slot_values, dict):
            raw_slot_values.update(slot_values)

    return raw_slot_values


def load_records(input_file):
    """
    Supports both:
    1. JSONL: one JSON object per line
    2. JSON: a list of objects
    """
    text = input_file.read_text(encoding="utf-8").strip()

    if not text:
        return []

    # Case 1: normal JSON array
    if text.startswith("["):
        return json.loads(text)

    # Case 2: JSONL
    records = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue

        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON on line {line_number}: {e}")

    return records


def normalize_dev_file(input_file=INPUT_FILE, output_file=OUTPUT_FILE):
    output_file.parent.mkdir(parents=True, exist_ok=True)

    records = load_records(input_file)

    total_records = 0
    normalized_records = 0

    with output_file.open("w", encoding="utf-8") as outfile:
        for record in records:
            # raw_slot_values = extract_raw_slot_values_from_turn(record)
            # normalized_slots = normalize_slot_value_pairs(raw_slot_values)
            raw_slot_values = record.get("slots", {})
            default_domain = record.get("domain")
            normalized_slots = normalize_slot_value_pairs(
                raw_slot_values,
                default_domain=default_domain
            )

            record["raw_slot_values"] = raw_slot_values
            record["normalized_slots"] = normalized_slots

            if normalized_slots:
                normalized_records += 1

            outfile.write(json.dumps(record, ensure_ascii=False) + "\n")
            total_records += 1

    print("Done.")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Total records processed: {total_records}")
    print(f"Records with normalized slots: {normalized_records}")


if __name__ == "__main__":
    normalize_dev_file()