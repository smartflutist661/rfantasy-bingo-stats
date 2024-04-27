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

from ..data_operations.author_title_book_operations import (
    book_to_title_author,
    title_author_to_book,
)
from ..types.author_info import AuthorInfo
from ..types.author_statistics import AuthorStatistics
from ..types.bingo_card import (
    BingoCard,
    BingoSquare,
    ShortStorySquare,
)
from ..types.bingo_statistics import BingoStatistics
from ..types.card_data import CardData
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
    card_data: CardData,
) -> Optional[ShortStorySquare]:
    """Get a square of five short stories"""
    shorts = []
    for ss_title_col, ss_author_col, _ in card_data.short_story_title_author_hm_cols:
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
    card_data: CardData,
) -> Optional[BingoSquare]:
    """Get a single bingo square"""
    title = row[title_col]
    author = row[author_col]
    if len(hm_col) > 0:
        hard_mode = bool(row[hm_col])
    else:
        hard_mode = True

    # This captures hard mode short story squares (collections/anthologies)
    if title and author:
        return BingoSquare(
            title=Title(str(title)),
            author=Author(str(author)),
            hard_mode=hard_mode,
        )

    if str(card_data.short_story_square_num) in title_col:
        return get_short_story_square(row, card_data)

    return None


def get_bingo_card(
    row: pandas.Series,  # type: ignore[type-arg]
    subbed_square_map: Mapping[SquareName, SquareName],
    card_data: CardData,
) -> BingoCard:
    """Get a single bingo card"""
    final_sub_map = dict(subbed_square_map)
    card: dict[SquareName, Optional[BingoSquare]] = {}
    for title_col, author_col, hm_col in card_data.novel_title_author_hm_cols:
        square_name = card_data.square_names[title_col]

        real_square_name = subbed_square_map.get(square_name, square_name)

        square = get_bingo_square(row, title_col, author_col, hm_col, card_data)

        card[real_square_name] = square

        if square is None and square_name != real_square_name:
            del final_sub_map[square_name]

    return BingoCard(MAP(card), final_sub_map)


def get_bingo_cards(data: pandas.DataFrame, card_data: CardData) -> Mapping[CardID, BingoCard]:
    cards: dict[CardID, BingoCard] = {}
    for index, row in data.iterrows():
        card_id = CardID(str(index))
        if card_id in ("nan", "None"):
            continue

        if card_data.subbed_by_square:
            subbed_square_map = {}
            for square_num, square_name in enumerate(card_data.square_names.values()):
                subbed_square_name = SquareName(row[f"SQUARE {square_num+1}: SUBSTITUTION"])
                if subbed_square_name is not None and len(subbed_square_name) > 0:
                    subbed_square_map[square_name] = subbed_square_name
        else:
            subbed_square_map = {SquareName(row["SUBBED OUT"]): SquareName(row["SUBBED IN"])}

        bingo_card = get_bingo_card(row, subbed_square_map, card_data)

        cards[card_id] = bingo_card

    return MAP(cards)


