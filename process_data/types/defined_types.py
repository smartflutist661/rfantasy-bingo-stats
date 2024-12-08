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
Book = NewType("Book", str)

SquareNumber = NewType("SquareNumber", str)
SquareName = NewType("SquareName", str)

Title = NewType("Title", str)
Author = NewType("Author", str)

TitleCol = NewType("TitleCol", str)
AuthorCol = NewType("AuthorCol", str)
HardModeCol = NewType("HardModeCol", str)

CardID = NewType("CardID", str)

# These are aliases for convenience
TitleAuthor = tuple[Title, Author]
TitleAuthorHMCols = tuple[TitleCol, AuthorCol, HardModeCol]

BookOrAuthor = TypeVar("BookOrAuthor", Book, Author)
