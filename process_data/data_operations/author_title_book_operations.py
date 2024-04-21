"""
Created on Apr 9, 2023

@author: fred
"""
from collections import Counter
from typing import (
    Iterable,
    cast,
)

import pandas

from ..constants import TITLE_AUTHOR_SEPARATOR
from ..data.current import ALL_TITLE_AUTHOR_HM_COLUMNS
from ..types.defined_types import (
    Author,
    Book,
    Title,
    TitleAuthor,
)


def get_all_authors(data: pandas.DataFrame) -> tuple[Author, ...]:
    """Get every author in data"""
    return tuple(author for _, author in get_all_title_author_combos(data))


def get_all_title_author_combos(data: pandas.DataFrame) -> tuple[TitleAuthor, ...]:
    """Get every title/author pair in data"""
    title_author_pairs: list[TitleAuthor] = []
    for title_col, author_col, _ in ALL_TITLE_AUTHOR_HM_COLUMNS:
        title_author_pairs.extend(
            cast(Iterable[TitleAuthor], zip(data[title_col], data[author_col]))
        )
    return tuple((title, author) for title, author in title_author_pairs if title and author)


def book_to_title_author(book: Book, separator: str = TITLE_AUTHOR_SEPARATOR) -> TitleAuthor:
    """Convert book to title/author pair"""
    title, author = book.split(separator)
    return Title(title), Author(author)


def books_to_title_authors(books: Iterable[Book]) -> tuple[TitleAuthor, ...]:
    """Convert iterable of books to tuple of title/author pairs"""
    return tuple(book_to_title_author(book) for book in books)


def title_author_to_book(title_author_pair: TitleAuthor) -> Book:
    """Convert title/author pair to book form"""
    return Book(TITLE_AUTHOR_SEPARATOR.join(str(elem) for elem in title_author_pair))


def title_authors_to_books(title_author_pairs: Iterable[TitleAuthor]) -> tuple[Book, ...]:
    """Convert an iterable of title/author pairs to a tuple of Books"""
    return tuple(title_author_to_book(pair) for pair in title_author_pairs)


def get_unique_author_counts(authors: Iterable[Author]) -> Counter[Author]:
    """Get counter for unique authors"""
    return Counter(authors)


def get_unique_authors(authors: Iterable[Author]) -> frozenset[Author]:
    """Get every unique author"""
    return frozenset(authors)


def get_unique_title_author_counts(
    title_author_pairs: Iterable[TitleAuthor],
) -> Counter[TitleAuthor]:
    """Get counter for unique title/author pairs"""
    return Counter(title_author_pairs)


def get_unique_book_counts(title_author_pairs: Iterable[TitleAuthor]) -> Counter[Book]:
    """Get counter for unique books"""
    for pair in title_author_pairs:
        for elem in pair:
            if TITLE_AUTHOR_SEPARATOR in elem:
                raise ValueError(
                    "Title/author separator appears in a raw title or author."
                    + " Select a different separator."
                )

    return Counter(title_authors_to_books(title_author_pairs))


def get_unique_books(title_author_pairs: Iterable[TitleAuthor]) -> frozenset[Book]:
    """Get every unique title/author combination"""

    return frozenset(get_unique_book_counts(title_author_pairs).keys())
