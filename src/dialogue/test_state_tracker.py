from state import create_empty_state
from state_tracker import update_state


def main():
    state = create_empty_state()

    turn_1_slots = {
        "hotel": {
            "search_slots": {
                "area": "north",
                "price_range": "cheap"
            },
            "booking_slots": {}
        }
    }

    state = update_state(state, turn_1_slots, dialogue_id="demo_001")
    print("After turn 1:")
    print(state)

    turn_2_slots = {
        "hotel": {
            "search_slots": {},
            "booking_slots": {
                "people": "2",
                "day": "friday",
                "stay": "3"
            }
        }
    }

    state = update_state(state, turn_2_slots, dialogue_id="demo_001")
    print("\nAfter turn 2:")
    print(state)


if __name__ == "__main__":
    main()