from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from threading import Lock

# Enums
class SeatType(Enum):
    NORMAL = 1
    PREMIUM = 2

class SeatStatus(Enum):
    AVAILABLE = 1
    BOOKED = 2

class BookingStatus(Enum):
    PENDING = 1
    CONFIRMED = 2
    FAILED = 3
    CANCELLED = 4

class PaymentStatus(Enum):
    PENDING = 1
    CONFIRMED = 2
    FAILED = 3
    CANCELLED = 4

# Seat
class Seat:
    def __init__(self, seat_id, row, col, seat_type, price, status=SeatStatus.AVAILABLE):
        self.seat_id = seat_id
        self.row = row
        self.col = col
        self.seat_type = seat_type
        self.price = price
        self.status = status

    def get_status(self):
        return self.status

    def book(self):
        if self.status == SeatStatus.AVAILABLE:
            self.status = SeatStatus.BOOKED
            return True
        return False

    def cancel(self):
        if self.status == SeatStatus.BOOKED:
            self.status = SeatStatus.AVAILABLE
            return True
        return False

# Show
class Show:
    def __init__(self, show_id, movie, theater, start_time):
        self.show_id = show_id
        self.movie = movie
        self.theater = theater
        self.start_time = start_time
        self.seats = {}  # seat_id: Seat

    def get_id(self):
        return self.show_id

    def get_available_seats(self):
        return [seat for seat in self.seats.values() if seat.get_status() == SeatStatus.AVAILABLE]

# Theater
class Theater:
    def __init__(self, theater_id):
        self.theater_id = theater_id
        self.shows = []

    def get_id(self):
        return self.theater_id

    def add_show(self, show):
        self.shows.append(show)

# Movie
class Movie:
    def __init__(self, id, title, duration):
        self.id = id
        self.title = title
        self.duration = duration

    def get_id(self):
        return self.id

# Person Hierarchy
class Person:
    def __init__(self, id, name, phone, email):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email

    def get_id(self):
        return self.id

class Customer(Person):
    pass

class Staff(Person):
    def __init__(self, id, name, phone, email, role):
        super().__init__(id, name, phone, email)
        self.role = role

# Booking
class Booking:
    def __init__(self, booking_id, user_id, show_id, seats):
        self.booking_id = booking_id
        self.user_id = user_id
        self.show_id = show_id
        self.seats = seats
        self.status = BookingStatus.PENDING

    def get_seats(self):
        return self.seats

    def update_status(self, status):
        self.status = status

# BookingManager Singleton
class BookingManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance.__init_instance()
            return cls._instance

    def __init_instance(self):
        self.bookings = {}
        self._booking_lock = Lock()

    def create_booking(self, user, show, seats):
        with self._booking_lock:
            for seat in seats:
                if seat.get_status() != SeatStatus.AVAILABLE:
                    return False
            for seat in seats:
                if not seat.book():
                    return False

            booking_id = f"{user.get_id()}_{show.get_id()}_{datetime.now().timestamp()}"
            booking = Booking(booking_id, user.get_id(), show.get_id(), seats)
            booking.update_status(BookingStatus.CONFIRMED)
            self.bookings[booking_id] = booking
            return True

    def cancel_booking(self, booking_id):
        with self._booking_lock:
            booking = self.bookings.get(booking_id)
            if not booking:
                return False
            for seat in booking.get_seats():
                seat.cancel()
            booking.update_status(BookingStatus.CANCELLED)
            return True

# Payment
class Payment:
    def __init__(self, id, amount, method, status=PaymentStatus.PENDING):
        self.id = id
        self.amount = amount
        self.method = method
        self.status = status
        self.timestamp = datetime.now()

    def update_status(self, status):
        self.status = status

# Payment Services
class PaymentGateway(ABC):
    @abstractmethod
    def pay(self, amount, customer):
        pass

class CashPayment(PaymentGateway):
    def pay(self, amount, customer):
        print("Cash payment successful")
        return True

class CreditPayment(PaymentGateway):
    def pay(self, amount, customer):
        print("Credit card payment successful")
        return True

class PaymentService:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance.__init_instance()
            return cls._instance

    def __init_instance(self):
        self.payments = {}

    def make_payment(self, id, method, amount, customer):
        payment = Payment(id, amount, method)
        success = method.pay(amount, customer)
        payment.update_status(PaymentStatus.CONFIRMED if success else PaymentStatus.FAILED)
        self.payments[id] = payment
        return success

# MovieTicketBooking Facade
class MovieTicketBooking:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        self.movies = {}
        self.shows = {}
        self.theaters = {}

    def add_movie(self, movie):
        self.movies[movie.get_id()] = movie

    def add_show(self, show):
        self.shows[show.get_id()] = show

    def add_theater(self, theater):
        self.theaters[theater.get_id()] = theater

    def book_tickets(self, customer, show_id, seat_ids):
        show = self.shows.get(show_id)
        if not show:
            return False  # Show doesn't exist

        seats_to_book = [show.seats[sid] for sid in seat_ids if sid in show.seats]

        return BookingManager().create_booking(customer, show, seats_to_book)

from datetime import datetime, timedelta

# Set up movie, theater, show
movie = Movie("m1", "Inception", 148)
theater = Theater("t1")
show = Show("s1", movie, theater, datetime.now() + timedelta(hours=1))

# Add seats to the show
for i in range(1, 6):
    seat = Seat(f"A{i}", "A", i, SeatType.NORMAL, 120)
    show.seats[seat.seat_id] = seat

# Link show to theater
theater.add_show(show)

# Set up booking system
system = MovieTicketBooking()
system.add_movie(movie)
system.add_theater(theater)
system.add_show(show)

# Create a customer
customer = Customer("u1", "Alice", "9999999999", "alice@example.com")

# Print available seats before booking
print("Available seats before booking:")
for seat in show.get_available_seats():
    print(seat.seat_id, seat.get_status().name)

# Book a couple of seats
success = system.book_tickets(customer, "s1", ["A1", "A2"])
print("\nBooking A1 and A2:", "Success" if success else "Failed")

# Print available seats after booking
print("\nAvailable seats after booking:")
for seat in show.get_available_seats():
    print(seat.seat_id, seat.get_status().name)

# Try booking already booked seats
print("\nAttempt to rebook A1:")
success = system.book_tickets(customer, "s1", ["A1"])
print("Booking A1 again:", "Success" if success else "Failed")

# Try making a payment
payment_service = PaymentService()
payment_success = payment_service.make_payment("pay1", CashPayment(), 240, customer)
print("\nPayment result:", "Success" if payment_success else "Failed")

# Done
print("\nDone ✅")
