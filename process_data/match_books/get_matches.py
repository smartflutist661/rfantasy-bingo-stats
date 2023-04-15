"""
Created on Apr 7, 2023

@author: fred
"""
import json
import traceback
from types import MappingProxyType as MAP
from typing import (
    Literal,
    Mapping,
    overload,
)

from ..data.filepaths import DUPE_RECORD_FILEPATH
from ..types.defined_types import (
    Author,
    Book,
    BookOrAuthor,
)
from ..types.recorded_states import RecordedStates
from .process_match import process_new_pair


@overload
def get_possible_matches(
    all_choices: frozenset[Author],
    match_score: int,
    rescan_non_dupes: bool,
    known_states: RecordedStates,
    ret_type: Literal["Author"],
) -> Mapping[Author, frozenset[Author]]:
    ...


@overload
def get_possible_matches(
    all_choices: frozenset[Book],
    match_score: int,
    rescan_non_dupes: bool,
    known_states: RecordedStates,
    ret_type: Literal["Book"],
) -> Mapping[Book, frozenset[Book]]:
    ...


def get_possible_matches(
    all_choices: frozenset[BookOrAuthor],
    match_score: int,
    rescan_non_dupes: bool,
    known_states: RecordedStates,
    ret_type: Literal["Book", "Author"],
) -> Mapping[Author, frozenset[Author]] | Mapping[Book, frozenset[Book]]:
    """Determine all possible misspellings for each title/author pair"""
    try:
        if ret_type == "Book":
            get_possible_book_matches(
                all_choices,  # type: ignore[arg-type]
                match_score,
                rescan_non_dupes,
                known_states,
            )
        else:
            get_possible_author_matches(
                all_choices,  # type: ignore[arg-type]
                match_score,
                rescan_non_dupes,
                known_states,
            )

    except ValueError:
        print("Saving progress and exiting")
    except Exception:  # pylint: disable=broad-exception-caught
        print("Unexpected error:")
        print(traceback.format_exc())
        print("Saving progress and exiting")
    else:
        print("All title/author pairs scanned!")

    finally:
        with DUPE_RECORD_FILEPATH.open("w", encoding="utf8") as dupe_file:
            json.dump(known_states.to_data(), dupe_file, indent=2)
        print("Updated duplicates saved.")

    if ret_type == "Book":
        return MAP({k: frozenset(v) for k, v in known_states.book_dupes.items()})
    return MAP({k: frozenset(v) for k, v in known_states.author_dupes.items()})


def get_possible_book_matches(
    books: frozenset[Book],
    match_score: int,
    rescan_non_dupes: bool,
    known_states: RecordedStates,
) -> None:
    unscanned_books = set(
        books
        - (set(known_states.book_dupes.keys()) | set().union(*(known_states.book_dupes.values())))
    )
    if rescan_non_dupes is False:
        unscanned_books -= known_states.book_non_dupes
        non_dupe_str = ""
    else:
        non_dupe_str = f", of which {len(known_states.book_non_dupes)} are being rescanned"

    print(f"Scanning {len(unscanned_books)} unscanned books{non_dupe_str}.")
    while len(unscanned_books) > 0:
        new_book = unscanned_books.pop()
        if rescan_non_dupes is True:
            # This may be replaced in the following call
            known_states.book_non_dupes.remove(new_book)

        process_new_pair(
            known_states.book_dupes,
            known_states.book_non_dupes,
            unscanned_books,
            new_book,
            match_score,
        )


def get_possible_author_matches(
    books: frozenset[Author],
    match_score: int,
    rescan_non_dupes: bool,
    known_states: RecordedStates,
) -> None:
    unscanned_authors = set(
        books
        - (
            set(known_states.author_dupes.keys())
            | set().union(*(known_states.author_dupes.values()))
        )
    )
    if rescan_non_dupes is False:
        unscanned_authors -= known_states.author_non_dupes
        non_dupe_str = ""
    else:
        non_dupe_str = f", of which {len(known_states.author_non_dupes)} are being rescanned"

    print(f"Scanning {len(unscanned_authors)} unscanned books{non_dupe_str}.")
    while len(unscanned_authors) > 0:
        new_author = unscanned_authors.pop()
        if rescan_non_dupes is True:
            # This may be replaced in the following call
            known_states.author_non_dupes.remove(new_author)

        process_new_pair(
            known_states.author_dupes,
            known_states.author_non_dupes,
            unscanned_authors,
            new_author,
            match_score,
        )
