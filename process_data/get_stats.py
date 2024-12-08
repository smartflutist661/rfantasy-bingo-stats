"""
Created on Apr 7, 2023

@author: fred
"""
from collections import Counter
from typing import (
    Iterable,
    cast,
)

import pandas

from .constants import (
    NOVEL_TITLE_AUTHOR_HM_COLS,
    SHORT_STORY_SQUARE_NUM,
    SHORT_STORY_TITLE_AUTHOR_HM_COLS,
    SQUARE_NAMES,
)
from .types.defined_types import (
    CardID,
    SquareName,
)


def get_incomplete_info(data: pandas.DataFrame) -> tuple[Counter[CardID], Counter[SquareName]]:
    """Check all 25 square to see how many are incomplete for each row"""
    incomplete_card_counts: Counter[CardID] = Counter()
    incomplete_square_counts: Counter[SquareName] = Counter()

    for title_col, author_col, _ in NOVEL_TITLE_AUTHOR_HM_COLS:

        novel_condition = data[title_col].astype(bool) & data[author_col].astype(bool)

        if SHORT_STORY_SQUARE_NUM in title_col:

            short_story_condition = pandas.Series(False, index=data.index)

            for ss_title_col, ss_author_col, _ in SHORT_STORY_TITLE_AUTHOR_HM_COLS:
                short_story_condition = (
                    data[ss_title_col].astype(bool) & data[ss_author_col].astype(bool)
                ) | short_story_condition

            incomplete_card_counts.update(
                cast(Iterable[CardID], data.index[short_story_condition | novel_condition])
            )
            incomplete_square_counts[square_name] = sum(short_story_condition | novel_condition)
        else:
            incomplete_card_counts.update(cast(Iterable[CardID], data.index[novel_condition]))
            incomplete_square_counts[square_name] = sum(novel_condition)

    return incomplete_card_counts, incomplete_square_counts
