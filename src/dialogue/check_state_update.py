from state import create_empty_state
from state_tracker import update_state


def main():
    state = create_empty_state()

    # Turn 1: "I need a cheap hotel in the north."
    turn_1_slots = {
        "hotel": {
            "search_slots": {
                "price_range": "cheap",
                "area": "north"
            },
            "booking_slots": {}
        }
    }

    state = update_state(
        current_state=state,
        normalized_slots=turn_1_slots,
        dialogue_id="manual_test_001"
    )

    # Turn 2: "Actually make it expensive."
    turn_2_slots = {
        "hotel": {
            "search_slots": {
                "price_range": "expensive"
            },
            "booking_slots": {}
        }
    }

    state = update_state(
        current_state=state,
        normalized_slots=turn_2_slots,
        dialogue_id="manual_test_001"
    )

    hotel_search_slots = state["domains"]["hotel"]["search_slots"]

    print("Final hotel search slots:")
    print(hotel_search_slots)

    assert hotel_search_slots["area"] == "north"
    assert hotel_search_slots["price_range"] == "expensive"

    print("State tracker update test passed.")


if __name__ == "__main__":
    main()