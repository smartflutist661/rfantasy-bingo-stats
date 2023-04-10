"""
Created on Apr 7, 2023

@author: fred
"""
from collections import defaultdict
from typing import Optional

from thefuzz import process  # type: ignore

from ..types.defined_types import Book
from ..types.match_choice import MatchChoice


def process_new_pair(
    dupes: defaultdict[Book, set[Book]],
    non_dupes: set[Book],
    unscanned_books: set[Book],
    book_to_process: Book,
    match_score: int,
    matches_to_remove: Optional[set[Book]] = None,
) -> None:
    """Process an unscanned title/author pair"""
    if matches_to_remove is None:
        matches_to_remove = set()

    res = process.extractOne(
        book_to_process,
        (set(dupes.keys()) | set().union(*(dupes.values()))) - matches_to_remove,
        score_cutoff=match_score,
    )
    existing_match_key = None
    if res is not None:
        title_author_match, score = res
        if title_author_match not in dupes.keys():
            existing_match_key = find_existing_match(dupes, title_author_match)
        else:
            existing_match_key = title_author_match
    else:
        res = process.extractOne(
            book_to_process,
            unscanned_books - matches_to_remove,
            score_cutoff=match_score,
        )
        if res is not None:
            title_author_match, score = res

    if res is not None:
        process_match(
            dupes=dupes,
            non_dupes=non_dupes,
            unscanned_books=unscanned_books,
            match_score=match_score,
            matched_book=title_author_match,
            book_to_process=book_to_process,
            score=score,
            matches_to_remove=matches_to_remove,
            existing_match_key=existing_match_key,
        )

    else:
        print(f"No duplicates found for {book_to_process}")
        non_dupes.add(book_to_process)


def find_existing_match(
    dupes: defaultdict[Book, set[Book]],
    title_author_match: Book,
) -> Book:
    """Determine which key to use for existing match"""

    for existing_match_key, dupe_tuples in dupes.items():
        if title_author_match in dupe_tuples:
            return existing_match_key

    raise ValueError(
        f"{title_author_match} was found in existing dupes, but matching key could not be found."
    )


def process_match(
    dupes: defaultdict[Book, set[Book]],
    non_dupes: set[Book],
    unscanned_books: set[Book],
    match_score: int,
    matched_book: Book,
    book_to_process: Book,
    score: int,
    matches_to_remove: set[Book],
    existing_match_key: Optional[Book] = None,
) -> None:
    """Process a single match, recursing if necessary"""
    matches_to_remove.add(matched_book)

    print(f"Tentative match: {book_to_process} -> {matched_book}, score {score}")
    if existing_match_key is not None:
        if existing_match_key != matched_book:
            in_val_str = f" to {existing_match_key}"
        else:
            in_val_str = ""
        print(f"{matched_book} already deduplicated{in_val_str}.")

    print("Choose the best version:")
    if existing_match_key is not None:
        print(f"[{MatchChoice.MATCH.value}] {existing_match_key}")
    else:
        print(f"[{MatchChoice.MATCH.value}] {matched_book}")
    print(f"[{MatchChoice.NEW.value}] {book_to_process}")
    print(f"[{MatchChoice.SKIP.value}] Not a match")
    print("[e] Save and exit")
    choice = MatchChoice(int(input("Selection: ")))

    if choice == MatchChoice.MATCH:
        if existing_match_key is not None:
            unify_matches(dupes, existing_match_key, book_to_process)
        else:
            unify_matches(dupes, matched_book, book_to_process)
        unscanned_books.discard(matched_book)
    elif choice == MatchChoice.NEW:
        if existing_match_key is not None:
            unify_matches(dupes, book_to_process, existing_match_key)
        else:
            unify_matches(dupes, book_to_process, matched_book)
        unscanned_books.discard(matched_book)
    else:
        # Re-process with match removed
        process_new_pair(
            dupes=dupes,
            non_dupes=non_dupes,
            unscanned_books=unscanned_books,
            book_to_process=book_to_process,
            match_score=match_score,
            matches_to_remove=matches_to_remove,
        )

    print()


def unify_matches(
    dupes: defaultdict[Book, set[Book]],
    best_match: Book,
    other_match: Book,
) -> None:
    """Unify all books associated with other match and existing key to best match"""

    # Not strictly required, but will prevent spurious prints
    if other_match in dupes.keys():
        dupes[best_match] |= dupes[other_match]
        print(f"Duplicates of {other_match} swapped to duplicates of {best_match}")

    dupes[best_match].add(other_match)
    print(f"{other_match} recorded as duplicate of {best_match}")

    if other_match in dupes.keys():
        del dupes[other_match]
