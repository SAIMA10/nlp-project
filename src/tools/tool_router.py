from hotel_tools import search_hotels, book_hotel
from restaurant_tools import search_restaurants, book_restaurant
from attraction_tools import search_attractions
from taxi_tools import book_taxi


TOOL_ALLOWED_ARGS = {
    "search_hotel": {"area", "price_range", "stars", "parking", "internet", "type", "name"},
    "book_hotel": {"name", "people", "day", "stay"},

    "search_restaurant": {"area", "food", "price_range", "name"},
    "book_restaurant": {"name", "people", "day", "time"},

    "search_attraction": {"area", "type", "name"},

    "book_taxi": {"departure", "destination", "leave_at", "arrive_by"},
}


def filter_args(action, slots):
    allowed_args = TOOL_ALLOWED_ARGS.get(action, set())
    return {
        key: value
        for key, value in slots.items()
        if key in allowed_args
    }


def get_domain_slots(dialogue_state, domain):
    return (
        dialogue_state
        .get("domains", {})
        .get(domain, {
            "search_slots": {},
            "booking_slots": {}
        })
    )


def get_first_result_name(tool_result):
    results = tool_result.get("results", [])

    if not results:
        return None

    return results[0].get("name")


def run_tool(policy_decision, dialogue_state):
    action = policy_decision.get("next_action")
    domain = policy_decision.get("domain")

    if action in {"fallback", "ask_missing_slot"}:
        return {
            "status": "skipped",
            "reason": action
        }

    domain_slots = get_domain_slots(dialogue_state, domain)
    search_slots = domain_slots.get("search_slots", {})
    booking_slots = domain_slots.get("booking_slots", {})

    if action == "search_hotel":
        args = filter_args(action, search_slots)
        return search_hotels(**args)

    if action == "book_hotel":
        search_args = filter_args("search_hotel", search_slots)
        hotel_name = search_slots.get("name")

        if not hotel_name:
            search_result = search_hotels(**search_args)
            hotel_name = get_first_result_name(search_result)

        booking_args = filter_args("book_hotel", booking_slots)
        booking_args["name"] = hotel_name

        return book_hotel(**booking_args)

    if action == "search_restaurant":
        args = filter_args(action, search_slots)
        return search_restaurants(**args)

    if action == "book_restaurant":
        search_args = filter_args("search_restaurant", search_slots)
        restaurant_name = search_slots.get("name")

        if not restaurant_name:
            search_result = search_restaurants(**search_args)
            restaurant_name = get_first_result_name(search_result)

        booking_args = filter_args("book_restaurant", booking_slots)
        booking_args["name"] = restaurant_name

        return book_restaurant(**booking_args)

    if action == "search_attraction":
        args = filter_args(action, search_slots)
        return search_attractions(**args)

    if action == "book_taxi":
        args = filter_args(action, booking_slots)
        return book_taxi(**args)

    return {
        "status": "error",
        "error": "unknown_action",
        "action": action
    }