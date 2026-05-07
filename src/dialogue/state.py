def create_empty_state():
    return {
        "dialogue_id": None,
        "active_domain": None,
        "domains": {}
    }


def create_empty_domain_state():
    return {
        "search_slots": {},
        "booking_slots": {},
        "last_action": None,
        "last_results": [],
        "booking_reference": None
    }