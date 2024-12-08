"""
Created on Apr 7, 2023

@author: fred
"""

from typing import (
    NewType,
    TypeVar,
)


# The purpose of these types is to make each kind of string distinct
# More complex logic can be implemented as a class, if necessary
# Inheritance employed for runtime-checkability
class Book(str):
    pass


class Title(str):
    pass


class Author(str):
    pass


class SquareName(str):
    pass


BingoName = NewType("BingoName", str)

TitleCol = NewType("TitleCol", str)
AuthorCol = NewType("AuthorCol", str)
HardModeCol = NewType("HardModeCol", str)

CardID = NewType("CardID", str)

DistName = NewType("DistName", str)

# These are aliases for convenience
TitleAuthor = tuple[Title, Author]
TitleAuthorHMCols = tuple[TitleCol, AuthorCol, HardModeCol]

BookOrAuthor = TypeVar("BookOrAuthor", Book, Author)
