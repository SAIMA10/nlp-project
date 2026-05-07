from state import create_empty_state, create_empty_domain_state


def ensure_domain_exists(state, domain):
    if domain not in state["domains"]:
        state["domains"][domain] = create_empty_domain_state()


def update_state(current_state, normalized_slots, dialogue_id=None):
    """
    Merge current turn's normalized slots into the running dialogue state.

    normalized_slots example:
    {
      "hotel": {
        "search_slots": {"area": "north", "price_range": "cheap"},
        "booking_slots": {"people": "2"}
      }
    }
    """
    if current_state is None:
        current_state = create_empty_state()

    if dialogue_id is not None:
        current_state["dialogue_id"] = dialogue_id

    if not normalized_slots:
        return current_state

    for domain, domain_slots in normalized_slots.items():
        ensure_domain_exists(current_state, domain)

        current_state["active_domain"] = domain

        search_slots = domain_slots.get("search_slots", {})
        booking_slots = domain_slots.get("booking_slots", {})

        current_state["domains"][domain]["search_slots"].update(search_slots)
        current_state["domains"][domain]["booking_slots"].update(booking_slots)

    return current_state


def reset_state():
    return create_empty_state()


def get_domain_state(state, domain=None):
    if domain is None:
        domain = state.get("active_domain")

    if domain is None:
        return None

    return state["domains"].get(domain)