from policy import decide_next_action


def main():
    hotel_missing_state = {
        "active_domain": "hotel",
        "domains": {
            "hotel": {
                "search_slots": {
                    "area": "north",
                    "price_range": "cheap"
                },
                "booking_slots": {
                    "people": "2",
                    "day": "friday"
                }
            }
        }
    }

    result = decide_next_action(
        dialogue_state=hotel_missing_state,
        intent="book_hotel"
    )

    print("Hotel missing slot result:")
    print(result)

    assert result["next_action"] == "ask_missing_slot"
    assert "stay" in result["missing_slots"]

    hotel_complete_state = {
        "active_domain": "hotel",
        "domains": {
            "hotel": {
                "search_slots": {
                    "area": "north",
                    "price_range": "cheap"
                },
                "booking_slots": {
                    "people": "2",
                    "day": "friday",
                    "stay": "3"
                }
            }
        }
    }

    result = decide_next_action(
        dialogue_state=hotel_complete_state,
        intent="book_hotel"
    )

    print("\nHotel complete booking result:")
    print(result)

    assert result["next_action"] == "book_hotel"
    assert result["missing_slots"] == []

    taxi_missing_state = {
        "active_domain": "taxi",
        "domains": {
            "taxi": {
                "search_slots": {},
                "booking_slots": {
                    "departure": "hotel",
                    "destination": "restaurant"
                }
            }
        }
    }

    result = decide_next_action(
        dialogue_state=taxi_missing_state,
        intent="book_taxi"
    )

    print("\nTaxi missing time result:")
    print(result)

    assert result["next_action"] == "ask_missing_slot"
    assert "leave_at_or_arrive_by" in result["missing_slots"]

    taxi_complete_state = {
        "active_domain": "taxi",
        "domains": {
            "taxi": {
                "search_slots": {},
                "booking_slots": {
                    "departure": "hotel",
                    "destination": "restaurant",
                    "arrive_by": "19:00"
                }
            }
        }
    }

    result = decide_next_action(
        dialogue_state=taxi_complete_state,
        intent="book_taxi"
    )

    print("\nTaxi complete booking result:")
    print(result)

    assert result["next_action"] == "book_taxi"
    assert result["missing_slots"] == []

    print("\nAll missing-slot policy tests passed.")


if __name__ == "__main__":
    main()