from abc import ABC
from enum import Enum
from threading import Lock
from datetime import datetime

# Enums
class PaymentStatus(Enum):
    PENDING = 1
    COMPLETED = 2
    FAILED = 3

class PaymentMethod(Enum):
    CASH = 1
    CREDIT = 2
    INSURANCE = 3

class PersonRole(Enum):
    PATIENT = 1
    DOCTOR = 2
    STAFF = 3

class AppointmentStatus(Enum):
    SCHEDULED = 1
    COMPLETED = 2
    CANCELLED = 3
    RESCHEDULED = 4

class BedStatus(Enum):
    AVAILABLE = 1
    OCCUPIED = 2

# Person
class Person(ABC):
    def __init__(self, id, name, email, phone, role):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.role = role

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_email(self):
        return self.email

    def get_phone(self):
        return self.phone

    def get_role(self):
        return self.role

# Patient
class Patient(Person):
    def __init__(self, id, name, email, phone, role, age, gender):
        super().__init__(id, name, email, phone, role)
        self.age = age
        self.gender = gender
        self.medical_history = []

    def get_age(self):
        return self.age

    def get_gender(self):
        return self.gender

    def add_medical_history(self, medical_record):
        self.medical_history.append(medical_record)

    def get_medical_history(self):
        return self.medical_history

# Medical Record
class MedicalRecordEntry:
    def __init__(self, date, doctor, patient, prescriptions=None, tests=None):
        self.date = date
        self.doctor = doctor
        self.patient = patient
        self.prescriptions = prescriptions or []
        self.tests = tests or []

class MedicalRecord:
    def __init__(self, patient_id):
        self.patient_id = patient_id
        self.entries = []

    def add_entry(self, doctor, patient, prescriptions, tests):
        entry = MedicalRecordEntry(datetime.now(), doctor, patient, prescriptions, tests)
        self.entries.append(entry)

    def get_history(self):
        return self.entries

# Doctor
class Doctor(Person):
    def __init__(self, id, name, email, phone, role, specialization):
        super().__init__(id, name, email, phone, role)
        self.specialization = specialization
        self.schedule = []

    def add_availability(self, timeslot):
        self.schedule.append(timeslot)

    def get_availability(self):
        return self.schedule

# Staff
class Staff(Person):
    def __init__(self, id, name, email, phone, role, department):
        super().__init__(id, name, email, phone, role)
        self.department = department

    def get_department(self):
        return self.department

# Appointment
class Appointment:
    def __init__(self, id, patient_id, doctor_id, timeslot):
        self.id = id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.timeslot = timeslot
        self.status = AppointmentStatus.SCHEDULED

    def get_id(self):
        return self.id

    def get_patient_id(self):
        return self.patient_id

    def get_doctor_id(self):
        return self.doctor_id

    def get_timeslot(self):
        return self.timeslot

    def get_status(self):
        return self.status

    def update_status(self, status):
        self.status = status

    def complete(self):
        self.update_status(AppointmentStatus.COMPLETED)

    def cancel(self):
        self.update_status(AppointmentStatus.CANCELLED)

    def reschedule(self, new_timeslot):
        self.timeslot = new_timeslot
        self.update_status(AppointmentStatus.RESCHEDULED)

# Appointment Manager
class AppointmentManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance.__init__()
            return cls._instance

    def __init__(self):
        self.appointments = {}
        self._appointment_lock = Lock()

    def schedule(self, appointment_id, patient, doctor, timeslot):
        with self._appointment_lock:
            for curr_appointment in self.appointments.values():
                if curr_appointment.get_timeslot() == timeslot and curr_appointment.get_status() == AppointmentStatus.SCHEDULED:
                    return None
                if curr_appointment.get_patient_id() == patient.get_id():
                    return None
            appointment = Appointment(appointment_id, patient.get_id(), doctor.get_id(), timeslot)
            self.appointments[appointment_id] = appointment
            doctor.add_availability(timeslot)
            return appointment

    def cancel(self, appointment_id):
        with self._appointment_lock:
            appointment = self.appointments.get(appointment_id)
            if appointment:
                appointment.cancel()
                return True
            return False

    def reschedule(self, appointment_id, new_timeslot, patient):
        with self._appointment_lock:
            appointment = self.appointments.get(appointment_id)
            if appointment:
                for curr in self.appointments.values():
                    if curr.get_timeslot() == new_timeslot and curr.get_status() == AppointmentStatus.SCHEDULED:
                        return None
                    if curr.get_patient_id() == patient.get_id():
                        return None
                appointment.reschedule(new_timeslot)
                return True
            return False

    def get_appointments_for_patient(self, patient_id):
        return [a for a in self.appointments.values() if a.get_patient_id() == patient_id]

    def get_appointments_for_doctor(self, doctor_id):
        return [a for a in self.appointments.values() if a.get_doctor_id() == doctor_id]

# Bill
class Bill:
    def __init__(self, id, patient_id, amount, status=PaymentStatus.PENDING):
        self.id = id
        self.patient_id = patient_id
        self.amount = amount
        self.status = status

    def get_id(self):
        return self.id

    def get_patient_id(self):
        return self.patient_id

    def get_amount(self):
        return self.amount

    def get_status(self):
        return self.status

    def update_status(self, status):
        self.status = status

# Billing Manager
class BillingManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance.__init__()
            return cls._instance

    def __init__(self):
        self.bills = {}

    def generate_bill(self, bill_id, patient_id, amount):
        bill = Bill(bill_id, patient_id, amount)
        self.bills[bill_id] = bill
        return bill

    def pay_bill(self, bill_id, payment_method):
        bill = self.bills.get(bill_id)
        if bill and payment_method in PaymentMethod:
            bill.update_status(PaymentStatus.COMPLETED)
            return True
        return False

    def get_bill(self, bill_id):
        return self.bills.get(bill_id)