def get_bingo_stats(
    cards: Mapping[CardID, BingoCard],
    recorded_states: RecordedDupes,
    card_data: CardData,
    author_data: Mapping[Author, AuthorInfo],
) -> BingoStatistics:
    """Get tuple of bingo cards with substituted names"""

    subbed_count: Counter[tuple[SquareName, SquareName]] = Counter()
    subbed_out_squares: Counter[SquareName] = Counter()
    incomplete_card_count: Counter[CardID] = Counter()
    incomplete_square_count: Counter[SquareName] = Counter()
    square_uniques: defaultdict[SquareName, UniqueStatistics] = defaultdict(UniqueStatistics)
    unique_square_book_usage: defaultdict[Book, set[SquareName]] = defaultdict(set)
    unique_square_author_usage: defaultdict[Author, set[SquareName]] = defaultdict(set)
    dedupes_by_card: Counter[CardID] = Counter()
    dedupes_by_book: defaultdict[Book, set[Book]] = defaultdict(set)
    all_books: Counter[Book] = Counter()
    all_authors: Counter[Author] = Counter()
    total_story_count = 0
    card_uniques: Counter[CardID] = Counter()
    hard_mode_by_card: Counter[CardID] = Counter()
    hard_mode_by_square: Counter[SquareName] = Counter()
    books_by_author: defaultdict[Author, set[Book]] = defaultdict(set)

    overall_author_stats: AuthorStatistics = AuthorStatistics()
    square_author_stats: defaultdict[SquareName, AuthorStatistics] = defaultdict(AuthorStatistics)

    book_dedupe_map = recorded_states.get_book_dedupe_map()

    current_square_names = frozenset(card_data.square_names.values())
    for square_name in current_square_names:
        subbed_out_squares[square_name] += 0

    for card_id, bingo_card in cards.items():

        for subbed_out_square, subbed_in_square in bingo_card.subbed_square_map.items():
            subbed_count[(subbed_out_square, subbed_in_square)] += 1
            subbed_out_squares[subbed_out_square] += 1

        hard_mode_by_card[card_id] += 0
        for square_name, square in bingo_card.squares.items():
            if square is not None:
                if not isinstance(square, ShortStorySquare):
                    book = title_author_to_book((square.title, square.author))
                    _, author = book_to_title_author(book)

                    if book in book_dedupe_map:
                        orig_book = book
                        book = book_dedupe_map[book]

                        _, author = book_to_title_author(book)

                        dedupes_by_card[card_id] += 1
                        dedupes_by_book[book].add(orig_book)

                    square_uniques[square_name].unique_books[book] += 1
                    unique_square_book_usage[book].add(square_name)

                    all_books[book] += 1

                    for split_author in author.split(", "):  # pylint: disable=no-member
                        single_author = Author(split_author)
                        all_authors[single_author] += 1
                        square_uniques[square_name].unique_authors[single_author] += 1
                        unique_square_author_usage[single_author].add(square_name)
                        books_by_author[single_author].add(book)

                        author_info = author_data.get(single_author, AuthorInfo())

                        overall_author_stats.gender_count[author_info.gender] += 1
                        overall_author_stats.race_count[author_info.race] += 1
                        overall_author_stats.queer_count[author_info.queer] += 1
                        overall_author_stats.nationality_count[author_info.nationality] += 1

                        square_author_stats[square_name].gender_count[author_info.gender] += 1
                        square_author_stats[square_name].race_count[author_info.race] += 1
                        square_author_stats[square_name].queer_count[author_info.queer] += 1
                        square_author_stats[square_name].nationality_count[
                            author_info.nationality
                        ] += 1

                    total_story_count += 1

                    if square.hard_mode:
                        hard_mode_by_card[card_id] += 1
                        hard_mode_by_square[square_name] += 1

                else:
                    total_story_count += len(square.stories)
            else:
                incomplete_card_count[card_id] += 1
                incomplete_square_count[square_name] += 1

    # Loop again after collecting `all_books` to determine uniques
    for card_id, card in cards.items():
        card_uniques[card_id] += 0
        for square_name, square in card.squares.items():
            if square is not None:
                book = title_author_to_book((square.title, square.author))
                if book in book_dedupe_map:
                    book = book_dedupe_map[book]

                if all_books[book] == 1:
                    card_uniques[card_id] += 1

    return BingoStatistics(
        total_card_count=len(cards),
        total_story_count=total_story_count,
        incomplete_cards=incomplete_card_count,
        incomplete_squares=incomplete_square_count,
        max_incomplete_squares=max(
            incomplete for incomplete in incomplete_card_count.values() if incomplete != 25
        ),
        incomplete_squares_per_card=Counter(incomplete_card_count.values()),
        subbed_squares=subbed_count,
        subbed_out_squares=subbed_out_squares,
        avoided_squares=incomplete_square_count + subbed_out_squares,
        overall_uniques=UniqueStatistics(all_books, all_authors),
        square_uniques=MAP(square_uniques),
        unique_squares_by_book=Counter(
            {book: len(squares) for book, squares in unique_square_book_usage.items()}
        ),
        unique_squares_by_author=Counter(
            {author: len(squares) for author, squares in unique_square_author_usage.items()}
        ),
        bad_spellings_by_card=dedupes_by_card,
        bad_spellings_by_book=Counter(
            {book: len(variations) for book, variations in dedupes_by_book.items()}
        ),
        card_uniques=card_uniques,
        hard_mode_by_card=hard_mode_by_card,
        hard_mode_by_square=hard_mode_by_square,
        books_per_author=Counter(
            {author: len(books) for author, books in books_by_author.items()}
        ),
        overall_author_stats=overall_author_stats,
        square_author_stats=square_author_stats,
    )
