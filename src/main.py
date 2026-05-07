import json
from pathlib import Path
from preprocessing.normalize_slots import normalize_slot_value_pairs
from preprocessing.define_intent import define_intents_for_record


DATASETS = {
    "train": {
        "input": Path("data/processed/train.jsonl"),
        "output": Path("data/processed/train_normalized.jsonl"),
    },
    "dev": {
        "input": Path("data/processed/dev.jsonl"),
        "output": Path("data/processed/dev_normalized.jsonl"),
    },
    "test": {
        "input": Path("data/processed/test.jsonl"),
        "output": Path("data/processed/test_normalized.jsonl"),
    },
}


def load_records(input_file):
    """
    Supports both:
    1. JSONL: one JSON object per line
    2. JSON: a list of objects
    """
    text = input_file.read_text(encoding="utf-8").strip()

    if not text:
        return []

    if text.startswith("["):
        return json.loads(text)

    records = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        line = line.strip()

        if not line:
            continue

        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON on line {line_number} in {input_file}: {e}")

    return records


def normalize_and_define_intents(input_file, output_file, split_name):
    output_file.parent.mkdir(parents=True, exist_ok=True)

    records = load_records(input_file)

    total_records = 0
    normalized_records = 0
    intent_records = 0

    with output_file.open("w", encoding="utf-8") as outfile:
        for record in records:
            raw_slot_values = record.get("slots", {})
            default_domain = record.get("domain")

            normalized_slots = normalize_slot_value_pairs(
                raw_slot_values,
                default_domain=default_domain,
            )

            intents = define_intents_for_record(normalized_slots)

            record["split"] = split_name
            record["raw_slot_values"] = raw_slot_values
            record["normalized_slots"] = normalized_slots
            record["intents"] = intents

            if len(intents) == 1:
                record["intent"] = next(iter(intents.values()))
            elif len(intents) > 1:
                record["intent"] = "multi_domain"
            else:
                record["intent"] = "unknown"

            if normalized_slots:
                normalized_records += 1

            if intents:
                intent_records += 1

            outfile.write(json.dumps(record, ensure_ascii=False) + "\n")
            total_records += 1

    print(f"\nFinished {split_name}")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Total records processed: {total_records}")
    print(f"Records with normalized slots: {normalized_records}")
    print(f"Records with intents: {intent_records}")


def process_all_datasets():
    for split_name, paths in DATASETS.items():
        input_file = paths["input"]
        output_file = paths["output"]

        if not input_file.exists():
            print(f"\nSkipping {split_name}: input file not found: {input_file}")
            continue

        normalize_and_define_intents(
            input_file=input_file,
            output_file=output_file,
            split_name=split_name,
        )


if __name__ == "__main__":
    process_all_datasets()