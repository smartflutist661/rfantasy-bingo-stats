"""
Created on Apr 9, 2023

@author: fred
"""
from typing import (
    Iterable,
    cast,
)

import pandas

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


def book_to_title_author(book: Book, separator: str) -> TitleAuthor:
    """Convert book to title/author pair"""
    title, author = book.split(separator)
    return cast(Title, title), cast(Author, author)


def books_to_title_authors(books: Iterable[Book], separator: str) -> tuple[TitleAuthor, ...]:
    """Convert iterable of books to tuple of title/author pairs"""
    return tuple(book_to_title_author(book, separator) for book in books)


def title_author_to_book(title_author_pair: TitleAuthor, separator: str) -> Book:
    """Convert title/author pair to book form"""
    return cast(Book, separator.join(str(elem) for elem in title_author_pair))


def title_authors_to_books(
    title_author_pairs: Iterable[TitleAuthor],
    separator: str,
) -> tuple[Book, ...]:
    """Convert an iterable of title/author pairs to a tuple of Books"""
    return tuple(title_author_to_book(pair, separator) for pair in title_author_pairs)


def get_unique_authors(authors: Iterable[Author]) -> frozenset[Author]:
    """Get every unique author"""
    return frozenset(authors)


def get_unique_books(
    title_author_pairs: Iterable[TitleAuthor],
    separator: str,
) -> frozenset[Book]:
    """Get every unique title/author combination"""

    for pair in title_author_pairs:
        for elem in pair:
            if separator in str(elem):
                raise ValueError("Pick a different separator")

    return frozenset(title_authors_to_books(title_author_pairs, separator))
