from hotel_tools import search_hotels, book_hotel
from restaurant_tools import search_restaurants, book_restaurant
from attraction_tools import search_attractions
from taxi_tools import book_taxi
from tool_router import run_tool


def main():
    print("Hotel search:")
    print(search_hotels(area="north", price_range="cheap"))

    print("\nHotel booking:")
    print(book_hotel(name="test hotel", people="2", day="friday", stay="3"))

    print("\nRestaurant search:")
    print(search_restaurants(area="centre", food="italian"))

    print("\nRestaurant booking:")
    print(book_restaurant(name="test restaurant", people="4", day="saturday", time="19:00"))

    print("\nAttraction search:")
    print(search_attractions(area="centre", type="museum"))

    print("\nTaxi booking:")
    print(book_taxi(departure="hotel", destination="restaurant", arrive_by="19:00"))

    print("\nTool router test:")
    dialogue_state = {
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

    policy_decision = {
        "next_action": "book_hotel",
        "missing_slots": [],
        "domain": "hotel"
    }

    print(run_tool(policy_decision, dialogue_state))


if __name__ == "__main__":
    main()