"""
Created on Apr 9, 2023

@author: fred
"""
from collections import (
    Counter,
    defaultdict,
)
from types import MappingProxyType as MAP
from typing import (
    Mapping,
    Optional,
)

import pandas

from process_data.data_operations.author_title_book_operations import (
    book_to_title_author,
    get_all_title_author_combos,
    get_unique_book_counts,
)

from ..data.current import (
    CUSTOM_SEPARATOR,
    NOVEL_TITLE_AUTHOR_HM_COLS,
    SHORT_STORY_SQUARE_NUM,
    SHORT_STORY_TITLE_AUTHOR_HM_COLS,
    SQUARE_NAMES,
)
from ..data_operations.author_title_book_operations import title_author_to_book
from ..types.bingo_card import (
    BingoCard,
    BingoSquare,
    ShortStorySquare,
)
from ..types.bingo_statistics import BingoStatistics
from ..types.defined_types import (
    Author,
    AuthorCol,
    Book,
    CardID,
    HardModeCol,
    SquareName,
    Title,
    TitleCol,
)
from ..types.recorded_states import RecordedDupes
from ..types.unique_statistics import UniqueStatistics


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


def get_bingo_stats(
    data: pandas.DataFrame,
    recorded_states: RecordedDupes,
) -> BingoStatistics:
    """Get tuple of bingo cards with substituted names"""

    cards: dict[CardID, BingoCard] = {}
    subbed_count: Counter[tuple[SquareName, SquareName]] = Counter()
    incomplete_card_count: Counter[CardID] = Counter()
    incomplete_square_count: Counter[SquareName] = Counter()
    square_uniques: defaultdict[SquareName, UniqueStatistics] = defaultdict(UniqueStatistics)
    unique_square_book_usage: defaultdict[Book, set[SquareName]] = defaultdict(set)
    unique_square_author_usage: defaultdict[Author, set[SquareName]] = defaultdict(set)
    dedupes_by_card: Counter[CardID] = Counter()
    dedupes_by_primary: Counter[Book] = Counter()

    dedupe_map = recorded_states.get_book_dedupe_map()

    for index, row in data.iterrows():
        index = CardID(str(index))

        subbed_square_map = {SquareName(row["SUBBED OUT"]): SquareName(row["SUBBED IN"])}

        for square_tuple in tuple(subbed_square_map.items()):
            if square_tuple[0] and square_tuple[1]:
                subbed_count[square_tuple] += 1

        bingo_card, incomplete_squares = get_bingo_card(row, subbed_square_map)

        cards[index] = bingo_card

        if len(incomplete_squares) > 0:
            incomplete_card_count[index] += len(incomplete_squares)
        for square_name in incomplete_squares:
            incomplete_square_count[square_name] += 1

        for square_name, square in bingo_card.items():
            if square is not None:
                if not isinstance(square, ShortStorySquare):
                    book = title_author_to_book((square.title, square.author), CUSTOM_SEPARATOR)

                    if book in dedupe_map:
                        book = dedupe_map[book]
                        dedupes_by_card[index] += 1
                        dedupes_by_primary[book] += 1

                    _, author = book_to_title_author(book, CUSTOM_SEPARATOR)

                    square_uniques[square_name].unique_authors[author] += 1
                    square_uniques[square_name].unique_books[book] += 1
                    unique_square_book_usage[book].add(square_name)
                    unique_square_author_usage[author].add(square_name)

    all_title_authors = get_all_title_author_combos(data)
    unique_book_counts = get_unique_book_counts(all_title_authors, CUSTOM_SEPARATOR)
    unique_author_counts = Counter(author for _, author in all_title_authors)

    subbed_out_squares = Counter(subbed_out for subbed_out, _ in subbed_count.keys())
    for square_name in SQUARE_NAMES.values():
        subbed_out_squares[square_name] += 0

    return BingoStatistics(
        total_card_count=len(cards),
        total_story_count=len(all_title_authors),
        incomplete_cards=incomplete_card_count,
        incomplete_squares=incomplete_square_count,
        max_incomplete_squares=max(
            incomplete for incomplete in incomplete_card_count.values() if incomplete != 25
        ),
        incomplete_squares_per_card=Counter(incomplete_card_count.values()),
        subbed_squares=subbed_count,
        subbed_out_squares=subbed_out_squares,
        avoided_squares=incomplete_square_count + subbed_out_squares,
        overall_uniques=UniqueStatistics(unique_book_counts, unique_author_counts),
        square_uniques=MAP(square_uniques),
        unique_squares_by_book=Counter(
            {book: len(squares) for book, squares in unique_square_book_usage.items()}
        ),
        unique_squares_by_author=Counter(
            {author: len(squares) for author, squares in unique_square_author_usage.items()}
        ),
        bad_spellings_by_card=dedupes_by_card,
        bad_spellings_by_book=dedupes_by_primary,
    )
