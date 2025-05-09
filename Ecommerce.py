from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from threading import Lock

# ---------------------- Product ----------------------
class Product:
    def __init__(self, id, name, price, stock, seller):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
        self.seller = seller

    def is_available(self, quantity):
        return self.stock >= quantity

    def remove_stock(self, quantity):
        if self.is_available(quantity):
            self.stock -= quantity
            return True
        return False

    def add_stock(self, quantity):
        self.stock += quantity


# ---------------------- Inventory ----------------------
class Inventory:
    def __init__(self):
        self.products = {}

    def add_product(self, product):
        self.products[product.id] = product

    def get_product_by_id(self, id):
        return self.products.get(id)

    def list_all_products(self):
        return list(self.products.values())


# ---------------------- Person ----------------------
class Person(ABC):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name


# ---------------------- User ----------------------
class User(Person):
    def __init__(self, id, name, address):
        super().__init__(id, name)
        self.address = address
        self.cart = Cart(self)
        self.order_history = []

    def get_address(self):
        return self.address

    def get_cart_items(self):
        return self.cart.get_items()

    def get_cart_total(self):
        return self.cart.get_cart_total()

    def clear_cart(self):
        self.cart = Cart(self)

    def add_to_order_history(self, order):
        self.order_history.append(order)


# ---------------------- Seller ----------------------
class Seller(Person):
    def __init__(self, id, name):
        super().__init__(id, name)
        self.products = []

    def add_product(self, name, price, stock):
        product = Product(str(id), name, price, stock, self)
        self.products.append(product)
        return product

    def remove_product(self, id):
        for product in self.products:
            if product.id == id:
                self.products.remove(product)
                return product
        return None

    def list_products(self):
        return self.products


# ---------------------- Cart ----------------------
class Cart:
    def __init__(self, user):
        self.user = user
        self.items = {}

    def add_product(self, product, quantity):
        if product.remove_stock(quantity):
            self.items[product] = self.items.get(product, 0) + quantity
        else:
            print(f"[Cart] Not enough stock for product: {product.name}")

    def remove_product(self, product):
        if product in self.items:
            self.items[product] -= 1
            if self.items[product] <= 0:
                del self.items[product]

    def get_cart_total(self):
        return sum(product.price * quantity for product, quantity in self.items.items())

    def get_items(self):
        return self.items.copy()


# ---------------------- Payment ----------------------
class PaymentStatus(Enum):
    PENDING = 'Pending'
    COMPLETE = 'Complete'
    FAILED = 'Failed'


# Payment Service Singleton
class PaymentService:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance

    def make_payment(self, payment_method, user, amount):
        return payment_method.pay(user, amount)


# ---------------------- Payment Gateway ----------------------
class PaymentGateway(ABC):
    @abstractmethod
    def pay(self, user, amount):
        pass


class SimplePaymentGateway(PaymentGateway):
    def pay(self, user, amount):
        print(f"[SimplePayment] ${amount:.2f} charged to {user.get_name()}")
        return True


class CreditCardPayment(PaymentGateway):
    def pay(self, user, amount):
        print(f"[CreditCard] ${amount:.2f} charged to {user.get_name()}'s credit card")
        return True


class PaypalPayment(PaymentGateway):
    def pay(self, user, amount):
        print(f"[Paypal] ${amount:.2f} charged to {user.get_name()}'s PayPal account")
        return True


# ---------------------- Order ----------------------
class OrderStatus(Enum):
    PENDING = 'Pending'
    IN_PROGRESS = 'In Progress'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'


class Order:
    def __init__(self, id, user, items, total):
        self.id = id
        self.user = user
        self.items = items
        self.total = total
        self.address = user.get_address()
        self.status = OrderStatus.PENDING
        self.created_at = datetime.now()

    def update_status(self, status):
        self.status = status


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
        self.payment_service = PaymentService()


    def place_order(self, user, payment_method: PaymentGateway):
        items = user.get_cart_items()
        total_price = user.get_cart_total()
        order_id = self.order_counter
        self.order_counter += 1

        order = Order(order_id, user, items, total_price)
        self.orders[order_id] = order
        user.add_to_order_history(order)

        if self.payment_service.make_payment(payment_method, user, total_price):
            order.update_status(OrderStatus.IN_PROGRESS)
        else:
            order.update_status(OrderStatus.PENDING)  # or OrderStatus.FAILED

        user.clear_cart()

        return order


# ---------------------- Ecommerce ----------------------
class Ecommerce:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.users = {}
        self.sellers = {}
        self.inventory = Inventory()
        self.order_manager = OrderManager()

    def register_user(self, id, name, address):
        user = User(id, name, address)
        self.users[user.get_id()] = user
        return user

    def register_seller(self, id, name):
        seller = Seller(id, name)
        self.sellers[seller.get_id()] = seller
        return seller

    def list_all_products(self):
        return self.inventory.list_all_products()

    def place_order(self, user, payment_service: PaymentGateway):
        return self.order_manager.place_order(user, payment_service)


# ---------------------- Demo ----------------------
if __name__ == "__main__":
    system = AmazonSystem()

    seller = system.register_seller("s1", "CoolTech")
    p1 = seller.add_product("Keyboard", 49.99, 10)
    p2 = seller.add_product("Mouse", 19.99, 15)
    system.inventory.add_product(p1)
    system.inventory.add_product(p2)

    user = system.register_user("u1", "Alice", "123 Main Street")

    user.cart.add_product(p1, 2)
    user.cart.add_product(p2, 1)

    order = system.place_order(user, PaypalPayment())
    if order:
        print(f"Order Total: ${order.total:.2f}, Status: {order.status.name}")
