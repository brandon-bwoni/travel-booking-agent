from langchain_core.tools import tool
from database.database import session, Booking
from datetime import datetime
from typing import Optional

@tool
def lookup_booking(booking_id: str) -> str:
    """
    Look up booking details by booking ID.
    
    Args:
        booking_id: The booking ID to search for (will be converted to integer)
        
    Returns:
        str: Detailed booking information including hotel, dates, price, and payment status
    """
    try:
        # Convert booking_id to integer
        bid = int(booking_id.strip())
        
        # Query the database for the booking
        booking = session.query(Booking).filter_by(booking_id=bid).first()
        
        if booking:
            # Format the booking details
            payment_status = "✅ Paid" if booking.is_paid else "❌ Unpaid"
            
            booking_details = f"""
📋 **Booking Details** (ID: {booking.booking_id})
🏨 **Hotel:** {booking.hotel_name}
📍 **Location:** {booking.hotel_city}, {booking.hotel_country}
📅 **Created:** {booking.created_date.strftime('%Y-%m-%d') if booking.created_date else 'N/A'}
🔗 **Check-in:** {booking.checkin_date.strftime('%Y-%m-%d') if booking.checkin_date else 'N/A'}
🔚 **Check-out:** {booking.checkout_date.strftime('%Y-%m-%d') if booking.checkout_date else 'N/A'}
💰 **Price:** €{booking.booking_price:.2f}
💳 **Payment:** {payment_status}
            """.strip()
            
            return booking_details
        else:
            return f"❌ No booking found for ID {bid}. Please check the booking ID and try again."
            
    except ValueError:
        return "❌ Invalid booking ID format. Booking ID must be a number."
    except Exception as e:
        return f"❌ Error looking up booking: {str(e)}"

@tool
def create_booking(hotel_name: str, hotel_city: str, hotel_country: str, 
                  checkin_date: str, checkout_date: str, booking_price: float) -> str:
    """
    Create a new hotel booking.
    
    Args:
        hotel_name: Name of the hotel
        hotel_city: City where the hotel is located
        hotel_country: Country where the hotel is located
        checkin_date: Check-in date (format: YYYY-MM-DD)
        checkout_date: Check-out date (format: YYYY-MM-DD)
        booking_price: Total booking price in euros
        
    Returns:
        str: Confirmation message with booking ID and details
    """
    try:
        # Parse dates
        checkin = datetime.strptime(checkin_date, '%Y-%m-%d').date()
        checkout = datetime.strptime(checkout_date, '%Y-%m-%d').date()
        
        # Validate dates
        if checkin >= checkout:
            return "❌ Check-in date must be before check-out date."
        
        if checkin < datetime.now().date():
            return "❌ Check-in date cannot be in the past."
        
        # Create new booking
        new_booking = Booking(
            hotel_name=hotel_name,
            hotel_city=hotel_city,
            hotel_country=hotel_country,
            checkin_date=checkin,
            checkout_date=checkout,
            booking_price=float(booking_price),
            created_date=datetime.now().date(),
            is_paid=False
        )
        
        # Add to database
        session.add(new_booking)
        session.commit()
        
        booking_confirmation = f"""
✅ **Booking Created Successfully!**
📋 **Booking ID:** {new_booking.booking_id}
🏨 **Hotel:** {hotel_name}
📍 **Location:** {hotel_city}, {hotel_country}
🔗 **Check-in:** {checkin_date}
🔚 **Check-out:** {checkout_date}
💰 **Total Price:** €{booking_price:.2f}
💳 **Payment Status:** Pending

Your booking has been created. Please proceed with payment to confirm your reservation.
        """.strip()
        
        return booking_confirmation
        
    except ValueError as e:
        return f"❌ Invalid date format. Please use YYYY-MM-DD format. Error: {str(e)}"
    except Exception as e:
        session.rollback()
        return f"❌ Error creating booking: {str(e)}"

@tool
def update_payment_status(booking_id: str, is_paid: bool) -> str:
    """
    Update the payment status of a booking.
    
    Args:
        booking_id: The booking ID to update
        is_paid: True if payment is completed, False otherwise
        
    Returns:
        str: Confirmation message of payment status update
    """
    try:
        bid = int(booking_id.strip())
        
        booking = session.query(Booking).filter_by(booking_id=bid).first()
        
        if booking:
            booking.is_paid = is_paid
            session.commit()
            
            status = "✅ Paid" if is_paid else "❌ Unpaid"
            return f"✅ Payment status updated for Booking {bid}: {status}"
        else:
            return f"❌ No booking found for ID {bid}."
            
    except ValueError:
        return "❌ Invalid booking ID format. Booking ID must be a number."
    except Exception as e:
        session.rollback()
        return f"❌ Error updating payment status: {str(e)}"

@tool
def list_user_bookings(limit: int = 10) -> str:
    """
    List recent bookings (useful for admin or user overview).
    
    Args:
        limit: Maximum number of bookings to return (default: 10)
        
    Returns:
        str: List of recent bookings with basic details
    """
    try:
        bookings = session.query(Booking).order_by(Booking.created_date.desc()).limit(limit).all()
        
        if not bookings:
            return "📋 No bookings found."
        
        booking_list = "📋 **Recent Bookings:**\n\n"
        
        for booking in bookings:
            payment_status = "✅" if booking.is_paid else "❌"
            booking_list += f"{payment_status} **ID {booking.booking_id}:** {booking.hotel_name} ({booking.hotel_city}) - €{booking.booking_price:.2f}\n"
        
        return booking_list
        
    except Exception as e:
        return f"❌ Error retrieving bookings: {str(e)}"

# Export tools for use in LangGraph
booking_lookup_tool = lookup_booking
booking_create_tool = create_booking
payment_update_tool = update_payment_status
booking_list_tool = list_user_bookings