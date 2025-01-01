from extentions import app
from models.book import Book, BookInput, Books
from quart import Blueprint, g, render_template
from quart_schema import validate_request, validate_response

blueprint = Blueprint("books", __name__)


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
