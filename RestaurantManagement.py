from enum import Enum
from datetime import datetime
from threading import Lock


# Enums
class OrderStatus(Enum):
    PENDING = 'Pending'
    PREPARING = 'Preparing'
    READY = 'Ready'
    COMPLETED = 'Completed'
    CANCELLED = 'Cancelled'


class PaymentMethod(Enum):
    CASH = 'Cash'
    CREDIT_CARD = 'Credit Card'
    MOBILE_PAYMENT = 'Mobile Payment'


class PaymentStatus(Enum):
    PENDING = 'Pending'
    COMPLETED = 'Completed'
    FAILED = 'Failed'


# Entities
class MenuItem:
    def __init__(self, id, name, description, price, available=True):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.available = available

    def get_id(self):
        return self.id

    def get_item_name(self):
        return self.name

    def get_description(self):
        return self.description

    def get_price(self):
        return self.price

    def is_available(self):
        return self.available


class Order:
    def __init__(self, id, menu_items):
        self.id = id
        self.items = menu_items
        self.order_amount = sum(item.get_price() for item in self.items)
        self.status = OrderStatus.PENDING
        self.timestamp = datetime.now()

    def update_status(self, status):
        self.status = status

    def get_order_amount(self):
        return self.order_amount

    def get_id(self):
        return self.id


class Payment:
    def __init__(self, id, amount, method):
        self.id = id
        self.amount = amount
        self.method = method
        self.status = PaymentStatus.PENDING
        self.timestamp = datetime.now()

    def update_status(self, status):
        self.status = status


class Reservation:
    def __init__(self, id, cust_name, cust_mobile, party_size, reservation_time):
        self.id = id
        self.cust_name = cust_name
        self.cust_mobile = cust_mobile
        self.party_size = party_size
        self.reservation_time = reservation_time

    def get_reservation_id(self):
        return self.id


class Staff:
    def __init__(self, id, name, role, mobile):
        self.id = id
        self.name = name
        self.role = role
        self.mobile = mobile

    def get_id(self):
        return self.id


# ---------------------- PaymentService ----------------------
class PaymentService:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance

    def process_payment(self, payment_method, order, payment_amount):
        payment = Payment(payment_method, order.get_order_amount(), payment_method)
        if payment_method.pay(order, payment_amount):
            payment.update_status(PaymentStatus.COMPLETED)
        else:
            payment.update_status(PaymentStatus.FAILED)
        return payment


# ---------------------- PaymentGateway ----------------------
class PaymentGateway:
    def pay(self, order, amount):
        pass


class CashPayment(PaymentGateway):
    def pay(self, order, amount):
        print(f"Payment of ${amount:.2f} received via Cash.")
        return True


class CreditCardPayment(PaymentGateway):
    def pay(self, order, amount):
        print(f"Payment of ${amount:.2f} received via Credit Card.")
        return True


class MobilePayment(PaymentGateway):
    def pay(self, order, amount):
        print(f"Payment of ${amount:.2f} received via Mobile Payment.")
        return True


# ---------------------- OrderManager ----------------------
class OrderManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.orders = {}
        self.order_counter = 1

    def place_order(self, user, item_ids, restaurant):
        items = [restaurant.menu[i] for i in item_ids if i in restaurant.menu and restaurant.menu[i].is_available()]
        order = Order(self.order_counter, items)
        self.orders[order.get_id()] = order
        self.order_counter += 1
        return order


# ---------------------- Restaurant ----------------------
class Restaurant:
    _instance = None
    _instance_lock = Lock()

    def __init__(self):
        if Restaurant._instance is not None:
            raise Exception("This class is a Singleton!")

        self.menu = {}
        self.orders = {}
        self.reservations = {}
        self.staff_members = {}

        # Locks
        self._menu_lock = Lock()
        self._orders_lock = Lock()
        self._reservations_lock = Lock()
        self._staff_members_lock = Lock()

        # Create an instance of PaymentService
        self.payment_service = PaymentService()

        Restaurant._instance = self

    @staticmethod
    def get_instance():
        with Restaurant._instance_lock:
            if Restaurant._instance is None:
                Restaurant()
            return Restaurant._instance

    # Menu Management
    def add_menu_item(self, id, name, description, price, available=True):
        with self._menu_lock:
            item = MenuItem(id, name, description, price, available)
            self.menu[item.get_id()] = item
            return item

    def get_menu(self):
        with self._menu_lock:
            return list(self.menu.values())

    # Order Management
    def place_order(self, id, item_ids):
        with self._orders_lock:
            order_manager = OrderManager()
            order = order_manager.place_order(id, item_ids, self)
            return order

    def update_order_status(self, order_id, status):
        with self._orders_lock:
            if order_id in self.orders:
                self.orders[order_id].update_status(status)

    # Reservation Management
    def make_reservation(self, id, name, mobile, party_size, time):
        with self._reservations_lock:
            reservation = Reservation(id, name, mobile, party_size, time)
            self.reservations[reservation.get_reservation_id()] = reservation
            return reservation

    # Staff Management
    def add_staff(self, id, name, role, mobile):
        with self._staff_members_lock:
            staff = Staff(id, name, role, mobile)
            self.staff_members[staff.get_id()] = staff

    def get_staff(self):
        with self._staff_members_lock:
            return list(self.staff_members.values())

    # Payment Processing (using PaymentService)
    def process_payment(self, order_id, payment_method: PaymentGateway):
        with self._orders_lock:
            if order_id not in self.orders:
                return None
            order = self.orders[order_id]
            payment = self.payment_service.process_payment(payment_method, order, order.get_order_amount())
            return payment


# ---------------------- Demo ----------------------

# Get the singleton instance of the restaurant
restaurant = Restaurant.get_instance()

# Add vegetarian menu items
restaurant.add_menu_item(1, "Paneer Tikka", "Grilled cottage cheese with spices", 9.5)
restaurant.add_menu_item(2, "Veg Biryani", "Basmati rice cooked with veggies", 8.0)
restaurant.add_menu_item(3, "Masala Dosa", "South Indian crepe with potato filling", 6.5)

# Place an order for some vegetarian items
order = restaurant.place_order(101, [1, 2])
print(f"\n🧾 Order Placed - ID: {order.id}, Total: ${order.get_order_amount():.2f}, Status: {order.status.name}")

# Process payment (using CashPayment)
payment = restaurant.process_payment(order.id, CashPayment())
print(f"\n💳 Payment Processed - Amount: ${payment.amount}, Method: {payment.method.name}, Status: {payment.status.name}")

# Update order status
restaurant.update_order_status(order.id, OrderStatus.READY)
print(f"🚚 Order Status Updated - ID: {order.id}, New Status: {order.status.name}")

# Make a reservation
reservation = restaurant.make_reservation(201, "Riya Sharma", "9876543210", 4, datetime.now())
print(f"\n📅 Reservation Made - ID: {reservation.id}, Name: {reservation.cust_name}")

# Add staff
restaurant.add_staff(301, "Anjali", "Waitress", "9123456789")
print("\n👩‍🍳 Staff Added - Name: Anjali, Role: Waitress")
