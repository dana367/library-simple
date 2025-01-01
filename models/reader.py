from dataclasses import dataclass


@dataclass
class ReaderInput:
    name: str


@dataclass
class Reader(ReaderInput):
    id: int


@dataclass
class Readers:
    readers: list[Reader]
