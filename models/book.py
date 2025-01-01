from dataclasses import dataclass


@dataclass
class BookInput:
    title: str
    author: str


@dataclass
class Book(BookInput):
    id: int


@dataclass
class Books:
    books: list[Book]
