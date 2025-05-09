from abc import ABC, abstractmethod
from enum import Enum
from threading import Lock
from datetime import datetime


# Enums
class RoomType(Enum):
    SINGLE = 1
    DOUBLE = 2
    DELUXE = 3


class RoomStatus(Enum):
    AVAILABLE = 1
    RESERVED = 2
    OCCUPIED = 3


class BookingStatus(Enum):
    PENDING = 1
    COMPLETED = 2
    CHECK_IN = 3
    CHECK_OUT = 4
    CANCELLED = 5
    FAILED = 6


class PaymentStatus(Enum):
    PENDING = 1
    COMPLETED = 2
    FAILED = 3


# Room
class Room:
    def __init__(self, room_no, room_type, price, status=RoomStatus.AVAILABLE):
        self.room_no = room_no
        self.room_type = room_type
        self.price = price
        self.status = status

    def get_room_no(self):
        return self.room_no

    def get_room_type(self):
        return self.room_type

    def get_price(self):
        return self.price

    def is_available(self):
        return self.status == RoomStatus.AVAILABLE

    def update_status(self, status):
        self.status = status

    def reserve(self):
        self.update_status(RoomStatus.RESERVED)

    def check_in(self):
        self.update_status(RoomStatus.OCCUPIED)

    def check_out(self):
        self.update_status(RoomStatus.AVAILABLE)

    def __str__(self):
        return f"Room {self.room_no} - {self.room_type.name}, ₹{self.price}, Status: {self.status.name}"


# Person, Guest, Staff
class Person:
    def __init__(self, id, name, phone, email):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_phone(self):
        return self.phone

    def get_email(self):
        return self.email


class Guest(Person):
    def __init__(self, id, name, phone, email):
        super().__init__(id, name, phone, email)


class Staff(Person):
    def __init__(self, id, name, phone, email, role):
        super().__init__(id, name, phone, email)
        self.role = role

    def get_role(self):
        return self.role


# Booking
class Booking:
    def __init__(self, booking_no, room, guest, check_in_date, check_out_date):
        self.booking_no = booking_no
        self.room = room
        self.guest = guest
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date
        self.status = BookingStatus.PENDING

    def get_booking_no(self):
        return self.booking_no

    def get_guest_id(self):
        return self.guest.get_id()

    def get_status(self):
        return self.status

    def update_status(self, status):
        self.status = status

    def check_in(self):
        self.update_status(BookingStatus.CHECK_IN)
        self.room.check_in()

    def check_out(self):
        self.update_status(BookingStatus.CHECK_OUT)
        self.room.check_out()

    def cancel(self):
        self.update_status(BookingStatus.CANCELLED)
        self.room.update_status(RoomStatus.AVAILABLE)

    def __str__(self):
        return f"Booking {self.booking_no} for Room {self.room.get_room_no()} by Guest {self.guest.get_name()} - Status: {self.status.name}"


# Payment Strategy
class Payment(ABC):
    @abstractmethod
    def pay(self, guest_id, amount):
        pass


class CreditCard(Payment):
    def __init__(self, card_no, expiry_date, cvv):
        self.card_no = card_no
        self.expiry_date = expiry_date
        self.cvv = cvv

    def pay(self, guest_id, amount):
        print(f"[CreditCard] ₹{amount} paid by Guest ID: {guest_id}")
        return PaymentStatus.COMPLETED


class CashPayment(Payment):
    def pay(self, guest_id, amount):
        print(f"[CashPayment] ₹{amount} paid by Guest ID: {guest_id}")
        return PaymentStatus.COMPLETED


# Payment Service
class PaymentService:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance

    def make_payment(self, payment_method, guest_id, amount):
        return payment_method.pay(guest_id, amount)


# Booking Manager
class BookingManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.bookings = {}
        self.payment_service = PaymentService()

    def book_room(self, booking_no, room, guest, check_in_date, check_out_date, payment_method):
        with self._lock:
            room.reserve()
            booking = Booking(booking_no, room, guest, check_in_date, check_out_date)

            payment_status = self.payment_service.make_payment(payment_method, guest.get_id(), room.get_price())
            if payment_status == PaymentStatus.COMPLETED:
                booking.update_status(BookingStatus.COMPLETED)
            else:
                booking.update_status(BookingStatus.FAILED)
                room.update_status(RoomStatus.AVAILABLE)

            self.bookings[booking_no] = booking
            return booking

    def cancel(self, booking_no):
        booking = self.bookings.get(booking_no)
        if booking:
            booking.cancel()

    def check_in(self, booking_no, guest):
        booking = self.bookings.get(booking_no)
        if booking and booking.get_guest_id() == guest.get_id():
            booking.check_in()

    def check_out(self, booking_no):
        booking = self.bookings.get(booking_no)
        if booking:
            booking.check_out()


# Hotel Management
class HotelManagement:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.guests = {}
        self.staff = {}
        self.rooms = {}
        self.booking_manager = BookingManager()

    def add_guest(self, guest):
        self.guests[guest.get_id()] = guest

    def add_staff(self, member):
        self.staff[member.get_id()] = member

    def add_room(self, room):
        self.rooms[room.get_room_no()] = room

    def find_available_room(self, room_type, max_price):
        for room in self.rooms.values():
            if room.get_room_type() == room_type and room.get_price() <= max_price and room.is_available():
                return room
        return None

    def book_room(self, booking_no, room, guest, check_in, check_out, payment_method):
        return self.booking_manager.book_room(booking_no, room, guest, check_in, check_out, payment_method)

    def check_in(self, booking_no, guest):
        self.booking_manager.check_in(booking_no, guest)

    def check_out(self, booking_no):
        self.booking_manager.check_out(booking_no)

    def cancel(self, booking_no):
        self.booking_manager.cancel(booking_no)


if __name__ == "__main__":
    # Step 1: Setup hotel
    hotel = HotelManagement()

    # Create a room and add it to hotel
    room1 = Room(room_no=101, room_type=RoomType.SINGLE, price=2000)
    hotel.add_room(room1)

    # Create a guest
    guest1 = Guest(id="G001", name="Alice", phone="9876543210", email="alice@example.com")
    hotel.add_guest(guest1)

    # Choose a payment method
    payment_method = CashPayment()

    # Step 2: Book room
    booking_id = "B001"
    check_in_date = datetime(2025, 4, 21)
    check_out_date = datetime(2025, 4, 23)

    booking = hotel.book_room(
        booking_no=booking_id,
        room=room1,
        guest=guest1,
        check_in=check_in_date,
        check_out=check_out_date,
        payment_method=payment_method
    )

    print("\n--- After Booking ---")
    print(booking)

    # Step 3: Check in
    hotel.check_in(booking_id, guest1)
    print("\n--- After Check-in ---")
    print(booking)

    # Step 4: Check out
    hotel.check_out(booking_id)
    print("\n--- After Check-out ---")
    print(booking)

    # Step 5: Cancel (will have no effect post check-out)
    hotel.cancel(booking_id)
    print("\n--- After Cancel Attempt ---")
    print(booking)