# Department
class Department:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.doctors = []
        self.staff = []

    def add_doctor(self, doctor):
        self.doctors.append(doctor)

    def remove_doctor(self, doctor):
        self.doctors.remove(doctor)

    def add_staff(self, member):
        self.staff.append(member)

    def remove_staff(self, member):
        self.staff.remove(member)

    def get_doctors(self):
        return self.doctors

    def get_staff(self):
        return self.staff

# Room and Bed
class Bed:
    def __init__(self, id, patient_id=None, status=BedStatus.AVAILABLE):
        self.id = id
        self.patient_id = patient_id
        self.status = status

    def get_status(self):
        return self.status

    def update_status(self, status):
        self.status = status

    def assign_patient(self, patient_id):
        if self.get_status() == BedStatus.AVAILABLE:
            self.update_status(BedStatus.OCCUPIED)
            self.patient_id = patient_id
            return True
        return False

    def release_bed(self):
        if self.get_status() == BedStatus.OCCUPIED:
            self.update_status(BedStatus.AVAILABLE)
            self.patient_id = None
            return True
        return False

class Room:
    def __init__(self, room_no, room_type, total_beds):
        self.room_no = room_no
        self.room_type = room_type
        self.beds = [Bed(f"{room_no}_{i+1}") for i in range(total_beds)]

    def get_id(self):
        return self.room_no

    def get_available_beds(self):
        return [bed for bed in self.beds if bed.get_status() == BedStatus.AVAILABLE]

    def assign_bed(self, patient_id):
        for bed in self.beds:
            if bed.assign_patient(patient_id):
                return bed
        return None

    def release_bed(self, bed_id):
        for bed in self.beds:
            if bed.id == bed_id and bed.release_bed():
                return True
        return False

# Prescription
class Medication:
    def __init__(self, name, dosage, freq, duration):
        self.name = name
        self.dosage = dosage
        self.freq = freq
        self.duration = duration

class Prescription:
    def __init__(self, id, patient_id, doctor_id, medications, notes=''):
        self.id = id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.medications = medications
        self.notes = notes
        self.date_issued = datetime.now()

    def add_medication(self, medication):
        self.medications.append(medication)

# Hospital (Main class)
class Hospital:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance.__init__()
            return cls._instance

    def __init__(self):
        self.patients = {}
        self.doctors = {}
        self.departments = {}
        self.rooms = {}
        self.prescriptions = {}
        self.medical_records = {}

    def add_patient(self, patient):
        self.patients[patient.get_id()] = patient

    def add_doctor(self, doctor):
        self.doctors[doctor.get_id()] = doctor

    def add_department(self, department):
        self.departments[department.id] = department

    def add_room(self, room):
        self.rooms[room.get_id()] = room

    def add_medical_record(self, record):
        self.medical_records[record.patient_id] = record

    def add_prescription(self, prescription):
        self.prescriptions[prescription.id] = prescription

    def assign_room(self, patient_id, room):
        if patient_id in self.patients:
            bed = room.assign_bed(patient_id)
            if bed:
                self.rooms[room.get_id()] = room


# First, ensure required classes are already defined as per previous discussion.

# ---- Create Doctors ----
doc1 = Doctor("D001", "Dr. Alice", "alice@example.com", "1234567890", PersonRole.DOCTOR, "Cardiology")
doc2 = Doctor("D002", "Dr. Bob", "bob@example.com", "0987654321", PersonRole.DOCTOR, "Neurology")

# ---- Create Patients ----
pat1 = Patient("P001", "John Doe", "john@example.com", "5551112222", PersonRole.PATIENT, 30, "Male")
pat2 = Patient("P002", "Jane Smith", "jane@example.com", "5553334444", PersonRole.PATIENT, 25, "Female")

# ---- Create a Department and Assign Doctor ----
cardio_dept = Department("DEP001", "Cardiology")
cardio_dept.add_doctor(doc1)

# ---- Create a Room with Beds ----
room101 = Room("101", "ICU", total_beds=2)

# ---- Assign Bed to Patient ----
assigned_bed = room101.assign_bed("P001")  # Assigns bed to John

# ---- Create Prescription ----
med1 = Medication("Paracetamol", "500mg", "Twice a day", "5 days")
prescription1 = Prescription("RX001", "P001", "D001", [med1], "For fever and body ache")

# ---- Create Appointment ----
appt_manager = AppointmentManager()
appt_manager.__init__()  # Important: must initialize manually in singleton pattern

appointment1 = appt_manager.schedule("A001", pat1, doc1, "2025-04-20 10:00")

# ---- Create Bill ----
billing_manager = BillingManager()
billing_manager.__init__()

bill1 = billing_manager.generate_bill("B001", "P001", 250.00)
billing_manager.pay_bill("B001", PaymentMethod.CASH)

# ---- Initialize Hospital Singleton ----
hospital = Hospital()
hospital.__init__()

# ---- Register Data in Hospital ----
hospital.add_patient(pat1)
hospital.add_patient(pat2)
hospital.add_doctor(doc1)
hospital.add_doctor(doc2)
hospital.add_department(cardio_dept)
hospital.add_room(room101)
hospital.add_prescription(prescription1)

print("Appointment Scheduled:", appointment1 is not None)
print("Bill Paid:", bill1.get_status() == PaymentStatus.COMPLETED)
print("Available Beds:", [bed.id for bed in room101.get_available_beds()])