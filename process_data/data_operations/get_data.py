"""
Created on Apr 7, 2023

@author: fred
"""
import json
from collections import defaultdict
from pathlib import Path

import pandas
from pyexcel_ods3 import get_data  # type: ignore

from ..types.recorded_states import RecordedStates


def get_existing_states(dupe_path: Path) -> RecordedStates:
    """Attempt to retrieve existing RecordedStates, returning empty on failure"""
    try:
        with dupe_path.open("r", encoding="utf8") as dupe_file:
            return RecordedStates.from_data(json.load(dupe_file))
    except IOError:
        return RecordedStates(
            author_dupes=defaultdict(set),
            book_dupes=defaultdict(set),
            ignored_author_dupes=defaultdict(set),
            ignored_book_dupes=defaultdict(set),
        )


def get_bingo_dataframe(bingo_data_filepath: Path) -> pandas.DataFrame:
    """Create a Pandas DataFrame of the bingo data, indexed on card number"""
    raw_bingo_data = dict(get_data(str(bingo_data_filepath)))

    column_names = raw_bingo_data["Uncorrectd 2022 Data"][0]

    bingo_data = pandas.DataFrame(
        raw_bingo_data["Uncorrectd 2022 Data"][1:],
        columns=column_names,
    ).set_index("CARD")

    return bingo_data
