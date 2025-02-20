from collections import defaultdict
from types import MappingProxyType as MAP
from typing import (
    AbstractSet,
    Mapping,
    Self,
)

from pydantic.functional_validators import (
    field_validator,
    model_validator,
)
from pydantic.main import BaseModel

from rfantasy_bingo_stats.constants import TITLE_AUTHOR_SEPARATOR
from rfantasy_bingo_stats.data_operations.author_title_book_operations import (
    book_to_title_author,
    title_author_to_book,
)
from rfantasy_bingo_stats.logger import LOGGER
from rfantasy_bingo_stats.match_books.process_match import find_existing_match
from rfantasy_bingo_stats.models.defined_types import (
    Author,
    Book,
    BookOrAuthor,
    SortedDefaultdict,
    SortedSet,
)
from rfantasy_bingo_stats.models.match_choice import MatchChoice


class RecordedDupes(BaseModel):
    """Known duplicate title/author pairs and likely non-duplicate title/author pairs"""

    author_dupes: SortedDefaultdict[Author, SortedSet[Author]]
    book_dupes: SortedDefaultdict[Book, SortedSet[Book]]
    # Specifically for deserialization checks if the separator needs to change
    title_author_separator: str = TITLE_AUTHOR_SEPARATOR

    @field_validator("author_dupes", "book_dupes")
    @classmethod
    def dedupe(
        cls,
        data: defaultdict[BookOrAuthor, set[BookOrAuthor]],
    ) -> defaultdict[BookOrAuthor, set[BookOrAuthor]]:
        handle_overlaps(data)
        return data

    @model_validator(mode="after")
    def validate_separator(self) -> Self:
        """Override default init to handle overlaps and changes in separator"""
        if self.title_author_separator != TITLE_AUTHOR_SEPARATOR:
            LOGGER.warning(
                "Title/author separator has changed since last serialization."
                + " Updating old data to use the new separator."
            )

            new_book_dupes: defaultdict[Book, set[Book]] = defaultdict(set)
            for book_dupe_key, book_dupe_vals in self.book_dupes.items():
                new_book_key = convert_title_author_separator(
                    book_dupe_key, self.title_author_separator
                )
                new_book_dupes[new_book_key] = set()
                for book in book_dupe_vals:
                    new_book_dupes[new_book_key].add(
                        convert_title_author_separator(book, self.title_author_separator)
                    )

            self.book_dupes = new_book_dupes
            self.title_author_separator = TITLE_AUTHOR_SEPARATOR

        return self

    def get_book_dedupe_map(self) -> Mapping[Book, Book]:
        """Reverse the book dupes to get bad values as keys"""
        return MAP(
            {
                dedupe_book: primary_book
                for primary_book, dedupe_books in self.book_dupes.items()
                for dedupe_book in dedupe_books
            }
        )

    def get_author_dedupe_map(self) -> Mapping[Author, Author]:
        """Reverse the author dupes to get bad values as keys"""
        return MAP(
            {
                dedupe_author: primary_author
                for primary_author, dedupe_authors in self.author_dupes.items()
                for dedupe_author in dedupe_authors
            }
        )


def convert_title_author_separator(book: Book, old_separator: str) -> Book:
    title_author = book_to_title_author(book, old_separator)
    for elem in title_author:
        if TITLE_AUTHOR_SEPARATOR in elem:
            raise ValueError(
                "New title/author separator appears in old data. Try a different separator."
            )
    return title_author_to_book(title_author)


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
    dupes: Mapping[BookOrAuthor, AbstractSet[BookOrAuthor]],
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
        choice_str = [f"{overlaps} are saved as duplicates for both {dupe_key_1} and {dupe_key_2}"]

        choice_str.append("Choose the best version:")
        choice_str.append(f"[{MatchChoice.MATCH.value}] {dupe_key_1}")
        choice_str.append(f"[{MatchChoice.NEW.value}] {dupe_key_2}")
        choice_str.append("Selection: ")
        choice = MatchChoice(int(input("\n".join(choice_str))))

        if choice == MatchChoice.MATCH:
            best = dupe_key_1
            remove = dupe_key_2
        else:
            best = dupe_key_1
            remove = dupe_key_2

        dupes[best] |= dupes[remove]
        LOGGER.info(f"Duplicates of {remove} swapped to duplicates of {best}")
        dupes[best].add(remove)
        LOGGER.info(f"{remove} recorded as duplicate of {best}")
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
            choice_str = [
                f"{overlap} is a corrected version and a duplicate for {existing_match_key}"
            ]

            choice_str.append("Choose the best version:")
            choice_str.append(f"[{MatchChoice.MATCH.value}] {existing_match_key}")
            choice_str.append(f"[{MatchChoice.NEW.value}] {overlap}")
            choice_str.append("Selection: ")
            choice = MatchChoice(int(input("\n".join(choice_str))))

            if choice == MatchChoice.MATCH:
                best = existing_match_key
                remove = overlap
            else:
                best = overlap
                remove = existing_match_key

            dupes[best] |= dupes[remove]
            LOGGER.info(f"Duplicates of {remove} swapped to duplicates of {best}")
            dupes[best].add(remove)
            LOGGER.info(f"{remove} recorded as duplicate of {best}")
            del dupes[remove]
