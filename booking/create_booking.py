from database.database import session
from database.database import Booking

def booking_fn(booking_id):
    try:
        bid = int(booking_id.strip())
        b = session.query(Booking).filter_by(booking_id=bid).first()
        if b:
            return f"Booking {b.booking_id}: {b.hotel_name} in {b.hotel_city}, {b.hotel_country}\nCreated: {b.created_date}\nCheck-in: {b.checkin_date}\nCheck-out: {b.checkout_date}\nPrice: €{b.booking_price:.2f}\nPaid: {'Yes' if b.is_paid else 'No'}"
        return f"No booking found for ID {bid}."
    except ValueError:
        return "Booking ID must be an integer."