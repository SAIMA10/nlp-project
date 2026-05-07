def define_intent(domain, normalized_domain_slots):
    search_slots = normalized_domain_slots.get("search_slots", {})
    booking_slots = normalized_domain_slots.get("booking_slots", {})

    has_search_slots = bool(search_slots)
    has_booking_slots = bool(booking_slots)

    if domain == "hotel":
        if has_booking_slots:
            return "book_hotel"
        if has_search_slots:
            return "search_hotel"

    if domain == "restaurant":
        if has_booking_slots:
            return "book_restaurant"
        if has_search_slots:
            return "search_restaurant"

    if domain == "taxi":
        if has_booking_slots or has_search_slots:
            return "book_taxi"

    if domain == "attraction":
        if has_search_slots:
            return "search_attraction"

    return "unknown"


def define_intents_for_record(normalized_slots):
    intents = {}

    for domain, domain_slots in normalized_slots.items():
        intents[domain] = define_intent(domain, domain_slots)

    return intents