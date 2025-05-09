from datetime import datetime, timedelta
from enum import Enum
from threading import Lock

# Enum classes for status
class PaymentStatus(Enum):
    PENDING = 'PENDING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'

class SeatStatus(Enum):
    AVAILABLE = 'AVAILABLE'
    RESERVED = 'RESERVED'

class SeatType(Enum):
    ECONOMY = 'ECONOMY'
    BUSINESS = 'BUSINESS'
    FIRST_CLASS = 'FIRST_CLASS'

class BookingStatus(Enum):
    PENDING = 'PENDING'
    CONFIRMED = 'CONFIRMED'
    CANCELLED = 'CANCELLED'

# Classes for Passenger, Seat, and Flight Management

class Passenger:
    def __init__(self, id, name, email, phone):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone


class Seat:
    def __init__(self, seat_no, seat_type):
        self.seat_no = seat_no
        self.seat_type = seat_type
        self.seat_status = SeatStatus.AVAILABLE

    def get_seat_no(self):
        return self.seat_no

    def reserve(self):
        self.seat_status = SeatStatus.RESERVED

    def release(self):
        self.seat_status = SeatStatus.AVAILABLE


class Aircraft:
    def __init__(self, id, model, capacity):
        self.id = id
        self.model = model
        self.capacity = capacity
        self.seats = []

    def get_seats(self):
        return self.seats


class Flight:
    def __init__(self, flight_no, src, dest, depart_time, arr_time, aircraft):
        self.flight_no = flight_no
        self.src = src
        self.dest = dest
        self.depart_time = depart_time
        self.arr_time = arr_time
        self.aircraft = aircraft
        self.crew = []

    def get_flight_no(self):
        return self.flight_no

    def get_src(self):
        return self.src

    def get_dest(self):
        return self.dest

    def get_depart_time(self):
        return self.depart_time

    def get_arr_time(self):
        return self.arr_time

    def get_aircraft(self):
        return self.aircraft

    def assign_crew(self, crew_list):
        self.crew.extend(crew_list)


class Booking:
    def __init__(self, booking_no, flight, passenger, seat):
        self.booking_no = booking_no
        self.passenger = passenger
        self.flight = flight
        self.seat = seat
        self.status = BookingStatus.PENDING

    def cancel(self):
        self.status = BookingStatus.CANCELLED

    def set_status(self, status):
        self.status = status


class PaymentService:
    _instance = None
    _lock = Lock()

    def __new__(self):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = cls()
        return cls._instance

    def make_payment(self, amount, payment_method, passenger):
        print(f"[Payment] Charging {amount} via {payment_method} for {passenger.name}")
        return PaymentStatus.COMPLETED


class BookingService:
    _lock = Lock()
    _instance = None

    def __init(self):
        bookings = {}

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super.__new__(cls)
        return cls._instance

    def book_seat(self, flight, passenger, seat_no, payment_method):
        with self._lock:
            seats = flight.get_aircraft().get_seats()
            for seat in seats:
                if seat.get_seat_no() == seat_no:
                    seat.reserve()
                    booking_id = f"{flight.get_flight_no()}_{seat.get_seat_no()}_{datetime.now()}"
                    booking = Booking(booking_id, flight, passenger, seat)
                    payment_status = PaymentService().make_payment(100, payment_method, passenger)
                    booking.set_status(payment_status)
                    self.bookings[booking_id] = booking
                    return booking

    def cancel(self, booking_no):
        with self._lock:
            booking = self.bookings.get(booking_no)
            if booking:
                booking.cancel()
                booking.seat.release()


# Testing the classes and functionality

# Creating seats
seat1 = Seat(seat_no="1A", seat_type=SeatType.ECONOMY)
seat2 = Seat(seat_no="1B", seat_type=SeatType.BUSINESS)

# Creating aircraft and adding seats
aircraft = Aircraft(id="A1", model="Boeing 737", capacity=2)
aircraft.seats = [seat1, seat2]

# Creating a flight
depart_time = datetime.now() + timedelta(days=1)
arrival_time = depart_time + timedelta(hours=2)
flight = Flight(flight_no="AI101", src="NYC", dest="LAX", depart_time=depart_time, arr_time=arrival_time, aircraft=aircraft)

# Creating a passenger
passenger = Passenger(id="P1", name="John Doe", email="john@example.com", phone="1234567890")

# Creating the airline system and adding flight and aircraft
booking_service = BookingService()

# Simulate booking a flight
payment_method = "Credit Card"
booking = booking_service.book_seat(flight, passenger, seat1.get_seat_no(), payment_method)

# Print booking details after booking
print(f"Booking No: {booking.booking_no}")
print(f"Booking Status: {booking.status.name}")
print(f"Seat Reserved: {booking.seat.get_seat_no()} ({booking.seat.seat_type.name})")

# Simulate cancelling the booking
booking_service.cancel(booking.booking_no)

# Print booking status after cancellation
print(f"Booking Status after cancellation: {booking.status.name}")
print(f"Seat status after cancellation: {booking.seat.seat_status.name}")
