SLOT_NAME_MAPPING = {
    "pricerange": "price_range",
    "leaveat": "leave_at",
    "arriveby": "arrive_by",
    "bookpeople": "people",
    "bookday": "day",
    "bookstay": "stay",
    "booktime": "time",

    "area": "area",
    "stars": "stars",
    "type": "type",
    "parking": "parking",
    "internet": "internet",
    "name": "name",
    "food": "food",
    "departure": "departure",
    "destination": "destination",
}

BOOKING_SLOTS = {"people", "day", "stay", "time"}

VALUE_MAPPING = {
    "dontcare": "any",
    "don't care": "any",
    "do n't care": "any",
    "not mentioned": None,
    "none": None,
    "": None,
    "?": None,
    "free": "yes",
    "noon": "12:00",
    "at noon": "12:00",
    "1200hrs": "12:00",
}


def normalize_value(value):
    """
    Handles:
    - string values
    - list values like ["golden wok", "Golden Wok"]
    - empty / unknown values
    """
    if isinstance(value, list):
        value = value[0] if value else None

    if value is None:
        return None

    value = str(value).strip().lower()
    return VALUE_MAPPING.get(value, value)


def normalize_slot_name(raw_slot, default_domain=None):
    """
    Supports both:

    1. Domain-prefixed slots:
       restaurant-pricerange -> restaurant, price_range
       hotel-bookstay -> hotel, stay

    2. Non-prefixed slots:
       pricerange -> default_domain, price_range
       bookpeople -> default_domain, people
    """
    raw_slot = raw_slot.strip().lower()

    if "-" in raw_slot:
        domain, slot = raw_slot.split("-", 1)
    else:
        domain = default_domain
        slot = raw_slot

    slot = SLOT_NAME_MAPPING.get(slot, slot)

    return domain, slot


def get_slot_section(domain, slot):
    """
    Search slots are used to find entities.
    Booking slots are used to make reservations.
    Taxi is treated as booking-only.
    """
    if domain == "taxi":
        return "booking_slots"

    if slot in BOOKING_SLOTS:
        return "booking_slots"

    return "search_slots"


def normalize_slot_value_pairs(raw_slot_values, default_domain=None):
    """
    Input examples:

    From dev:
    {
      "hotel-pricerange": ["cheap"],
      "hotel-bookstay": ["3"]
    }

    From test:
    {
      "pricerange": "cheap",
      "bookstay": "3"
    }

    Output:
    {
      "hotel": {
        "search_slots": {
          "price_range": "cheap"
        },
        "booking_slots": {
          "stay": "3"
        }
      }
    }
    """
    normalized = {}

    if not isinstance(raw_slot_values, dict):
        return normalized

    for raw_slot, raw_value in raw_slot_values.items():
        domain, slot = normalize_slot_name(raw_slot, default_domain=default_domain)
        value = normalize_value(raw_value)

        if domain is None or value is None:
            continue

        if domain not in normalized:
            normalized[domain] = {
                "search_slots": {},
                "booking_slots": {}
            }

        section = get_slot_section(domain, slot)
        normalized[domain][section][slot] = value

    return normalized