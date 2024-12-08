"""
Created on Apr 7, 2023

@author: fred
"""
import json
from pathlib import Path
from types import MappingProxyType as MAP
from typing import (
    Iterable,
    Mapping,
    Optional,
    cast,
)

import pandas
from pyexcel_ods3 import get_data  # type: ignore

from .constants import (
    ALL_TITLE_AUTHOR_HM_COLUMNS,
    CUSTOM_SEPARATOR,
    NOVEL_TITLE_AUTHOR_HM_COLS,
    SQUARE_NAMES,
)
from .types.bingo_card import (
    BingoCard,
    BingoSquare,
)
from .types.defined_types import (
    Author,
    Book,
    CardID,
    SquareName,
    Title,
    TitleAuthor,
)
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


def get_all_title_author_combos(data: pandas.DataFrame) -> tuple[TitleAuthor, ...]:
    """Get every title/author pair in data"""
    title_author_pairs: list[TitleAuthor] = []
    for title_col, author_col, _ in ALL_TITLE_AUTHOR_HM_COLUMNS:
        title_author_pairs.extend(
            cast(Iterable[TitleAuthor], zip(data[title_col], data[author_col]))
        )
    return tuple(title_author_pairs)


def get_unique_books(title_author_pairs: tuple[TitleAuthor, ...]) -> frozenset[Book]:
    """Get every unique title/author combination"""

    for pair in title_author_pairs:
        for elem in pair:
            if CUSTOM_SEPARATOR in str(elem):
                raise ValueError("Pick a different separator")

    return frozenset(
        {
            cast(Book, CUSTOM_SEPARATOR.join(str(elem) for elem in pair))
            for pair in title_author_pairs
        }
    )


def get_indexed_bingo_cards(data: pandas.DataFrame) -> Mapping[CardID, BingoCard]:
    """Get tuple of bingo cards with substituted names"""

    # TODO: Make this a multiindexed dataframe

    cards: dict[CardID, BingoCard] = {}
    for index, row in data.iterrows():

        subbed_square_map = {
            cast(SquareName, row["SUBBED OUT"]): cast(SquareName, row["SUBBED IN"])
        }

        card: dict[SquareName, Optional[BingoSquare]] = {}
        for title_col, author_col, hm_col in NOVEL_TITLE_AUTHOR_HM_COLS:
            square_name = SQUARE_NAMES[title_col]

            # TODO: count subs

            real_square_name = subbed_square_map.get(square_name, square_name)
            title = cast(Title, row[title_col])
            author = cast(Author, row[author_col])
            hard_mode = bool(row[hm_col])

            card[real_square_name] = BingoSquare(
                title=title,
                author=author,
                hard_mode=hard_mode,
            )
        cards[cast(CardID, index)] = MAP(card)

    return MAP(cards)
