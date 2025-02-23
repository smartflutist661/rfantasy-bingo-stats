from collections.abc import Mapping
from typing import AbstractSet

from rfantasy_bingo_stats.constants import (
    AUTHOR_INFO_FILEPATH,
    BOOK_INFO_FILEPATH,
    DUPE_RECORD_FILEPATH,
)
from rfantasy_bingo_stats.data_operations.update_data import comma_separate_authors
from rfantasy_bingo_stats.logger import LOGGER
from rfantasy_bingo_stats.match_books.get_matches import get_possible_matches
from rfantasy_bingo_stats.models.author_info import (
    AuthorInfo,
    AuthorInfoAdapter,
)
from rfantasy_bingo_stats.models.book_info import (
    BookInfo,
    BookInfoAdapter,
)
from rfantasy_bingo_stats.models.defined_types import (
    Author,
    Book,
)
from rfantasy_bingo_stats.models.recorded_ignores import RecordedIgnores
from rfantasy_bingo_stats.models.recorded_states import RecordedDupes


def normalize_authors(
    unique_authors: AbstractSet[Author],
    match_score: int,
    rescan_non_dupes: bool,
    recorded_dupes: RecordedDupes,
    recorded_ignores: RecordedIgnores,
    skip_authors: bool,
) -> None:
    """Normalize book titles and authors"""

    LOGGER.info(
        f"Starting with {len(unique_authors)} unique authors.\n\n"
        + "Processing possible misspellings."
        + " You may hit ctrl+C at any point to exit, or enter `e` at the prompt."
        + " Progress will be saved.\n\nCurrent canonical versions are marked with {CK}\n"
    )

    if not skip_authors:
        get_possible_matches(
            unique_authors,
            match_score,
            rescan_non_dupes,
            recorded_dupes,
            recorded_ignores,
            "Author",
        )

    comma_separate_authors(recorded_dupes)

    if not skip_authors:
        unique_single_authors = frozenset(
            {
                Author(single_author)
                for author in recorded_dupes.author_dupes.keys()
                for single_author in author.split(", ")
            }
        )

        get_possible_matches(
            unique_single_authors | unique_authors,
            match_score,
            rescan_non_dupes,
            recorded_dupes,
            recorded_ignores,
            "Author",
        )

    author_dedupe_map = recorded_dupes.get_author_dedupe_map()

    # Correct multi-author groups
    for author in tuple(recorded_dupes.author_dupes.keys()):
        final_author = author
        for single_author in author.split(", "):
            single_author = Author(single_author)
            updated_single_author = author_dedupe_map.get(single_author, single_author)
            final_author = Author(final_author.replace(single_author, updated_single_author))
        if final_author != author:
            recorded_dupes.author_dupes[final_author] |= recorded_dupes.author_dupes[author]
            recorded_dupes.author_dupes[final_author].add(author)
            del recorded_dupes.author_dupes[author]

    with DUPE_RECORD_FILEPATH.open("w", encoding="utf8") as dupe_file:
        dupe_file.write(recorded_dupes.model_dump_json(indent=2))


def normalize_books(
    unique_books: AbstractSet[Book],
    match_score: int,
    rescan_non_dupes: bool,
    recorded_dupes: RecordedDupes,
    recorded_ignores: RecordedIgnores,
) -> None:

    LOGGER.info(
        f"Starting with {len(unique_books)} unique books.\n\n"
        + "Processing possible misspellings."
        + " You may hit ctrl+C at any point to exit, or enter `e` at the prompt."
        + " Progress will be saved.\n"
    )

    get_possible_matches(
        unique_books,
        match_score,
        rescan_non_dupes,
        recorded_dupes,
        recorded_ignores,
        "Book",
    )


def update_author_info_map(recorded_duplicates: RecordedDupes) -> Mapping[Author, AuthorInfo]:
    """If an author in the current info map has been corrected, swap the info key"""
    with AUTHOR_INFO_FILEPATH.open("r", encoding="utf8") as author_info_file:
        author_data = AuthorInfoAdapter.validate_json(author_info_file.read())

    # Correct author info keys as necessary
    author_dedupe_map = recorded_duplicates.get_author_dedupe_map()
    author_data = {
        author_dedupe_map.get(author, author): author_info
        for author, author_info in author_data.items()
    }

    with AUTHOR_INFO_FILEPATH.open("w", encoding="utf8") as author_info_file:
        author_info_file.write(AuthorInfoAdapter.dump_json(author_data, indent=2).decode("utf8"))

    return author_data


def update_book_info_map(recorded_duplicates: RecordedDupes) -> Mapping[Book, BookInfo]:
    """If a book in the current info map has been corrected, swap the info key"""
    with BOOK_INFO_FILEPATH.open("r", encoding="utf8") as book_info_file:
        book_data = BookInfoAdapter.validate_json(book_info_file.read())

    # Correct author info keys as necessary
    book_dedupe_map = recorded_duplicates.get_book_dedupe_map()
    book_data = {
        book_dedupe_map.get(book, book): book_info for book, book_info in book_data.items()
    }

    with BOOK_INFO_FILEPATH.open("w", encoding="utf8") as book_info_file:
        book_info_file.write(BookInfoAdapter.dump_json(book_data, indent=2).decode("utf8"))

    return book_data
