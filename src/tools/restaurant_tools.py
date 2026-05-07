from utils import RAW_DB_DIR, load_json, values_match, generate_reference


RESTAURANT_DB_PATH = RAW_DB_DIR / "restaurants.json"


def load_restaurants():
    return load_json(RESTAURANT_DB_PATH)


def search_restaurants(area=None, food=None, price_range=None, name=None):
    restaurants = load_restaurants()
    results = []

    for restaurant in restaurants:
        if not values_match(restaurant.get("area"), area):
            continue
        if not values_match(restaurant.get("food"), food):
            continue
        if not values_match(restaurant.get("pricerange"), price_range):
            continue
        if not values_match(restaurant.get("name"), name):
            continue

        results.append(restaurant)

    return {
        "status": "success",
        "count": len(results),
        "results": results[:5]
    }


def book_restaurant(name=None, people=None, day=None, time=None):
    missing = []

    for slot, value in {
        "name": name,
        "people": people,
        "day": day,
        "time": time,
    }.items():
        if value in [None, ""]:
            missing.append(slot)

    if missing:
        return {
            "status": "error",
            "error": "missing_required_slots",
            "missing_slots": missing
        }

    return {
        "status": "success",
        "booking_reference": generate_reference("RST"),
        "booking": {
            "name": name,
            "people": people,
            "day": day,
            "time": time
        }
    }