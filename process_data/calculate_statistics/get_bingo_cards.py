"""
Created on Apr 9, 2023

@author: fred
"""
from collections import Counter
from types import MappingProxyType as MAP
from typing import (
    Mapping,
    Optional,
)

import pandas

from ..data.current import (
    NOVEL_TITLE_AUTHOR_HM_COLS,
    SHORT_STORY_SQUARE_NUM,
    SHORT_STORY_TITLE_AUTHOR_HM_COLS,
    SQUARE_NAMES,
)
from ..types.bingo_card import (
    BingoCard,
    BingoSquare,
    ShortStorySquare,
)
from ..types.defined_types import (
    Author,
    AuthorCol,
    CardID,
    HardModeCol,
    SquareName,
    Title,
    TitleCol,
)


def get_short_story_square(
    row: pandas.Series,  # type: ignore[type-arg]
) -> Optional[ShortStorySquare]:
    """Get a square of five short stories"""
    shorts = []
    for ss_title_col, ss_author_col, _ in SHORT_STORY_TITLE_AUTHOR_HM_COLS:
        ss_title = Title(row[ss_title_col])
        ss_author = Author(row[ss_author_col])

        if ss_title and ss_author:
            shorts.append((ss_title, ss_author))
        else:
            return None

    return ShortStorySquare(
        title=Title(""),
        author=Author(""),
        hard_mode=False,
        stories=tuple(shorts),
    )


def get_bingo_square(
    row: pandas.Series,  # type: ignore[type-arg]
    title_col: TitleCol,
    author_col: AuthorCol,
    hm_col: HardModeCol,
) -> Optional[BingoSquare]:
    """Get a single bingo square"""
    title = Title(row[title_col])
    author = Author(row[author_col])
    hard_mode = bool(row[hm_col])

    if title and author:
        return BingoSquare(
            title=title,
            author=author,
            hard_mode=hard_mode,
        )

    if SHORT_STORY_SQUARE_NUM in title_col:
        return get_short_story_square(row)

    return None


def get_bingo_card(
    row: pandas.Series,  # type: ignore[type-arg]
    subbed_square_map: Mapping[SquareName, SquareName],
) -> tuple[BingoCard, frozenset[SquareName]]:
    """Get a single bingo card"""
    card: dict[SquareName, Optional[BingoSquare]] = {}
    incomplete_squares = set()
    for title_col, author_col, hm_col in NOVEL_TITLE_AUTHOR_HM_COLS:
        square_name = SQUARE_NAMES[title_col]

        real_square_name = subbed_square_map.get(square_name, square_name)

        square = get_bingo_square(row, title_col, author_col, hm_col)
        card[real_square_name] = square
        if square is None:
            incomplete_squares.add(real_square_name)

    return MAP(card), frozenset(incomplete_squares)


def get_bingo_cards(
    data: pandas.DataFrame,
) -> tuple[
    Mapping[CardID, BingoCard],
    Counter[tuple[SquareName, SquareName]],
    Counter[CardID],
    Counter[SquareName],
]:
    """Get tuple of bingo cards with substituted names"""

    cards: dict[CardID, BingoCard] = {}
    subbed_count: Counter[tuple[SquareName, SquareName]] = Counter()
    incomplete_card_count: Counter[CardID] = Counter()
    incomplete_square_count: Counter[SquareName] = Counter()
    for index, row in data.iterrows():
        index = CardID(str(index))

        subbed_square_map = {SquareName(row["SUBBED OUT"]): SquareName(row["SUBBED IN"])}

        for square_tuple in tuple(subbed_square_map.items()):
            if square_tuple[0] and square_tuple[1]:
                subbed_count[square_tuple] += 1

        cards[index], incomplete_squares = get_bingo_card(row, subbed_square_map)

        if len(incomplete_squares) > 0:
            incomplete_card_count[index] += len(incomplete_squares)
        for square_name in incomplete_squares:
            incomplete_square_count[square_name] += 1

    return MAP(cards), subbed_count, incomplete_card_count, incomplete_square_count
