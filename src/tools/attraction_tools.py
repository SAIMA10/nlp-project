from tools.utils import RAW_DB_DIR, load_json, values_match


ATTRACTION_DB_PATH = RAW_DB_DIR / "attractions.json"


def load_attractions():
    return load_json(ATTRACTION_DB_PATH)


def search_attractions(area=None, type=None, name=None):
    attractions = load_attractions()
    results = []

    for attraction in attractions:
        if not values_match(attraction.get("area"), area):
            continue
        if not values_match(attraction.get("type"), type):
            continue
        if not values_match(attraction.get("name"), name):
            continue

        results.append(attraction)

    return {
        "status": "success",
        "count": len(results),
        "results": results[:5]
    }