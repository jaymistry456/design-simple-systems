from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime

# Enums
class BookStatus(Enum):
    AVAILABLE = 'Available'
    BORROWED = 'Borrowed'

class FinePolicy(Enum):
    MAX_BORROW_DAYS = 14
    FINE_PER_DAY = 10

# Book
class Book:
    def __init__(self, ISBN, title, author):
        self.ISBN = ISBN
        self.title = title
        self.author = author

    def get_ISBN(self):
        return self.ISBN

    def get_title(self):
        return self.title

    def get_author(self):
        return self.author

# BookItem
class BookItem:
    def __init__(self, book, copy_id):
        self.book = book
        self.copy_id = copy_id
        self.status = BookStatus.AVAILABLE
        self.borrowed_by = None
        self.borrow_date = None

    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status

    def set_borrower(self, user):
        self.borrowed_by = user

    def get_borrower(self):
        return self.borrowed_by

    def set_borrow_date(self, date):
        self.borrow_date = date

    def get_borrow_date(self):
        return self.borrow_date

    def get_ISBN(self):
        return self.book.get_ISBN()

    def get_title(self):
        return self.book.get_title()

    def get_author(self):
        return self.book.get_author()

# User
class User(ABC):
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name

# Member
class Member(User):
    def __init__(self, user_id, name):
        super().__init__(user_id, name)
        self.borrowed_books = []

    def borrow_book(self, library, ISBN):
        available_books = library.get_available_copies(ISBN)
        if available_books:
            book_item = available_books[0]
            book_item.set_status(BookStatus.BORROWED)
            book_item.set_borrower(self)
            book_item.set_borrow_date(datetime.now())
            self.borrowed_books.append(book_item)
            print(f"{self.name} borrowed '{book_item.get_title()}'")
        else:
            print(f"No available copies for ISBN {ISBN}")

    def return_book(self, book_item):
        if book_item in self.borrowed_books:
            fine = self.calculate_fine(book_item)
            book_item.set_status(BookStatus.AVAILABLE)
            book_item.set_borrower(None)
            book_item.set_borrow_date(None)
            self.borrowed_books.remove(book_item)
            print(f"{self.name} returned '{book_item.get_title()}'. Fine: ₹{fine}")
            return fine
        return 0

    def calculate_fine(self, book_item):
        days_borrowed = (datetime.now() - book_item.get_borrow_date()).days
        extra_days = max(0, days_borrowed - FinePolicy.MAX_BORROW_DAYS.value)
        return extra_days * FinePolicy.FINE_PER_DAY.value

# Librarian
class Librarian(User):
    def __init__(self, user_id, name):
        super().__init__(user_id, name)

    def add_book(self, library, book_item):
        library.add_book_item(book_item)

    def remove_book(self, library, book_item):
        library.remove_book_item(book_item)

# Library
class Library:
    def __init__(self):
        self.books_by_ISBN = {}

    def add_book_item(self, book_item):
        isbn = book_item.get_ISBN()
        if isbn not in self.books_by_ISBN:
            self.books_by_ISBN[isbn] = []
        self.books_by_ISBN[isbn].append(book_item)
        print(f"Added: {book_item.get_title()} - {book_item.copy_id}")

    def remove_book_item(self, book_item):
        isbn = book_item.get_ISBN()
        if isbn in self.books_by_ISBN and book_item in self.books_by_ISBN[isbn]:
            self.books_by_ISBN[isbn].remove(book_item)
            if not self.books_by_ISBN[isbn]:
                del self.books_by_ISBN[isbn]
            print(f"Removed: {book_item.get_title()} - {book_item.copy_id}")

    def get_available_copies(self, isbn=None):
        if isbn:
            return [b for b in self.books_by_ISBN.get(isbn, []) if b.get_status() == BookStatus.AVAILABLE]
        else:
            result = []
            for book_list in self.books_by_ISBN.values():
                result.extend([b for b in book_list if b.get_status() == BookStatus.AVAILABLE])
            return result

    def get_all_books(self):
        return [book for book_list in self.books_by_ISBN.values() for book in book_list]

    def search_by_title(self, title):
        return [b for b in self.get_all_books() if title.lower() in b.get_title().lower()]

    def search_by_author(self, author):
        return [b for b in self.get_all_books() if author.lower() in b.get_author().lower()]

# Main
if __name__ == '__main__':
    library = Library()
    librarian = Librarian(1, "Alice")
    member = Member(2, "Bob")

    book = Book("123", "Clean Code", "Robert C. Martin")
    book_item1 = BookItem(book, "copy1")
    book_item2 = BookItem(book, "copy2")

    librarian.add_book(library, book_item1)
    librarian.add_book(library, book_item2)

    member.borrow_book(library, "123")
    member.borrow_book(library, "123")

    # No copies should be available now
    member.borrow_book(library, "123")

    # Return one book
    member.return_book(book_item1)

    # Try borrowing again
    member.borrow_book(library, "123")