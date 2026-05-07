import re

from preprocessing.normalize_slots import normalize_slot_value_pairs
from preprocessing.define_intent import define_intents_for_record

AREAS = {"north", "south", "east", "west", "centre", "center"}
PRICE_RANGES = {"cheap", "moderate", "expensive"}
DAYS = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}


def normalize_area(value):
    if value == "center":
        return "centre"
    return value


def detect_domain(message, current_domain=None):
    text = message.lower().strip()

    # If we are already booking a taxi, follow-up route/time messages
    # should stay in taxi even if they mention hotel/restaurant.
    if current_domain == "taxi":
        taxi_followup_keywords = [
            "to ",
            "from ",
            "by ",
            "at ",
            "leave",
            "leaving",
            "arrive",
            "arriving",
        ]

        if any(keyword in text for keyword in taxi_followup_keywords):
            return "taxi"

    # Check taxi first because taxi messages often mention hotel/restaurant.
    if any(word in text for word in ["taxi", "cab"]):
        return "taxi"

    if any(word in text for word in ["hotel", "guesthouse", "guest house"]):
        return "hotel"

    if any(word in text for word in ["restaurant", "food", "table", "dinner", "lunch"]):
        return "restaurant"

    if any(word in text for word in ["attraction", "museum", "park", "theatre", "college", "entertainment"]):
        return "attraction"

    return current_domain

def extract_slots(message, domain):
    text = message.lower()
    slots = {}

    for area in AREAS:
        if re.search(rf"\b{area}\b", text):
            slots["area"] = normalize_area(area)

    for price in PRICE_RANGES:
        if re.search(rf"\b{price}\b", text):
            slots["pricerange"] = price

    for day in DAYS:
        if re.search(rf"\b{day}\b", text):
            slots["bookday"] = day

    people_match = re.search(r"\b(\d+)\s*(people|persons|guests)\b", text)
    if people_match:
        slots["bookpeople"] = people_match.group(1)

    stay_match = re.search(r"\b(\d+)\s*(night|nights)\b", text)
    if stay_match:
        slots["bookstay"] = stay_match.group(1)

    time_match = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", text)

    if time_match and any(word in text for word in ["at", "by", "arrive", "leave", "leaving"]):
        hour = int(time_match.group(1))
        minute = time_match.group(2) or "00"
        meridiem = time_match.group(3)

        if meridiem == "pm" and hour != 12:
            hour += 12
        if meridiem == "am" and hour == 12:
            hour = 0

        normalized_time = f"{hour:02d}:{minute}"

        if domain == "taxi":
            if "by" in text or "arrive" in text:
                slots["arriveby"] = normalized_time
            else:
                slots["leaveat"] = normalized_time
        else:
            slots["booktime"] = normalized_time

    if domain == "taxi":
        route_match = re.search(
            r"from (.+?) to (.+?)(?: by| at| leaving| leave|\.|$)",
            text
        )

        if route_match:
            slots["departure"] = route_match.group(1).strip()
            slots["destination"] = route_match.group(2).strip()
        else:
            to_match = re.search(r"to (.+?)(?: by| at| leaving| leave|\.|$)", text)
            if to_match:
                slots["destination"] = to_match.group(1).strip()

            from_match = re.search(r"from (.+?)(?: to| by| at| leaving| leave|\.|$)", text)
            if from_match:
                slots["departure"] = from_match.group(1).strip()

    if domain == "hotel":
        if "parking" in text or "free parking" in text:
            slots["parking"] = "yes"

        if "internet" in text or "wifi" in text or "wi-fi" in text:
            slots["internet"] = "yes"

        # Only set type if the user explicitly asks for guesthouse.
        # Do not set type="hotel" just because the word hotel appears.
        if "guesthouse" in text or "guest house" in text:
            slots["type"] = "guesthouse"

        stars_match = re.search(r"\b(\d)\s*(star|stars)\b", text)
        if stars_match:
            slots["stars"] = stars_match.group(1)

    if domain == "restaurant":
        cuisines = [
            "chinese",
            "italian",
            "indian",
            "british",
            "french",
            "thai",
            "japanese",
            "mediterranean",
            "european",
        ]
        for cuisine in cuisines:
            if cuisine in text:
                slots["food"] = cuisine

    if domain == "attraction":
        attraction_types = [
            "museum",
            "park",
            "theatre",
            "college",
            "cinema",
            "nightclub",
        ]
        for attraction_type in attraction_types:
            if attraction_type in text:
                slots["type"] = attraction_type


    return slots


def parse_user_message(message, current_domain=None):
    domain = detect_domain(message, current_domain=current_domain)

    if domain is None:
        return {"domain": None, "intent": "unknown", "normalized_slots": {}}

    raw_slots = extract_slots(message, domain)

    normalized_slots = normalize_slot_value_pairs(raw_slots, default_domain=domain)

    intents = define_intents_for_record(normalized_slots)

    if len(intents) == 1:
        intent = next(iter(intents.values()))
    elif len(intents) > 1:
        intent = "multi_domain"
    else:
        intent = "unknown"

    return {
        "domain": domain,
        "intent": intent,
        "raw_slots": raw_slots,
        "normalized_slots": normalized_slots,
    }
