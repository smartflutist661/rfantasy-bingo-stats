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
)

import pandas
from progressbar import progressbar  # type: ignore

from process_data.data_operations.author_title_book_operations import title_author_to_book

from ..constants import TITLE_AUTHOR_SEPARATOR
from ..data.current import (
    ALL_TITLE_AUTHOR_HM_COLUMNS,
    OUTPUT_DF_FILEPATH,
)
from ..data.filepaths import DUPE_RECORD_FILEPATH
from ..types.defined_types import (
    Author,
    Book,
)
from ..types.recorded_states import RecordedDupes


def update_bingo_books(
    data: pandas.DataFrame,
    books_to_replace: Mapping[Book, AbstractSet[Book]],
) -> pandas.DataFrame:
    """
    Update the dataframe with the recorded changes

    Also saves dataframe
    """

    new_data = data.copy()

    # This makes lookups easier
    inverted_replacements = {v: key for key, val in books_to_replace.items() for v in val}

    for title_col, author_col, _ in progressbar(ALL_TITLE_AUTHOR_HM_COLUMNS):
        for old, new in inverted_replacements.items():
            old_title, old_author = old.split(TITLE_AUTHOR_SEPARATOR)
            new_title, new_author = new.split(TITLE_AUTHOR_SEPARATOR)
            paired_cols = (
                new_data[title_col] == old_title  # pylint: disable=unsubscriptable-object
            ) & (
                new_data[author_col] == old_author  # pylint: disable=unsubscriptable-object
            )
            new_data.loc[paired_cols, title_col] = new_title
            new_data.loc[paired_cols, author_col] = new_author

    new_data.to_csv(OUTPUT_DF_FILEPATH)

    return new_data


def update_bingo_authors(
    data: pandas.DataFrame,
    authors_to_replace: Mapping[Author, AbstractSet[Author]],
) -> tuple[pandas.DataFrame, Mapping[Book, frozenset[Book]]]:
    """
    Update the dataframe with the recorded changes

    Also saves dataframe
    """

    new_data = data.copy()

    # This makes lookups easier
    inverted_replacements = {v: key for key, val in authors_to_replace.items() for v in val}

    all_author_dedupes: defaultdict[Book, set[Book]] = defaultdict(set)
    for title_col, author_col, _ in progressbar(ALL_TITLE_AUTHOR_HM_COLUMNS):
        for old_author, new_author in inverted_replacements.items():
            for title in new_data.loc[new_data[author_col] == old_author, title_col].unique():
                all_author_dedupes[title_author_to_book((title, new_author))].add(
                    title_author_to_book((title, old_author))
                )
            new_data.loc[new_data[author_col] == old_author, author_col] = new_author

    new_data.to_csv(OUTPUT_DF_FILEPATH)

    return new_data, MAP(
        {
            author_dedupe: frozenset(author_dedupes)
            for author_dedupe, author_dedupes in all_author_dedupes.items()
        }
    )


def comma_separate_authors(recorded_states: RecordedDupes) -> None:
    """Turn all multi-authors into comma-separated"""

    for string in (";", " , ", ", & ", " & ", ", and ", " and ", ", with ", " with "):
        for author, author_dedupes in tuple(recorded_states.author_dupes.items()):
            if string in author:
                updated_author = Author(author.replace(string, ", "))
                recorded_states.author_dupes[updated_author] |= author_dedupes
                recorded_states.author_dupes[updated_author].add(author)
                del recorded_states.author_dupes[author]

    with DUPE_RECORD_FILEPATH.open("w", encoding="utf8") as dupe_file:
        json.dump(recorded_states.to_data(), dupe_file, indent=2)
    print("Updated duplicates saved.")
