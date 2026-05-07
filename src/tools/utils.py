import json
import random
import string
from pathlib import Path


RAW_DB_DIR = Path("data/mock_db")


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize_db_value(value):
    if value is None:
        return None

    value = str(value).strip().lower()

    if value in {"", "?", "none", "not mentioned"}:
        return None

    return value


def values_match(db_value, query_value):
    db_value = normalize_db_value(db_value)
    query_value = normalize_db_value(query_value)

    if query_value is None:
        return True

    if db_value is None:
        return False

    return db_value == query_value


def generate_reference(prefix):
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{suffix}"