from typing import (
    AbstractSet,
    Literal,
    Mapping,
    overload,
)

from rfantasy_bingo_stats.constants import (
    DUPE_RECORD_FILEPATH,
    IGNORED_RECORD_FILEPATH,
)
from rfantasy_bingo_stats.logger import LOGGER
from rfantasy_bingo_stats.match_books.process_match import (
    find_existing_match,
    process_new_pair,
)
from rfantasy_bingo_stats.models.defined_types import (
    Author,
    Book,
    BookOrAuthor,
)
from rfantasy_bingo_stats.models.recorded_ignores import RecordedIgnores
from rfantasy_bingo_stats.models.recorded_states import RecordedDupes


@overload
def get_possible_matches(
    all_choices: AbstractSet[Author],
    match_score: int,
    rescan_keys: bool,
    known_states: RecordedDupes,
    known_ignores: RecordedIgnores,
    ret_type: Literal["Author"],
) -> None: ...


@overload
def get_possible_matches(
    all_choices: AbstractSet[Book],
    match_score: int,
    rescan_keys: bool,
    known_states: RecordedDupes,
    known_ignores: RecordedIgnores,
    ret_type: Literal["Book"],
) -> None: ...


def get_possible_matches(
    all_choices: AbstractSet[BookOrAuthor],
    match_score: int,
    rescan_keys: bool,
    known_states: RecordedDupes,
    known_ignores: RecordedIgnores,
    ret_type: Literal["Book", "Author"],
) -> None:
    """Determine all possible misspellings for each author or book"""
    try:
        if ret_type == "Book":
            get_possible_book_matches(
                all_choices,  # type: ignore[arg-type]
                match_score,
                rescan_keys,
                known_states,
                known_ignores,
            )
        else:
            get_possible_author_matches(
                all_choices,  # type: ignore[arg-type]
                match_score,
                rescan_keys,
                known_states,
                known_ignores,
            )

    except ValueError:
        LOGGER.info("Saving progress and exiting")
    except Exception:
        LOGGER.error("Unexpected error. Saving progress and exiting.")
        # Note `finally` is executed before `raise`ing
        raise
    else:
        LOGGER.info(f"All {ret_type}s scanned!")

    finally:
        with DUPE_RECORD_FILEPATH.open("w", encoding="utf8") as dupe_file:
            dupe_file.write(known_states.model_dump_json(indent=2))
        with IGNORED_RECORD_FILEPATH.open("w", encoding="utf8") as ignore_file:
            ignore_file.write(known_ignores.model_dump_json(indent=2))
        LOGGER.info("Updated duplicates saved.")


def get_possible_book_matches(
    books: AbstractSet[Book],
    match_score: int,
    rescan_keys: bool,
    known_states: RecordedDupes,
    known_ignores: RecordedIgnores,
) -> None:
    """Get possible matches for un-matched books"""

    unscanned_books = set(
        books
        - (set(known_states.book_dupes.keys()) | set().union(*(known_states.book_dupes.values())))
    )

    if rescan_keys is False:
        non_dupe_str = ""
    else:
        best_books = set(known_states.book_dupes.keys())
        unscanned_books |= best_books
        non_dupe_str = f", of which {len(best_books)} are being rescanned"

    total_to_scan = len(unscanned_books)
    count = 0
    LOGGER.info(f"Scanning {total_to_scan} unscanned books{non_dupe_str}.")
    while len(unscanned_books) > 0:
        count += 1
        print(f"\n{count}/{total_to_scan}")  # noqa: T201
        new_book = unscanned_books.pop()

        process_new_pair(
            known_states.book_dupes,
            known_ignores.ignored_book_dupes,
            unscanned_books,
            new_book,
            match_score,
        )


def get_possible_author_matches(
    authors: AbstractSet[Author],
    match_score: int,
    rescan_keys: bool,
    known_states: RecordedDupes,
    known_ignores: RecordedIgnores,
) -> None:
    """Get possible matches for un-checked authors"""
    unscanned_authors = set(
        authors
        - (
            set(known_states.author_dupes.keys())
            | set().union(*(known_states.author_dupes.values()))
        )
    )
    if rescan_keys is False:
        non_dupe_str = ""
    else:
        best_authors = set(known_states.author_dupes.keys())
        unscanned_authors |= best_authors
        non_dupe_str = f", of which {len(best_authors)} are being rescanned"

    total_to_scan = len(unscanned_authors)
    count = 0
    LOGGER.info(f"Scanning {len(unscanned_authors)} unscanned authors{non_dupe_str}.")
    while len(unscanned_authors) > 0:
        count += 1
        print(f"\n{count}/{total_to_scan}")  # noqa: T201
        new_author = unscanned_authors.pop()

        process_new_pair(
            known_states.author_dupes,
            known_ignores.ignored_author_dupes,
            unscanned_authors,
            new_author,
            match_score,
        )


def update_dedupes_from_authors(
    recorded_states: RecordedDupes,
    author_dedupes: Mapping[Book, AbstractSet[Book]],
) -> None:
    """Take recorded Books for each deduped Author, and record to target Book"""
    for author_dedupe, author_dupes in author_dedupes.items():
        if author_dedupe in recorded_states.book_dupes.keys():
            recorded_states.book_dupes[author_dedupe] |= author_dupes
        elif author_dedupe in set().union(*recorded_states.book_dupes.values()):
            existing_key = find_existing_match(recorded_states.book_dupes, author_dedupe)
            recorded_states.book_dupes[existing_key] |= author_dupes

    with DUPE_RECORD_FILEPATH.open("w", encoding="utf8") as dupe_file:
        dupe_file.write(recorded_states.model_dump_json(indent=2))
    LOGGER.info("Updated duplicates saved.")
