from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from quart import Quart, g
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


@app.get("/books/")
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
