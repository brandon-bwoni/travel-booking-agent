from langchain.tools import Tool
from bookings.create_booking import booking_fn

booking_tool = Tool(
    name="booking", func=booking_fn, description="Lookup booking details by booking ID."
)