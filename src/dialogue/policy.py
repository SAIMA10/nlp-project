REQUIRED_BOOKING_SLOTS = {
    "hotel": ["people", "day", "stay"],
    "restaurant": ["people", "day", "time"],
    "taxi": ["departure", "destination"],
    "attraction": [],
}

SEARCH_ACTIONS = {
    "hotel": "search_hotel",
    "restaurant": "search_restaurant",
    "attraction": "search_attraction",
}

BOOK_ACTIONS = {
    "hotel": "book_hotel",
    "restaurant": "book_restaurant",
    "taxi": "book_taxi",
}


def get_domain_from_intent(intent):
    if not intent or intent == "unknown":
        return None

    parts = intent.split("_")

    if len(parts) < 2:
        return None

    return parts[-1]


def is_booking_intent(intent):
    return intent in {
        "book_hotel",
        "book_restaurant",
        "book_taxi",
    }


def is_search_intent(intent):
    return intent in {
        "search_hotel",
        "search_restaurant",
        "search_attraction",
    }


def get_domain_state(dialogue_state, domain):
    return (
        dialogue_state
        .get("domains", {})
        .get(domain, {
            "search_slots": {},
            "booking_slots": {}
        })
    )


def get_missing_booking_slots(domain_state, domain):
    booking_slots = domain_state.get("booking_slots", {})
    required_slots = REQUIRED_BOOKING_SLOTS.get(domain, [])

    missing_slots = []

    for slot in required_slots:
        if slot not in booking_slots or booking_slots.get(slot) in [None, ""]:
            missing_slots.append(slot)

    if domain == "taxi":
        has_leave_at = bool(booking_slots.get("leave_at"))
        has_arrive_by = bool(booking_slots.get("arrive_by"))

        if not has_leave_at and not has_arrive_by:
            missing_slots.append("leave_at_or_arrive_by")

    return missing_slots


def decide_next_action(dialogue_state, intent):
    """
    Decide what the chatbot should do next based on current state and intent.
    """

    domain = get_domain_from_intent(intent)

    if domain is None:
        return {
            "next_action": "fallback",
            "missing_slots": [],
            "domain": None
        }

    domain_state = get_domain_state(dialogue_state, domain)

    if is_booking_intent(intent):
        missing_slots = get_missing_booking_slots(domain_state, domain)

        if missing_slots:
            return {
                "next_action": "ask_missing_slot",
                "missing_slots": missing_slots,
                "domain": domain
            }

        return {
            "next_action": BOOK_ACTIONS[domain],
            "missing_slots": [],
            "domain": domain
        }

    if is_search_intent(intent):
        return {
            "next_action": SEARCH_ACTIONS[domain],
            "missing_slots": [],
            "domain": domain
        }

    return {
        "next_action": "fallback",
        "missing_slots": [],
        "domain": domain
    }