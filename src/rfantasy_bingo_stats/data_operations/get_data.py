from collections import defaultdict
from pathlib import Path
from typing import AbstractSet

import numpy as np
import pandas

from rfantasy_bingo_stats.constants import (
    DUPE_RECORD_FILEPATH,
    IGNORED_RECORD_FILEPATH,
)
from rfantasy_bingo_stats.data_operations.author_title_book_operations import (
    get_all_authors,
    get_all_title_author_combos,
    get_unique_authors,
    get_unique_books,
)
from rfantasy_bingo_stats.models.card_data import CardData
from rfantasy_bingo_stats.models.defined_types import (
    Author,
    Book,
)
from rfantasy_bingo_stats.models.recorded_ignores import RecordedIgnores
from rfantasy_bingo_stats.models.recorded_states import RecordedDupes


def get_existing_states() -> tuple[RecordedDupes, RecordedIgnores]:
    """Attempt to retrieve existing RecordedDupes, returning empty on failure"""
    try:
        with DUPE_RECORD_FILEPATH.open("r", encoding="utf8") as dupe_file:
            dupes = RecordedDupes.model_validate_json(dupe_file.read())
        with IGNORED_RECORD_FILEPATH.open("r", encoding="utf8") as ignore_file:
            ignores = RecordedIgnores.model_validate_json(ignore_file.read())
        return dupes, ignores
    except IOError:
        return RecordedDupes(
            author_dupes=defaultdict(set), book_dupes=defaultdict(set)
        ), RecordedIgnores(
            ignored_author_dupes=defaultdict(set), ignored_book_dupes=defaultdict(set)
        )


def get_unique_bingo_authors(
    bingo_data: pandas.DataFrame,
    card_data: CardData,
) -> AbstractSet[Author]:
    all_authors = get_all_authors(bingo_data, card_data.all_title_author_hm_columns)

    return get_unique_authors(all_authors)


def get_unique_bingo_books(
    bingo_data: pandas.DataFrame,
    card_data: CardData,
) -> AbstractSet[Book]:
    all_title_author_combos = get_all_title_author_combos(
        bingo_data, card_data.all_title_author_hm_columns
    )

    return get_unique_books(all_title_author_combos)


def get_bingo_dataframe(bingo_data_filepath: Path) -> pandas.DataFrame:
    """Create a Pandas DataFrame of the bingo data, indexed on card number"""

    bingo_data = pandas.read_csv(bingo_data_filepath)
    bingo_data.set_index("CARD", inplace=True)

    # Just looping through everywhere, minimal performance implications?
    return bingo_data.replace({np.nan: None})
