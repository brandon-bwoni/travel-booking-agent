from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import date

Base = declarative_base()

class Booking(Base):
    __tablename__ = 'bookings'
    booking_id = Column(Integer, primary_key=True)
    created_date = Column(Date)
    checkin_date = Column(Date)
    checkout_date = Column(Date)
    hotel_name = Column(String)
    hotel_city = Column(String)
    hotel_country = Column(String)
    booking_price = Column(Float)
    is_paid = Column(Boolean)

engine = create_engine("sqlite:///bookings.db", connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()

# Initialize bookings
bookings = [
    (1, date(2025, 4, 1), date(2025, 6, 1), date(2025, 6, 5), "Memmo Alfama", "Lisbon", "Portugal", 250.0, True),
    (2, date(2025, 4, 2), date(2025, 7, 10), date(2025, 7, 15), "The Lumiares Hotel & Spa", "Lisbon", "Portugal", 300.0, False),
    (3, date(2025, 4, 3), date(2025, 8, 20), date(2025, 8, 25), "Valverde Hotel", "Lisbon", "Portugal", 280.0, True),
    (4, date(2025, 4, 4), date(2025, 9, 5), date(2025, 9, 10), "Santiago de Alfama", "Lisbon", "Portugal", 260.0, False),
    (5, date(2025, 4, 5), date(2025, 10, 1), date(2025, 10, 3), "LUSTER Hotel", "Lisbon", "Portugal", 220.0, True),
]

if not session.query(Booking).first():
    session.add_all([Booking(booking_id=b[0], created_date=b[1], checkin_date=b[2], checkout_date=b[3], hotel_name=b[4], hotel_city=b[5], hotel_country=b[6], booking_price=b[7], is_paid=b[8]) for b in bookings])
    session.commit()