def format_missing_slot(slot):
    labels = {
        "people": "how many people",
        "day": "which day",
        "stay": "how many nights",
        "time": "what time",
        "departure": "where you are leaving from",
        "destination": "where you are going",
        "leave_at_or_arrive_by": "what time you want to leave or arrive by",
        "area_or_type": "what area or type of attraction you prefer",
    }

    return labels.get(slot, slot.replace("_", " "))


def generate_response(policy_decision, tool_result):
    action = policy_decision.get("next_action")
    missing_slots = policy_decision.get("missing_slots", [])
    domain = policy_decision.get("domain")

    if action == "fallback":
        return "Sorry, I could not understand that. Are you looking for a hotel, restaurant, taxi, or attraction?"

    if action == "ask_missing_slot":
        if not missing_slots:
            return "Could you provide a bit more information?"

        missing_text = format_missing_slot(missing_slots[0])
        return f"Could you tell me {missing_text}?"

    if tool_result.get("status") == "success":
        if action.startswith("search_"):
            count = tool_result.get("count", 0)
            results = tool_result.get("results", [])

            if count == 0:
                return f"I could not find any matching {domain} options. Could you try different preferences?"

            first_name = results[0].get("name", "one option")
            return f"I found {count} matching {domain} option(s). One option is {first_name}."

        if action.startswith("book_"):
            reference = tool_result.get("booking_reference")
            return f"Your {domain} booking is confirmed. Reference number: {reference}."

    if tool_result.get("status") == "skipped":
        return "I need a little more information before I can continue."

    if tool_result.get("status") == "error":
        missing = tool_result.get("missing_slots", [])
        if missing:
            return f"I am missing this information: {', '.join(missing)}."
        return "Something went wrong while using the booking tool."

    return "Okay."