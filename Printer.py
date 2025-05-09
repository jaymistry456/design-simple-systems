from typing import override

from abc import ABC, abstractmethod

class Printer(ABC):
    @abstractmethod
    def print(self, filename):
        pass

class InkJet(Printer):
    @override
    def print(self, filename):
        print('Printing file with ' + filename + ' in InkJet Printer')

class LaserJet(Printer):
    @override
    def print(self, filename):
        print('Printing file with ' + filename + ' in LasrJet Printer')

class Thermal(Printer):
    @override
    def print(self, filename):
        print('Printing file with ' + filename + ' in Thermal Printer')

class PrintJob:
    def __init__(self, filename, printer):
        self.filename = filename
        self.printer = printer

    def print(self):
        self.printer.print(self.filename)

class PrintQueue:
    def __init__(self):
        self.queue = []

    def add_job(self, print_job):
        self.queue.append(print_job)

    def process_all_jobs(self):
        while queue:
            self.process_next_job()

    def process_next_job(self):
        if not self.queue:
            print("No jobs in the queue")
        else:
            self.queue.popleft().print()