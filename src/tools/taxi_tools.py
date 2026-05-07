from tools.utils import generate_reference


def book_taxi(departure=None, destination=None, leave_at=None, arrive_by=None):
    missing = []

    if not departure:
        missing.append("departure")

    if not destination:
        missing.append("destination")

    if not leave_at and not arrive_by:
        missing.append("leave_at_or_arrive_by")

    if missing:
        return {
            "status": "error",
            "error": "missing_required_slots",
            "missing_slots": missing
        }

    return {
        "status": "success",
        "booking_reference": generate_reference("TXI"),
        "booking": {
            "departure": departure,
            "destination": destination,
            "leave_at": leave_at,
            "arrive_by": arrive_by
        },
        "taxi": {
            "car_type": "toyota prius",
            "phone": "01223 555555"
        }
    }