"""
Created on Apr 7, 2023

@author: fred
"""
from typing import Mapping

import pandas

from .constants import (
    CUSTOM_SEPARATOR,
    OUTPUT_DF_FILEPATH,
)


def update_bingo_dataframe(
    data: pandas.DataFrame,
    vals_to_replace: Mapping[str, frozenset[str]],
    title_author_colpairs: tuple[tuple[str, str], ...],
) -> None:
    """
    Update the dataframe with the recorded changes

    Also saves dataframe
    """

    # This makes lookups easier
    inverted_replacements = {v: key for key, val in vals_to_replace.items() for v in val}

    for title_col, author_col in title_author_colpairs:
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
