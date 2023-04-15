"""
Created on Apr 7, 2023

@author: fred
"""
import json
from collections import defaultdict
from types import MappingProxyType as MAP
from typing import (
    AbstractSet,
    Mapping,
    cast,
)

import pandas
from progressbar import progressbar  # type: ignore

from ..data.current import (
    ALL_TITLE_AUTHOR_HM_COLUMNS,
    CUSTOM_SEPARATOR,
    OUTPUT_DF_FILEPATH,
)
from ..data.filepaths import DUPE_RECORD_FILEPATH
from ..types.defined_types import (
    Author,
    Book,
)
from ..types.recorded_states import RecordedStates
from .author_title_book_operations import title_author_to_book


def update_bingo_books(
    data: pandas.DataFrame,
    books_to_replace: Mapping[Book, AbstractSet[Book]],
) -> None:
    """
    Update the dataframe with the recorded changes

    Also saves dataframe
    """

    # This makes lookups easier
    inverted_replacements = {v: key for key, val in books_to_replace.items() for v in val}

    for title_col, author_col, _ in progressbar(ALL_TITLE_AUTHOR_HM_COLUMNS):
        for old, new in inverted_replacements.items():
            old_title, old_author = old.split(CUSTOM_SEPARATOR)
            new_title, new_author = new.split(CUSTOM_SEPARATOR)
            paired_cols = (
                data[title_col] == old_title  # pylint: disable=unsubscriptable-object
            ) & (
                data[author_col] == old_author  # pylint: disable=unsubscriptable-object
            )
            data.loc[paired_cols, title_col] = new_title
            data.loc[paired_cols, author_col] = new_author

    data.to_csv(OUTPUT_DF_FILEPATH)


def update_bingo_authors(
    data: pandas.DataFrame,
    authors_to_replace: Mapping[Author, AbstractSet[Author]],
    separator: str,
) -> Mapping[Book, frozenset[Book]]:
    """
    Update the dataframe with the recorded changes

    Also saves dataframe
    """

    # This makes lookups easier
    inverted_replacements = {v: key for key, val in authors_to_replace.items() for v in val}

    all_author_dedupes: defaultdict[Book, set[Book]] = defaultdict(set)
    for title_col, author_col, _ in progressbar(ALL_TITLE_AUTHOR_HM_COLUMNS):
        for old_author, new_author in inverted_replacements.items():
            for title in data.loc[data[author_col] == old_author, title_col].unique():
                all_author_dedupes[title_author_to_book((title, new_author), separator)].add(
                    title_author_to_book((title, old_author), separator)
                )
            data.loc[data[author_col] == old_author, author_col] = new_author

    data.to_csv(OUTPUT_DF_FILEPATH)

    return MAP(
        {
            author_dedupe: frozenset(author_dedupes)
            for author_dedupe, author_dedupes in all_author_dedupes.items()
        }
    )


def comma_separate_authors(recorded_states: RecordedStates) -> None:
    """Turn all multi-authors into comma-separated"""

    for string in (" , ", ", & ", " & ", ", and ", " and "):
        for author, author_dedupes in tuple(recorded_states.author_dupes.items()):
            if string in author:
                updated_author = cast(Author, author.replace(string, ", "))
                recorded_states.author_dupes[updated_author] |= author_dedupes
                recorded_states.author_dupes[updated_author].add(author)
                del recorded_states.author_dupes[author]

    with DUPE_RECORD_FILEPATH.open("w", encoding="utf8") as dupe_file:
        json.dump(recorded_states.to_data(), dupe_file, indent=2)
    print("Updated duplicates saved.")


def add_to_markdown(lines: list[str], new_str: str) -> None:
    """Print and add to a collection of lines to write as a Markdown file"""
    print(new_str)
    lines.append(new_str)
