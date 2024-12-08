"""
Created on Apr 7, 2023

@author: fred
"""
import json
from collections import defaultdict
from pathlib import Path

import pandas
from pyexcel_ods3 import get_data  # type: ignore

from ..types.recorded_ignores import RecordedIgnores
from ..types.recorded_states import RecordedDupes


def get_existing_states(
    dupe_path: Path, ignore_path: Path, skip_updates: bool
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
    raw_bingo_data = dict(get_data(str(bingo_data_filepath)))

    bingo_data = pandas.DataFrame(raw_bingo_data["Sheet1"])
    bingo_data.columns = bingo_data.iloc[0]
    bingo_data.drop(bingo_data.index[0], inplace=True)
    bingo_data.set_index("CARD")

    return bingo_data
