"""
Created on Apr 7, 2023

@author: fred
"""
from collections import defaultdict
from typing import Optional

from thefuzz import process  # type: ignore

from .types.defined_types import Book
from .types.match_choice import MatchChoice


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
    if res is not None:
        title_author_match, score = res
        print(title_author_match)
        if title_author_match in dupes.keys():
            process_existing_match(
                dupes=dupes,
                non_dupes=non_dupes,
                unscanned_books=unscanned_books,
                match_score=match_score,
                existing_match=title_author_match,
                book_to_process=book_to_process,
                score=score,
                matches_to_remove=matches_to_remove,
                existing_match_key=None,
            )
        else:
            for existing_match_key, dupe_tuples in dupes.items():
                if title_author_match in dupe_tuples:
                    process_existing_match(
                        dupes=dupes,
                        non_dupes=non_dupes,
                        unscanned_books=unscanned_books,
                        match_score=match_score,
                        existing_match=title_author_match,
                        book_to_process=book_to_process,
                        score=score,
                        existing_match_key=existing_match_key,
                        matches_to_remove=matches_to_remove,
                    )
                    break
    else:
        res = process.extractOne(
            book_to_process,
            unscanned_books - matches_to_remove,
            score_cutoff=match_score,
        )

        if res is not None:
            title_author_match, score = res if res is not None else (None, None)
            process_new_match(
                dupes=dupes,
                non_dupes=non_dupes,
                unscanned_books=unscanned_books,
                match_score=match_score,
                book_to_process=book_to_process,
                new_match=title_author_match,
                score=score,
                matches_to_remove=matches_to_remove,
            )
            unscanned_books.remove(title_author_match)
        else:
            print(f"No duplicates found for {book_to_process}")
            non_dupes.add(book_to_process)


def process_existing_match(
    dupes: defaultdict[Book, set[Book]],
    non_dupes: set[Book],
    unscanned_books: set[Book],
    match_score: int,
    existing_match: Book,
    book_to_process: Book,
    score: int,
    matches_to_remove: set[Book],
    existing_match_key: Optional[Book] = None,
) -> None:
    """If the current pair matched an existing pair, add it"""
    print(f"Tentative match: {book_to_process} -> {existing_match}, score {score}")
    if existing_match_key is not None:
        in_val_str = f" to {existing_match_key}"
    else:
        in_val_str = ""
    print(f"{existing_match} already deduplicated{in_val_str}.")
    if existing_match_key is not None:
        existing_match = existing_match_key

    print("Choose the best version:")
    print(f"[{MatchChoice.SAVE.value}] {existing_match}")
    print(f"[{MatchChoice.SWAP.value}] {book_to_process}")
    print(f"[{MatchChoice.SKIP.value}] Not a match")
    print("[e] Save and exit")
    choice = MatchChoice(int(input("Selection: ")))

    if choice == MatchChoice.SAVE:
        dupes[existing_match].add(book_to_process)
        print(f"{book_to_process} recorded as duplicate of {existing_match}")
    elif choice == MatchChoice.SWAP:
        dupes[book_to_process] |= dupes[existing_match]
        print(f"Duplicates of {existing_match} swapped to duplicates of {book_to_process}")
        dupes[book_to_process].add(existing_match)
        print(f"{existing_match} recorded as duplicate of {book_to_process}")
        del dupes[existing_match]
    else:
        # Re-process with match removed
        matches_to_remove.add(existing_match)
        process_new_pair(
            dupes=dupes,
            non_dupes=non_dupes,
            unscanned_books=unscanned_books,
            book_to_process=book_to_process,
            match_score=match_score,
            matches_to_remove=matches_to_remove,
        )

    print()


def process_new_match(
    dupes: defaultdict[Book, set[Book]],
    non_dupes: set[Book],
    unscanned_books: set[Book],
    match_score: int,
    book_to_process: Book,
    new_match: Book,
    score: int,
    matches_to_remove: set[Book],
) -> None:
    """If two previously-unseen pairs matched, add them both"""
    print(f"Tentative match found: {book_to_process} -> {new_match}, score {score}")
    print("Choose the best version:")
    print(f"[{MatchChoice.SAVE.value}] {book_to_process}")
    print(f"[{MatchChoice.SWAP.value}] {new_match}")
    print(f"[{MatchChoice.SKIP.value}] Not a match")
    print("[e] Save and exit")
    choice = MatchChoice(int(input("Selection: ")))

    if choice == MatchChoice.SAVE:
        dupes[book_to_process].add(new_match)
        print(f"{new_match} recorded as duplicate of {book_to_process}")
    elif choice == MatchChoice.SWAP:
        dupes[new_match].add(book_to_process)
        print(f"{book_to_process} recorded as duplicate of {new_match}")
    else:
        # Re-process with non-match removed
        matches_to_remove.add(new_match)
        process_new_pair(
            dupes=dupes,
            non_dupes=non_dupes,
            unscanned_books=unscanned_books,
            book_to_process=book_to_process,
            match_score=match_score,
            matches_to_remove=matches_to_remove,
        )

    print()
