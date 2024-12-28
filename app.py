from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from quart import Quart, g, render_template
from quart_db import QuartDB
from quart_schema import QuartSchema, validate_request, validate_response

app = Quart(__name__)
QuartDB(app, url="sqlite:///database.db")
QuartSchema(app)


@dataclass
class BookInput:
    title: str
    author: str


@dataclass
class Book(BookInput):
    id: int


@app.post("/books/")
@validate_request(BookInput)
@validate_response(Book)
async def create_book(data: BookInput):
    """Create a new Book entry"""
    result = await g.connection.fetch_one(
        """INSERT INTO books (title, author) 
            VALUES (:title, :author) 
            RETURNING id, title, author""",
        {"title": data.title, "author": data.author},
    )

    return Book(**result)


@dataclass
class Books:
    books: list[Book]


@app.get("/books1/")
@validate_response(Books)
async def get_books() -> Books:
    query = """SELECT id, title, author 
                FROM books"""
    books = [Book(**row) async for row in g.connection.iterate(query)]
    return Books(books=books)


@app.get("/books/<int:id>/")
@validate_response(Book)
async def get_book_by_id(id: int) -> Book:
    """Get a book.
    Fetch a Book by its ID.
    """
    result = await g.connection.fetch_one(
        """SELECT id, title, author
            FROM books
            WHERE id = :id""",
        {"id": id},
    )
    if result is None:
        raise Exception(f"Book {id} not found")
    else:
        return Book(**result)


@app.get("/books/<string:title>/")
@validate_response(Book)
async def get_book_by_title(title: str) -> Book:
    """Get a book.
    Fetch a Book by its title.
    """
    result = await g.connection.fetch_one(
        """SELECT id, title, author
            FROM books
            WHERE title LIKE :title""",
        {"title": f"%{title}%"},
    )
    if result is None:
        raise Exception(f"Book {title} not found")
    else:
        return Book(**result)


@dataclass
class ReaderInput:
    name: str


@dataclass
class Reader(ReaderInput):
    id: int


@dataclass
class Readers:
    readers: list[Reader]


@app.post("/readers/")
@validate_request(ReaderInput)
@validate_response(Reader)
async def create_reader(data: ReaderInput):
    """Create a new Reader entry"""
    result = await g.connection.fetch_one(
        """INSERT INTO readers (name)
            VALUES (:name)
            RETURNING id, name""",
        {"name": data.name},
    )

    return Reader(**result)


@app.get("/readers/")
@validate_response(Readers)
async def get_readers() -> Reader:
    query = """SELECT id, name
                FROM readers"""
    readers = [Reader(**row) async for row in g.connection.iterate(query)]
    return Readers(readers=readers)


@app.get("/readers/<int:id>/")
@validate_response(Reader)
async def get_reader_by_id(id: int) -> Reader:
    """Get a reader.
    Fetch a Reader by its ID.
    """
    result = await g.connection.fetch_one(
        """SELECT id, name
            FROM readers
            WHERE id = :id""",
        {"id": id},
    )
    if result is None:
        raise Exception(f"Reader {id} not found")
    else:
        return Reader(**result)


@app.get("/readers/<string:name>/")
@validate_response(Reader)
async def get_reader_by_name(name: str) -> Reader:
    """Get a reader.
    Fetch a Reader by its name.
    """
    result = await g.connection.fetch_one(
        """SELECT id, name
            FROM readers
            WHERE name LIKE :name""",
        {"name": f"%{name}%"},
    )
    if result is None:
        raise Exception(f"Reader {name} not found")
    else:
        return Reader(**result)


@dataclass
class LoanInput:
    book_id: int
    reader_id: int
    loan_date: str
    due_date: str
    returned: bool

    def __post_init__(self):
        # Convert date format if needed
        if isinstance(self.loan_date, bytes):
            self.loan_date = self.loan_date.decode("utf-8")
        if isinstance(self.due_date, bytes):
            self.due_date = self.due_date.decode("utf-8")


@dataclass
class Loan(LoanInput):
    id: int


@dataclass
class Loans:
    loans: list[Loan]


@app.post("/loans/")
@validate_request(LoanInput)
@validate_response(Loan)
async def create_loan(data: LoanInput):
    """Create a new Loan entry"""

    # First check if the book is already borrowed
    existing_loan = await g.connection.fetch_one(
        """SELECT id 
           FROM loans 
           WHERE book_id = :book_id 
           AND returned = FALSE""",
        {"book_id": data.book_id},
    )

    if existing_loan is not None:
        raise Exception("This book is already borrowed and not yet returned")

    result = await g.connection.fetch_one(
        """INSERT INTO loans (book_id, reader_id, loan_date, due_date, returned)
            VALUES (:book_id, :reader_id, :loan_date, :due_date, :returned)
            RETURNING id, book_id, reader_id, loan_date, due_date, returned""",
        {
            "book_id": data.book_id,
            "reader_id": data.reader_id,
            "loan_date": data.loan_date,
            "due_date": data.due_date,
            "returned": data.returned,
        },
    )

    return Loan(**result)


@app.get("/loans/")
@validate_response(Loans)
async def get_loans() -> Loans:
    query = """SELECT id, book_id, reader_id, 
                strftime('%Y-%m-%d', loan_date) as loan_date, 
                strftime('%Y-%m-%d', due_date) as due_date, 
                returned
                FROM loans"""
    loans = [Loan(**row) async for row in g.connection.iterate(query)]
    return Loans(loans=loans)


