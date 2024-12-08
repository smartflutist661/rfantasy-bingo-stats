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
from .defined_types import Book
from .match_choice import MatchChoice
from .utils import to_data


@dataclass(frozen=True)
class RecordedStates:
    """Known duplicate title/author pairs and likely non-duplicate title/author pairs"""

    dupes: defaultdict[Book, set[Book]]
    non_dupes: set[Book]
    book_separator: str = CUSTOM_SEPARATOR

    @classmethod
    def from_data(cls, data: Any) -> RecordedStates:
        """Restore from JSON data"""

        # Handle duplicated keys
        dupes: defaultdict[Book, set[Book]] = defaultdict(set)
        for key, val in data["dupes"].items():
            dupes[cast(Book, str(key))] |= {cast(Book, str(v)) for v in val}

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

        return cls(
            dupes=dupes,
            non_dupes={cast(Book, str(val)) for val in data["non_dupes"]},
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
            dupes=defaultdict(set),
            non_dupes=set(),
            book_separator=book_separator,
        )


def get_all_value_overlaps(
    dupes: Mapping[Book, AbstractSet[Book]]
) -> Mapping[tuple[Book, Book], AbstractSet[Book]]:
    """Get overlaps in value fields"""
    all_overlaps = {}
    for dupe_key_num, (dupe_key_1, dupe_vals_1) in enumerate(tuple(dupes.items())):
        for dupe_key_2, dupe_vals_2 in tuple(dupes.items())[dupe_key_num + 1 :]:
            overlaps = dupe_vals_1 & dupe_vals_2
            if len(overlaps) > 0:
                all_overlaps[(dupe_key_1, dupe_key_2)] = overlaps

    return MAP(all_overlaps)


def unify_overlapped_values(
    dupes: defaultdict[Book, set[Book]],
    all_overlaps: Mapping[tuple[Book, Book], AbstractSet[Book]],
) -> None:
    """Unify books that are duplicated as values"""
    for (dupe_key_1, dupe_key_2), overlaps in all_overlaps.items():
        print(f"{overlaps} are saved as duplicates for both {dupe_key_1} and {dupe_key_2}")

        print("Choose the best version:")
        print(f"[{MatchChoice.SAVE.value}] {dupe_key_1}")
        print(f"[{MatchChoice.SWAP.value}] {dupe_key_2}")
        choice = MatchChoice(int(input("Selection: ")))

        if choice == MatchChoice.SAVE:
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
    dupes: defaultdict[Book, set[Book]], overlapping_dedupes: set[Book]
) -> None:
    """Unify books that are duplicated as keys and values"""
    for overlap in overlapping_dedupes:
        existing_match_key = find_existing_match(dupes, overlap)
        print(f"{overlap} is a corrected version and a duplicate for {existing_match_key}")

        print("Choose the best version:")
        print(f"[{MatchChoice.SAVE.value}] {existing_match_key}")
        print(f"[{MatchChoice.SWAP.value}] {overlap}")
        choice = MatchChoice(int(input("Selection: ")))

        if choice == MatchChoice.SAVE:
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
