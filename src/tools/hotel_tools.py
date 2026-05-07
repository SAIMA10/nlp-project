from utils import RAW_DB_DIR, load_json, values_match, generate_reference


HOTEL_DB_PATH = RAW_DB_DIR / "hotels.json"


def load_hotels():
    return load_json(HOTEL_DB_PATH)


def search_hotels(area=None, price_range=None, stars=None, parking=None, internet=None, type=None, name=None):
    hotels = load_hotels()
    results = []

    for hotel in hotels:
        if not values_match(hotel.get("area"), area):
            continue
        if not values_match(hotel.get("pricerange"), price_range):
            continue
        if not values_match(hotel.get("stars"), stars):
            continue
        if not values_match(hotel.get("parking"), parking):
            continue
        if not values_match(hotel.get("internet"), internet):
            continue
        if not values_match(hotel.get("type"), type):
            continue
        if not values_match(hotel.get("name"), name):
            continue

        results.append(hotel)

    return {
        "status": "success",
        "count": len(results),
        "results": results[:5]
    }


def book_hotel(name=None, people=None, day=None, stay=None):
    missing = []

    for slot, value in {
        "name": name,
        "people": people,
        "day": day,
        "stay": stay,
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
        "booking_reference": generate_reference("HTL"),
        "booking": {
            "name": name,
            "people": people,
            "day": day,
            "stay": stay
        }
    }