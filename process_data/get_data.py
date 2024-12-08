"""
Created on Apr 7, 2023

@author: fred
"""
import json
from collections import Counter
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
    SHORT_STORY_SQUARE_NUM,
    SHORT_STORY_TITLE_AUTHOR_HM_COLS,
    SQUARE_NAMES,
)
from .types.bingo_card import (
    BingoCard,
    BingoSquare,
    ShortStorySquare,
)
from .types.defined_types import (
    Author,
    AuthorCol,
    Book,
    CardID,
    HardModeCol,
    SquareName,
    Title,
    TitleAuthor,
    TitleCol,
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
    return tuple((title, author) for title, author in title_author_pairs if title and author)


def book_to_title_author(book: Book) -> TitleAuthor:
    """Convert book to title/author pair"""
    title, author = book.split(CUSTOM_SEPARATOR)
    return cast(Title, title), cast(Author, author)


def books_to_title_authors(books: Iterable[Book]) -> tuple[TitleAuthor, ...]:
    """Convert iterable of books to tuple of title/author pairs"""
    return tuple(book_to_title_author(book) for book in books)


def title_author_to_book(title_author_pair: TitleAuthor) -> Book:
    """Convert title/author pair to book form"""
    return cast(Book, CUSTOM_SEPARATOR.join(str(elem) for elem in title_author_pair))


def title_authors_to_books(title_author_pairs: Iterable[TitleAuthor]) -> tuple[Book, ...]:
    """Convert an iterable of title/author pairs to a tuple of Books"""
    return tuple(title_author_to_book(pair) for pair in title_author_pairs)


def get_unique_books(title_author_pairs: tuple[TitleAuthor, ...]) -> frozenset[Book]:
    """Get every unique title/author combination"""

    for pair in title_author_pairs:
        for elem in pair:
            if CUSTOM_SEPARATOR in str(elem):
                raise ValueError("Pick a different separator")

    return frozenset(title_authors_to_books(title_author_pairs))


def get_short_story_square(
    row: pandas.Series,  # type: ignore[type-arg]
) -> Optional[ShortStorySquare]:
    """Get a square of five short stories"""
    shorts = []
    for ss_title_col, ss_author_col, _ in SHORT_STORY_TITLE_AUTHOR_HM_COLS:
        ss_title = cast(Title, row[ss_title_col])
        ss_author = cast(Author, row[ss_author_col])

        if ss_title and ss_author:
            shorts.append((ss_title, ss_author))
        else:
            return None

    return ShortStorySquare(
        title=cast(Title, ""),
        author=cast(Author, ""),
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
    title = cast(Title, row[title_col])
    author = cast(Author, row[author_col])
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

        index = cast(CardID, index)

        subbed_square_map = {
            cast(SquareName, row["SUBBED OUT"]): cast(SquareName, row["SUBBED IN"])
        }

        for square_tuple in tuple(subbed_square_map.items()):
            subbed_count[square_tuple] += 1

        cards[index], incomplete_squares = get_bingo_card(row, subbed_square_map)

        if len(incomplete_squares) > 0:
            incomplete_card_count[index] += len(incomplete_squares)
        for square_name in incomplete_squares:
            incomplete_square_count[square_name] += 1

    return MAP(cards), subbed_count, incomplete_card_count, incomplete_square_count
