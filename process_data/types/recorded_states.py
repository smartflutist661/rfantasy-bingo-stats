"""
Created on Apr 7, 2023

@author: fred
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import (
    dataclass,
    fields,
)
from types import MappingProxyType as MAP
from typing import (
    AbstractSet,
    Any,
    Mapping,
    cast,
)

from ..data.current import CUSTOM_SEPARATOR
from ..match_books.process_match import find_existing_match
from .defined_types import (
    Author,
    Book,
    BookOrAuthor,
)
from .match_choice import MatchChoice
from .utils import to_data


@dataclass(frozen=True)
class RecordedStates:
    """Known duplicate title/author pairs and likely non-duplicate title/author pairs"""

    author_dupes: defaultdict[Author, set[Author]]
    book_dupes: defaultdict[Book, set[Book]]
    book_separator: str = CUSTOM_SEPARATOR

    # @property
    # def author_non_dupes(self) -> frozenset[Author]:
    #     """Get keys with no """
    #     return frozenset(
    #         {
    #             author
    #             for author, author_dedupes in self.author_dupes.items()
    #             if len(author_dedupes) == 0
    #         }
    #     )
    #
    # @property
    # def book_non_dupes(self) -> frozenset[Book]:
    #     return frozenset(
    #         {book for book, book_dedupes in self.book_dupes.items() if len(book_dedupes) == 0}
    #     )

    @classmethod
    def from_data(cls, data: Any) -> RecordedStates:
        """Restore from JSON data"""

        # Should try to handle duplicated keys... this does not
        book_dupes: defaultdict[Book, set[Book]] = defaultdict(
            set,
            {key: {cast(Book, str(v)) for v in val} for key, val in data["book_dupes"].items()},
        )

        book_non_dupes = data.get("book_non_dupes")
        if book_non_dupes is not None:
            for book in book_non_dupes:
                book_dupes[cast(Book, str(book))] = set()

        handle_overlaps(book_dupes)

        author_dupes: defaultdict[Author, set[Author]] = defaultdict(
            set,
            {
                key: {cast(Author, str(v)) for v in val}
                for key, val in data["author_dupes"].items()
            },
        )

        author_non_dupes = data.get("author_non_dupes")
        if author_non_dupes is not None:
            for author in author_non_dupes:
                author_dupes[cast(Author, str(author))] = set()

        handle_overlaps(author_dupes)

        return cls(
            author_dupes=author_dupes,
            book_dupes=book_dupes,
            book_separator=str(data["book_separator"]),
        )

    def to_data(self) -> dict[str, Any]:
        """Write to JSON data"""
        out = {}
        for key, val in {field.name: getattr(self, field.name) for field in fields(self)}.items():
            out[key] = to_data(val)
        return out

    @classmethod
    def empty(cls, book_separator: str = CUSTOM_SEPARATOR) -> RecordedStates:
        """Create an empty RecordedStates"""
        return cls(
            author_dupes=defaultdict(set),
            book_dupes=defaultdict(set),
            book_separator=book_separator,
        )


def handle_overlaps(dupes: defaultdict[BookOrAuthor, set[BookOrAuthor]]) -> None:
    """Handle overlapping duplicate key/val and val/val pairs"""
    # Check for key/value overlaps
    overlapping_dedupes = set(dupes.keys()) & set().union(*dupes.values())
    while len(overlapping_dedupes) > 0:
        unify_key_value_overlaps(dupes, overlapping_dedupes)
        overlapping_dedupes = set(dupes.keys()) & set().union(*dupes.values())

    # Check for value/value overlaps
    all_overlaps = get_all_value_overlaps(dupes)
    while len(all_overlaps) > 0:
        unify_overlapped_values(dupes, all_overlaps)
        all_overlaps = get_all_value_overlaps(dupes)


def get_all_value_overlaps(
    dupes: Mapping[BookOrAuthor, AbstractSet[BookOrAuthor]]
) -> Mapping[tuple[BookOrAuthor, BookOrAuthor], AbstractSet[BookOrAuthor]]:
    """Get overlaps in value fields"""
    all_overlaps = {}
    for dupe_key_num, (dupe_key_1, dupe_vals_1) in enumerate(tuple(dupes.items())):
        for dupe_key_2, dupe_vals_2 in tuple(dupes.items())[dupe_key_num + 1 :]:
            overlaps = dupe_vals_1 & dupe_vals_2
            if len(overlaps) > 0:
                all_overlaps[(dupe_key_1, dupe_key_2)] = overlaps

    return MAP(all_overlaps)


def unify_overlapped_values(
    dupes: defaultdict[BookOrAuthor, set[BookOrAuthor]],
    all_overlaps: Mapping[tuple[BookOrAuthor, BookOrAuthor], AbstractSet[BookOrAuthor]],
) -> None:
    """Unify books that are duplicated as values"""
    for (dupe_key_1, dupe_key_2), overlaps in all_overlaps.items():
        print(f"{overlaps} are saved as duplicates for both {dupe_key_1} and {dupe_key_2}")

        print("Choose the best version:")
        print(f"[{MatchChoice.MATCH.value}] {dupe_key_1}")
        print(f"[{MatchChoice.NEW.value}] {dupe_key_2}")
        choice = MatchChoice(int(input("Selection: ")))

        if choice == MatchChoice.MATCH:
            best = dupe_key_1
            remove = dupe_key_2
        else:
            best = dupe_key_1
            remove = dupe_key_2

        dupes[best] |= dupes[remove]
        print(f"Duplicates of {remove} swapped to duplicates of {best}")
        dupes[best].add(remove)
        print(f"{remove} recorded as duplicate of {best}")
        del dupes[remove]


def unify_key_value_overlaps(
    dupes: defaultdict[BookOrAuthor, set[BookOrAuthor]],
    overlapping_dedupes: set[BookOrAuthor],
) -> None:
    """Unify books that are duplicated as keys and values"""
    for overlap in overlapping_dedupes:
        existing_match_key = find_existing_match(dupes, overlap)
        if overlap == existing_match_key:
            dupes[existing_match_key].remove(overlap)
        else:
            print(f"{overlap} is a corrected version and a duplicate for {existing_match_key}")

            print("Choose the best version:")
            print(f"[{MatchChoice.MATCH.value}] {existing_match_key}")
            print(f"[{MatchChoice.NEW.value}] {overlap}")
            choice = MatchChoice(int(input("Selection: ")))

            if choice == MatchChoice.MATCH:
                best = existing_match_key
                remove = overlap
            else:
                best = overlap
                remove = existing_match_key

            dupes[best] |= dupes[remove]
            print(f"Duplicates of {remove} swapped to duplicates of {best}")
            dupes[best].add(remove)
            print(f"{remove} recorded as duplicate of {best}")
            del dupes[remove]
