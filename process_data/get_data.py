"""
Created on Apr 7, 2023

@author: fred
"""
import json
from pathlib import Path

import pandas
from pyexcel_ods3 import get_data  # type: ignore

from .types.recorded_states import RecordedStates


def get_existing_states(dupe_path: Path) -> RecordedStates:
    """Attempt to retrieve existing RecordedStates, returning empty on failure"""
    try:
        with dupe_path.open("r", encoding="utf8") as dupe_file:
            return RecordedStates.from_data(json.load(dupe_file))
    except IOError:
        return RecordedStates.empty()


def get_bingo_dataframe(bingo_data_filepath: Path) -> pandas.DataFrame:
    """Create a Pandas DataFrame of the bingo data, indexed on card number"""
    raw_bingo_data = dict(get_data(str(bingo_data_filepath)))

    column_names = raw_bingo_data["Uncorrectd 2022 Data"][0]

    bingo_data = pandas.DataFrame(
        raw_bingo_data["Uncorrectd 2022 Data"][1:],
        columns=column_names,
    ).set_index("CARD")

    return bingo_data


def get_unique_title_author_combos(data: pandas.DataFrame) -> frozenset[str]:
    """Get every unique title/author combination"""
    column_names = data.columns
    title_author_colnames = tuple(
        (col_name_1, col_name_2)
        for col_name_1 in column_names
        for col_name_2 in column_names
        if "TITLE" in col_name_1
        and "AUTHOR" in col_name_2
        and col_name_1.split(":")[0] == col_name_2.split(":")[0]
    )

    title_author_pairs: list[tuple[str, str]] = []
    for title_col, author_col in title_author_colnames:
        title_author_pairs.extend(zip(data[title_col], data[author_col]))

    return frozenset({" by ".join(str(elem) for elem in pair) for pair in title_author_pairs})
