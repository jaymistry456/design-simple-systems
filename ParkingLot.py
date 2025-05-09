from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime

# ===========================
# Enums
# ===========================

class VehicleType(Enum):
    BIKE = 'Bike'
    CAR = 'Car'
    TRUCK = 'Truck'

class SpotType(Enum):
    COMPACT = "Compact"
    LARGE = "Large"
    HANDICAPPED = "Handicapped"

# ===========================
# Vehicle
# ===========================

class Vehicle:
    def __init__(self, reg_num, vehicle_type: VehicleType):
        self.reg_num = reg_num
        self.vehicle_type = vehicle_type

    def get_vehicle_reg_num(self):
        return self.reg_num

    def get_vehicle_type(self):
        return self.vehicle_type

# ===========================
# Parking Spot
# ===========================

class ParkingSpot:
    def __init__(self, spot_id, spot_type):
        self.spot_id = spot_id
        self.spot_type = spot_type
        self._vehicle = None

    def is_available(self):
        return self._vehicle is None

    def assign_vehicle(self, vehicle):
        if not self.is_available():
            return False
        self._vehicle = vehicle
        return True

    def release_vehicle(self):
        if self._vehicle is None:
            return False
        self._vehicle = None
        return True

    def get_vehicle(self):
        return self._vehicle

    def get_spot_id(self):
        return self.spot_id

    def get_spot_type(self):
        return self.spot_type

# ===========================
# Parking Floor
# ===========================

class ParkingFloor:
    def __init__(self, floor_num, compact, large, handicapped):
        self.floor_num = floor_num
        self.parking_spots = []

        for i in range(compact):
            self.parking_spots.append(ParkingSpot(f"C{i}_F{floor_num}", SpotType.COMPACT))
        for i in range(large):
            self.parking_spots.append(ParkingSpot(f"L{i}_F{floor_num}", SpotType.LARGE))
        for i in range(handicapped):
            self.parking_spots.append(ParkingSpot(f"H{i}_F{floor_num}", SpotType.HANDICAPPED))

    def get_parking_spots(self):
        return self.parking_spots

# ===========================
# Parking Lot
# ===========================

class ParkingLot:
    def __init__(self, total_floors, compact_per_floor, large_per_floor, handicapped_per_floor):
        self.total_floors = total_floors
        self.parking_floors = [
            ParkingFloor(i, compact_per_floor, large_per_floor, handicapped_per_floor) for i in range(self.total_floors)
        ]

    def get_required_spot_type(self, vehicle_type, is_handicapped):
        if vehicle_type in [VehicleType.BIKE, VehicleType.CAR]:
            return SpotType.HANDICAPPED if is_handicapped else SpotType.COMPACT
        return SpotType.LARGE

# ===========================
# Parking Ticket
# ===========================

class ParkingTicket:
    def __init__(self, vehicle, spot_id, floor):
        self.vehicle = vehicle
        self.spot_id = spot_id
        self.floor = floor
        self.issued_at = datetime.now()

# ===========================
# Parking Manager
# ===========================

class ParkingManager:
    def __init__(self, parking_lot):
        self.parking_lot = parking_lot
        self.active_tickets = {}

    def park_vehicle(self, vehicle, is_handicapped=False):
        required_spot_type = self.parking_lot.get_required_spot_type(vehicle.get_vehicle_type(), is_handicapped)

        for floor in self.parking_lot.parking_floors:
            for spot in floor.get_parking_spots():
                if spot.get_spot_type() == required_spot_type and spot.is_available():
                    spot.assign_vehicle(vehicle)
                    ticket = ParkingTicket(vehicle, spot.get_spot_id(), floor.floor_num)
                    self.active_tickets[vehicle.get_vehicle_reg_num()] = ticket
                    print(f"✅ Vehicle {vehicle.get_vehicle_reg_num()} parked at spot {spot.get_spot_id()}")
                    return ticket
        print(f"❌ No Parking Spot available for {vehicle.get_vehicle_reg_num()}")
        return None

    def unpark_vehicle(self, vehicle_reg_num):
        ticket = self.active_tickets.get(vehicle_reg_num)
        if not ticket:
            print(f"⚠️ No active ticket found for {vehicle_reg_num}")
            return False

        floor = self.parking_lot.parking_floors[ticket.floor]
        for spot in floor.get_parking_spots():
            if spot.get_spot_id() == ticket.spot_id:
                if spot.release_vehicle():
                    print(f"🟢 Vehicle {vehicle_reg_num} removed from spot {spot.get_spot_id()}")
                    del self.active_tickets[vehicle_reg_num]
                    return True
        print(f"❌ Could not unpark {vehicle_reg_num}")
        return False

# ===========================
# Test
# ===========================

if __name__ == "__main__":
    lot = ParkingLot(total_floors=2, compact_per_floor=2, large_per_floor=1, handicapped_per_floor=1)
    manager = ParkingManager(lot)

    bike = Vehicle("BIKE-123", VehicleType.BIKE)
    car = Vehicle("CAR-456", VehicleType.CAR)
    truck = Vehicle("TRUCK-789", VehicleType.TRUCK)
    another_truck = Vehicle("TRUCK-999", VehicleType.TRUCK)

    manager.park_vehicle(bike)
    manager.park_vehicle(car)
    manager.park_vehicle(truck)
    manager.park_vehicle(another_truck)

    manager.unpark_vehicle("BIKE-123")
    manager.park_vehicle(another_truck)
