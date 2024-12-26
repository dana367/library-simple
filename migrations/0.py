from quart_db import Connection


async def enable_foreign_keys(connection: Connection) -> None:
    await connection.execute("PRAGMA foreign_keys = ON;")


async def migrate(connection: Connection) -> None:
    await connection.execute(
        """CREATE TABLE books (
               id INTEGER PRIMARY KEY,
               title TEXT NOT NULL,
               author TEXT NOT NULL
               
           )""",
    )

    await connection.execute(
        """CREATE TABLE readers (
               id INTEGER PRIMARY KEY,
               name TEXT NOT NULL
           )""",
    )

    await connection.execute(
        """CREATE TABLE loans (
                id INTEGER PRIMARY KEY,
                book_id INTEGER NOT NULL,
                reader_id INTEGER NOT NULL,
                loan_date TIMESTAMP NOT NULL,
                due_date TIMESTAMP NOT NULL,
                returned BOOLEAN NOT NULL DEFAULT FALSE,
                FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE RESTRICT,
                FOREIGN KEY(reader_id) REFERENCES readers(id) ON DELETE RESTRICT
        )""",
    )


async def valid_migration(connection: Connection) -> bool:
    return True