@app.get("/loans/<int:id>/")
@validate_response(Loan)
async def get_loan_by_id(id: int) -> Loan:
    """Get a loan.
    Fetch a Loan by its ID.
    """
    result = await g.connection.fetch_one(
        """SELECT id, book_id, reader_id,
                strftime('%Y-%m-%d', loan_date) as loan_date,
                strftime('%Y-%m-%d', due_date) as due_date,
                returned
            FROM loans
            WHERE id = :id""",
        {"id": id},
    )
    if result is None:
        raise Exception(f"Loan {id} not found")
    else:
        return Loan(**result)


@dataclass
class BorrowedBook:
    book_id: int
    title: str
    author: str
    loan_date: str
    due_date: str
    returned: bool


@dataclass
class ReaderWithBooks:
    id: int
    name: str
    borrowed_books: list[BorrowedBook]


@app.get("/readers/<int:reader_id>/books/")
@validate_response(ReaderWithBooks)
async def get_reader_with_books(reader_id: int) -> ReaderWithBooks:
    """Get a reader and their borrowed books.
    Fetch a Reader and all books they have borrowed.
    """
    # First get reader details
    reader = await g.connection.fetch_one(
        """SELECT id, name
           FROM readers
           WHERE id = :reader_id""",
        {"reader_id": reader_id},
    )

    if reader is None:
        raise Exception(f"Reader {reader_id} not found")

    # Then get all books borrowed by this reader
    query = """
        SELECT 
            b.id as book_id,
            b.title,
            b.author,
            strftime('%d-%m-%Y', l.loan_date) as loan_date,
            strftime('%d-%m-%Y', l.due_date) as due_date,
            l.returned
        FROM loans l
        JOIN books b ON l.book_id = b.id
        WHERE l.reader_id = :reader_id
        ORDER BY l.loan_date DESC
    """

    borrowed_books = [
        BorrowedBook(**row)
        async for row in g.connection.iterate(query, {"reader_id": reader_id})
    ]

    return ReaderWithBooks(
        id=reader["id"], name=reader["name"], borrowed_books=borrowed_books
    )


@dataclass
class ReturnBookInput:
    loan_id: int
    return_date: str


@app.post("/loans/<int:loan_id>/return/")
@validate_request(ReturnBookInput)
@validate_response(Loan)
async def return_book(loan_id: int, data: ReturnBookInput):
    """Return a borrowed book"""

    # First fetch the loan details before deleting
    existing_loan = await g.connection.fetch_one(
        """SELECT id, book_id, reader_id,
           strftime('%Y-%m-%d', loan_date) as loan_date,
           strftime('%Y-%m-%d', due_date) as due_date,
           returned
           FROM loans 
           WHERE id = :loan_id 
           AND returned = FALSE""",
        {"loan_id": loan_id},
    )

    if existing_loan is None:
        raise Exception("Loan not found or book already returned")

    # Delete the loan record
    await g.connection.execute(
        """DELETE FROM loans 
           WHERE id = :loan_id""",
        {"loan_id": loan_id},
    )

    # Return the loan details that were just deleted
    return Loan(**existing_loan)


@app.get("/")
async def home():
    # Get counts
    book_count = await g.connection.fetch_val("SELECT COUNT(*) FROM books")
    reader_count = await g.connection.fetch_val("SELECT COUNT(*) FROM readers")
    active_loans_count = await g.connection.fetch_val(
        "SELECT COUNT(*) FROM loans WHERE returned = FALSE"
    )

    # Get recent loans
    recent_loans_query = """
        SELECT 
            b.title as book_title,
            r.name as reader_name,
            strftime('%d-%m-%Y', l.due_date) as due_date
        FROM loans l
        JOIN books b ON l.book_id = b.id
        JOIN readers r ON l.reader_id = r.id
        WHERE l.returned = FALSE
        ORDER BY l.loan_date DESC
        LIMIT 5
    """
    recent_loans = [dict(row) async for row in g.connection.iterate(recent_loans_query)]

    # Get popular books
    popular_books_query = """
        SELECT 
            b.title,
            b.author,
            COUNT(*) as borrow_count
        FROM loans l
        JOIN books b ON l.book_id = b.id
        GROUP BY b.id
        ORDER BY borrow_count DESC
        LIMIT 5
    """
    popular_books = [
        dict(row) async for row in g.connection.iterate(popular_books_query)
    ]

    return await render_template(
        "home.html",
        book_count=book_count,
        reader_count=reader_count,
        active_loans_count=active_loans_count,
        recent_loans=recent_loans,
        popular_books=popular_books,
    )


@app.get("/books/")
async def books_page():
    # Get all books with their loan status
    query = """
        SELECT 
            b.id,
            b.title,
            b.author,
            EXISTS (
                SELECT 1 
                FROM loans l 
                WHERE l.book_id = b.id 
                AND l.returned = FALSE
            ) as is_borrowed
        FROM books b
        ORDER BY b.title
    """
    books = [dict(row) async for row in g.connection.iterate(query)]

    # Get all readers for the loan form
    readers_query = "SELECT id, name FROM readers ORDER BY name"
    readers = [dict(row) async for row in g.connection.iterate(readers_query)]

    return await render_template("display_books.html", books=books, readers=readers)
