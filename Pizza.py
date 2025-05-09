from abc import ABC, abstractmethod
from threading import Lock
from enum import Enum

# Enums
class BaseType(Enum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3

class CrustType(Enum):
    THIN = 1
    THICK = 2
    STUFFED = 3

class ToppingType(Enum):
    CHEESE = 10
    CORN = 10
    JALAPENO = 10
    OLIVES = 10
    DOUBLE_CHEESE = 10
    ONIONS = 10
    PANEER = 20

class PaymentStatus(Enum):
    PENDING = 1
    COMPLETED = 2
    FAILED = 3

class OrderStatus(Enum):
    PENDING = 1
    IN_PROGRESS = 2
    DELIVERED = 3
    CANCELLED = 4

# Price Maps
BasePrices = {
    BaseType.SMALL: 10,
    BaseType.MEDIUM: 20,
    BaseType.LARGE: 30
}

CrustPrices = {
    CrustType.THIN: 10,
    CrustType.THICK: 20,
    CrustType.STUFFED: 30
}

ToppingPrices = {
    ToppingType.CORN: 10,
    ToppingType.JALAPENO: 10,
    ToppingType.OLIVES: 10,
    ToppingType.DOUBLE_CHEESE: 10,
    ToppingType.ONIONS: 10,
    ToppingType.PANEER: 20
}

# Base Class
class Base:
    def __init__(self, base_type):
        self.base_type = base_type

    def get_price(self):
        return BasePrices[self.base_type]

# Crust Class
class Crust:
    def __init__(self, crust_type):
        self.crust_type = crust_type

    def get_price(self):
        return CrustPrices[self.crust_type]

# Topping Class
class Topping:
    def __init__(self, topping_type, qty=1):
        self.topping_type = topping_type
        self.qty = qty

    def get_topping_type(self):
        return self.topping_type

    def add_qty(self, qty_to_add=1):
        self.qty += qty_to_add

    def remove_topping(self, qty_to_remove=1):
        self.qty -= min(self.qty, qty_to_remove)

    def get_qty(self):
        return self.qty

    def get_price(self):
        return ToppingPrices[self.topping_type] * self.qty

# Topping Manager
class ToppingManager:
    def __init__(self):
        self.toppings = []

    def add_topping(self, new_topping_type, qty):
        for curr_topping in self.toppings:
            if curr_topping.get_topping_type() == new_topping_type:
                curr_topping.add_qty(qty)
                return
        self.toppings.append(Topping(new_topping_type, qty))

    def remove_topping(self, topping_type_to_remove, qty):
        for curr_topping in self.toppings:
            if curr_topping.get_topping_type() == topping_type_to_remove:
                curr_topping.remove_topping(qty)
                if curr_topping.get_qty() == 0:
                    self.toppings.remove(curr_topping)
                break

    def get_price(self):
        return sum(t.get_price() for t in self.toppings)

# Pizza Class
class Pizza:
    def __init__(self, id, base_type, crust_type):
        self.id = id
        self.base = Base(base_type)
        self.crust = Crust(crust_type)
        self.topping_manager = ToppingManager()

    def get_id(self):
        return self.id

    def add_topping(self, new_topping_type, qty):
        self.topping_manager.add_topping(new_topping_type, qty)

    def remove_topping(self, topping_type_to_remove, qty):
        self.topping_manager.remove_topping(topping_type_to_remove, qty)

    def get_price(self):
        return self.base.get_price() + self.crust.get_price() + self.topping_manager.get_price()

# Payment Strategy Pattern
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount):
        pass

class InteracPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Paid ₹{amount} using Interac")
        return PaymentStatus.COMPLETED

class CreditCardPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Paid ₹{amount} using Credit Card")
        return PaymentStatus.COMPLETED

# Order Class
class Order:
    def __init__(self, order_id, pizzas=None, status=OrderStatus.PENDING):
        self.id = order_id
        self.pizzas = pizzas if pizzas else []
        self.status = status
        self.payment_status = PaymentStatus.PENDING

    def add_pizza(self, pizza):
        self.pizzas.append(pizza)

    def remove_pizza(self, pizza_id):
        self.pizzas = [p for p in self.pizzas if p.get_id() != pizza_id]

    def get_order_price(self):
        return sum(p.get_price() for p in self.pizzas)

    def make_payment(self, payment_strategy: PaymentStrategy):
        amount = self.get_order_price()
        self.payment_status = payment_strategy.pay(amount)
        if self.payment_status == PaymentStatus.COMPLETED:
            self.status = OrderStatus.IN_PROGRESS

    def update_status(self, status):
        self.status = status

    def get_status(self):
        return self.status

    def get_payment_status(self):
        return self.payment_status

    def cancel_order(self):
        self.update_status(OrderStatus.CANCELLED)

# Order Manager Singleton
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
        self.order_id_counter = 0

    def create_order(self, pizzas):
        self.order_id_counter += 1
        order = Order(self.order_id_counter, pizzas)
        self.orders[self.order_id_counter] = order
        return order

    def cancel_order(self, order_id):
        if order_id in self.orders:
            self.orders[order_id].cancel_order()

# Example usage:
if __name__ == '__main__':
    om = OrderManager()

    pizza1 = Pizza(1, BaseType.MEDIUM, CrustType.THIN)
    pizza1.add_topping(ToppingType.OLIVES, 2)
    pizza1.add_topping(ToppingType.PANEER, 1)

    pizza2 = Pizza(2, BaseType.SMALL, CrustType.STUFFED)
    pizza2.add_topping(ToppingType.CORN, 3)

    order = om.create_order([pizza1, pizza2])
    order.make_payment(InteracPayment())

    print("Order Price:", order.get_order_price())
    print("Order Status:", order.get_status())
    print("Payment Status:", order.get_payment_status())
