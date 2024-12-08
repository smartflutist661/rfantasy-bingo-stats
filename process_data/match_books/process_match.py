"""
Created on Apr 7, 2023

@author: fred
"""
from collections import defaultdict
from typing import (
    Optional,
    cast,
)

from thefuzz import process  # type: ignore

from ..types.defined_types import Book


def process_new_pair(
    dupes: defaultdict[Book, set[Book]],
    non_dupes: set[Book],
    unscanned_books: set[Book],
    book_to_process: Book,
    match_score: int,
) -> None:
    """Process an unscanned title/author pair"""

    dedupes = set().union(*(dupes.values()))
    all_choices = set(dupes.keys()) | dedupes | unscanned_books

    print()
    results = process.extractBests(
        query=book_to_process,
        choices=all_choices,
        score_cutoff=match_score,
        limit=len(all_choices),
    )
    existing_match_keys = set()
    possible_matches = {book_to_process}
    if results is not None and len(results) > 0:
        print(f"Matching {book_to_process}:")
        for book_match, _ in results:
            if book_match in dedupes:
                existing_match_keys.add(find_existing_match(dupes, book_match))
            elif book_match in dupes.keys():
                existing_match_keys.add(book_match)
            else:
                possible_matches.add(book_match)

        all_match_choices = possible_matches | existing_match_keys

        best_match = get_best_match(matched_books=all_match_choices)

        if best_match in all_choices - all_match_choices:
            raise KeyError(
                "Manual best match that overlaps with non-matches not currently handled."
            )

    else:
        best_match = None

    if best_match is None:
        print(f"No duplicates found for {book_to_process}")
        non_dupes.add(book_to_process)
    else:
        # Intersection discards matches removed in `get_best_match`
        possible_matches &= all_match_choices
        existing_match_keys &= all_match_choices

        # This discards the match chosen from one of these two sets
        possible_matches.discard(best_match)
        existing_match_keys.discard(best_match)

        unify_matches(
            dupes=dupes,
            best_match=best_match,
            other_matches=frozenset(possible_matches),
            existing_match_keys=frozenset(existing_match_keys),
        )

        # Drop matches that were just unified
        unscanned_books -= possible_matches
        unscanned_books -= existing_match_keys
        unscanned_books.discard(best_match)


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


def get_best_match(matched_books: set[Book]) -> Optional[Book]:
    """Process all possible matches for a book"""

    choice = "d"
    while choice == "d":
        match_choices = tuple(matched_books)
        print("Choose the best version:")
        for choice_num, match_choice in enumerate(match_choices):
            print(f"[{choice_num}] {match_choice}")
        print()
        print("[r] Remove one or more matches")
        print("[c] Enter a better version of all")
        print("[e] Save and exit")
        choice = input("Selection: ")
        if choice == "r":
            while len(matched_books) > 1 and choice != "d":
                choice = input("Match to remove ([d] for done): ")
                if choice != "d":
                    matched_books.remove(match_choices[int(choice)])
        elif choice == "c":
            return cast(Book, input("Enter a better version, in the format 'title /// author':\n"))

    if len(matched_books) > 1:
        return match_choices[int(choice)]
    return None


def unify_matches(
    dupes: defaultdict[Book, set[Book]],
    best_match: Book,
    other_matches: frozenset[Book],
    existing_match_keys: frozenset[Book],
) -> None:
    """Unify all books associated with other match and existing key to best match"""

    for existing_key in existing_match_keys:
        dupes[best_match] |= dupes[existing_key]
        dupes[best_match].add(existing_key)
        del dupes[existing_key]
        print(f"Duplicates of {existing_key} swapped to duplicates of {best_match}")

    dupes[best_match] |= other_matches
    print(
        f"{', '.join(other_matches)} recorded as duplicate{'s'*(len(other_matches) > 1)} of {best_match}"
    )
