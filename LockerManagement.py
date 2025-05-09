from enum import Enum
from datetime import datetime
from threading import Lock


# Enums
class LockerSize(Enum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3


class LockerStatus(Enum):
    AVAILABLE = 1
    OCCUPIED = 2


# Notification
class NotificationChannel:
    def send(self, to, subject, message):
        pass


class EmailNotification(NotificationChannel):
    def send(self, to, subject, message):
        print(f"Sending Email to {to}: {subject} - {message}")


class SMSNotification(NotificationChannel):
    def send(self, to, subject, message):
        print(f"Sending SMS to {to}: {subject} - {message}")


class PushNotification(NotificationChannel):
    def send(self, to, subject, message):
        print(f"Sending Push to {to}: {subject} - {message}")


class NotificationService:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance.__int__()
        return cls._instance

    def __int__(self):
        self.channels = []

    def register_channel(self, channel):
        self.channels.append(channel)

    def send_notification(self, to, subject, message):
        for channel in self.channels:
            channel.send(to, subject, message)


# Locker Manager
class LockerManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance.__int__()
        return cls._instance

    def __int__(self):
        self.lockers = []
        self.package_locker_map = {}
        self.notification_service = NotificationService()

    def add_locker(self, locker):
        self.lockers.append(locker)

    def assign_package_to_locker(self, package):
        for locker in self.lockers:
            if locker.is_available() and locker.get_size() == package.get_size():
                locker.assign_package(package)
                self.package_locker_map[package.tracking_id] = locker
                self.notification_service.send_notification(
                    package.user.email,
                    "Package Assigned to Locker",
                    f"Your package {package.tracking_id} has been placed in locker {locker.locker_id}."
                )
                return True
        return False

    def retrieve_package(self, package):
        locker = self.package_locker_map.get(package.tracking_id)
        if locker and locker.get_package():
            locker.release_package()
            del self.package_locker_map[package.tracking_id]
            return True
        return False


# Locker
class Locker:
    def __init__(self, locker_id, size):
        self.locker_id = locker_id
        self.size = size
        self.status = LockerStatus.AVAILABLE
        self.package = None

    def is_available(self):
        return self.status == LockerStatus.AVAILABLE

    def get_size(self):
        return self.size

    def assign_package(self, package):
        self.package = package
        self.status = LockerStatus.OCCUPIED
        package.set_delivered()

    def release_package(self):
        self.package = None
        self.status = LockerStatus.AVAILABLE

    def get_package(self):
        return self.package


# Package
class Package:
    def __init__(self, tracking_id, size, user):
        self.tracking_id = tracking_id
        self.size = size
        self.user = user
        self.delivered_at = None

    def set_delivered(self):
        self.delivered_at = datetime.now()

    def get_delivery_date(self):
        return self.delivered_at

    def get_size(self):
        return self.size


# User
class User:
    def __init__(self, user_id, name, email, phone, push_id):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone = phone
        self.push_id = push_id


# Example usage
if __name__ == "__main__":
    # Create users
    user1 = User(1, "John Doe", "john.doe@example.com", '111-222-3333', 'push-1234')

    # Create lockers
    locker1 = Locker("L001", LockerSize.SMALL)
    locker2 = Locker("L002", LockerSize.MEDIUM)

    # Add lockers to locker manager (singleton)
    locker_manager = LockerManager()
    locker_manager.add_locker(locker1)
    locker_manager.add_locker(locker2)

    # Register notification channels (singleton NotificationService)
    notification_service = NotificationService()
    notification_service.register_channel(EmailNotification())
    notification_service.register_channel(SMSNotification())
    notification_service.register_channel(PushNotification())

    # Create a package
    package1 = Package("PKG123", LockerSize.SMALL, user1)

    # Assign package to locker
    locker_manager.assign_package_to_locker(package1)

    # Retrieve package
    locker_manager.retrieve_package(package1)
