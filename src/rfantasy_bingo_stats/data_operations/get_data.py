"""
Created on Apr 7, 2023

@author: fred
"""

import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas

from ..types.recorded_ignores import RecordedIgnores
from ..types.recorded_states import RecordedDupes


def get_existing_states(
    dupe_path: Path,
    ignore_path: Path,
    skip_updates: bool,
) -> tuple[RecordedDupes, RecordedIgnores]:
    """Attempt to retrieve existing RecordedDupes, returning empty on failure"""
    try:
        with dupe_path.open("r", encoding="utf8") as dupe_file:
            dupes = RecordedDupes.from_data(json.load(dupe_file), skip_updates)
        with ignore_path.open("r", encoding="utf8") as ignore_file:
            ignores = RecordedIgnores.from_data(json.load(ignore_file))
        return dupes, ignores
    except IOError:
        return RecordedDupes(
            author_dupes=defaultdict(set), book_dupes=defaultdict(set)
        ), RecordedIgnores(
            ignored_author_dupes=defaultdict(set), ignored_book_dupes=defaultdict(set)
        )


def get_bingo_dataframe(bingo_data_filepath: Path) -> pandas.DataFrame:
    """Create a Pandas DataFrame of the bingo data, indexed on card number"""

    bingo_data = pandas.read_csv(bingo_data_filepath)
    bingo_data.set_index("CARD", inplace=True)

    # Just looping through everywhere, minimal performance implications?
    return bingo_data.replace({np.nan: None})
