from collections import (
    Counter,
    defaultdict,
)
from numbers import Number
from types import MappingProxyType as MAP
from typing import (
    Mapping,
    Optional,
    cast,
)

import inflect
import numpy as np
import pandas

from rfantasy_bingo_stats.data_operations.author_title_book_operations import (
    book_to_title_author,
    title_author_to_book,
)
from rfantasy_bingo_stats.models.author_info import AuthorInfo
from rfantasy_bingo_stats.models.author_statistics import AuthorStatistics
from rfantasy_bingo_stats.models.bingo_card import (
    BingoCard,
    BingoSquare,
    ShortStorySquare,
)
from rfantasy_bingo_stats.models.bingo_statistics import BingoStatistics
from rfantasy_bingo_stats.models.bingo_type_statistics import BingoTypeStatistics
from rfantasy_bingo_stats.models.card_data import CardData
from rfantasy_bingo_stats.models.defined_types import (
    Author,
    AuthorCol,
    BingoName,
    Book,
    CardID,
    HardModeCol,
    SquareName,
    Title,
    TitleCol,
)
from rfantasy_bingo_stats.models.recorded_states import RecordedDupes
from rfantasy_bingo_stats.models.unique_statistics import UniqueStatistics

BINGO_SIZE = 5


def get_possible_bingos() -> Mapping[BingoName, frozenset[int]]:
    inflector = inflect.engine()
    bingo_board = np.arange(BINGO_SIZE**2).reshape(BINGO_SIZE, BINGO_SIZE)

    out: dict[BingoName, frozenset[int]] = {}
    for i, row in enumerate(bingo_board.T):
        out[
            BingoName(
                f"{inflector.number_to_words(inflector.ordinal(cast(Number, i+1)))} row".title()
            )
        ] = frozenset(row)
    for i, col in enumerate(bingo_board):
        out[
            BingoName(
                f"{inflector.number_to_words(inflector.ordinal(cast(Number, i+1)))} column".title()
            )
        ] = frozenset(col)
    out[BingoName("Diagonal")] = frozenset(bingo_board.diagonal())
    out[BingoName("Antidiagonal")] = frozenset(np.fliplr(bingo_board).diagonal())

    return out


POSSIBLE_BINGOS = get_possible_bingos()


def get_short_story_square(
    row: pandas.Series,  # type: ignore[type-arg]
    card_data: CardData,
) -> Optional[ShortStorySquare]:
    """Get a square of five short stories"""
    shorts = []
    for ss_title_col, ss_author_col, _ in card_data.short_story_title_author_hm_cols:
        ss_title = row[ss_title_col]
        ss_author = row[ss_author_col]

        if ss_title and ss_author:
            shorts.append(
                (
                    Title(ss_title),
                    Author(ss_author),
                )
            )
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
            title=Title(title),
            author=Author(author),
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
        if index is None:
            continue
        card_id = CardID(str(index))

        if card_data.subbed_by_square:
            subbed_square_map = {}
            for square_num, square_name in enumerate(card_data.square_names.values()):
                subbed_val = row[f"SQUARE {square_num+1}: SUBSTITUTION"]
                if subbed_val is not None and len(subbed_val) > 0:
                    subbed_square_map[square_name] = SquareName(subbed_val)
        else:
            if row["SUBBED OUT"] is not None and row["SUBBED IN"] is not None:
                subbed_square_map = {SquareName(row["SUBBED OUT"]): SquareName(row["SUBBED IN"])}
            else:
                subbed_square_map = {}

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
    complete_bingos_by_card: Counter[CardID] = Counter()
    incomplete_squares_by_bingo: Counter[BingoName] = Counter()
    incomplete_bingos: Counter[BingoName] = Counter()
    complete_hardmode_bingos_by_card: Counter[CardID] = Counter()
    incomplete_hardmode_squares_by_bingo: Counter[BingoName] = Counter()
    incomplete_hardmode_bingos: Counter[BingoName] = Counter()

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
        completed_square_nums = set()
        completed_hardmode_square_nums = set()
        for square_num, (square_name, square) in enumerate(bingo_card.squares.items()):
            if square is not None:
                completed_square_nums.add(square_num)
                if square.hard_mode:
                    completed_hardmode_square_nums.add(square_num)
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
                        overall_author_stats.ethnicity_count[author_info.ethnicity] += 1
                        overall_author_stats.queer_count[author_info.queer] += 1
                        overall_author_stats.nationality_count[author_info.nationality] += 1

                        square_author_stats[square_name].gender_count[author_info.gender] += 1
                        square_author_stats[square_name].ethnicity_count[
                            author_info.ethnicity
                        ] += 1
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

        complete_bingos_by_card[card_id] += 0
        complete_hardmode_bingos_by_card[card_id] += 0
        for bingo_name, square_nums in POSSIBLE_BINGOS.items():
            squares_completed = len(completed_square_nums & square_nums)
            if squares_completed == BINGO_SIZE:
                complete_bingos_by_card[card_id] += 1
            else:
                incomplete_squares_by_bingo[bingo_name] += BINGO_SIZE - squares_completed
                incomplete_bingos[bingo_name] += 1

            hardmode_squares_completed = len(completed_hardmode_square_nums & square_nums)
            if hardmode_squares_completed == BINGO_SIZE:
                complete_hardmode_bingos_by_card[card_id] += 1
            else:
                incomplete_hardmode_squares_by_bingo[bingo_name] += (
                    BINGO_SIZE - hardmode_squares_completed
                )
                incomplete_hardmode_bingos[bingo_name] += 1

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
            incomplete
            for incomplete in incomplete_card_count.values()
            if incomplete != BINGO_SIZE**2
        ),
        incomplete_squares_per_card=Counter(incomplete_card_count.values()),
        subbed_squares=subbed_count,
        subbed_out_squares=subbed_out_squares,
        avoided_squares=incomplete_square_count + subbed_out_squares,
        overall_uniques=UniqueStatistics(unique_books=all_books, unique_authors=all_authors),
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
        normal_bingo_type_stats=BingoTypeStatistics(
            complete_bingos_by_card=complete_bingos_by_card,
            incomplete_bingos=incomplete_bingos,
            incomplete_squares_by_bingo=incomplete_squares_by_bingo,
        ),
        hardmode_bingo_type_stats=BingoTypeStatistics(
            complete_bingos_by_card=complete_hardmode_bingos_by_card,
            incomplete_bingos=incomplete_hardmode_bingos,
            incomplete_squares_by_bingo=incomplete_hardmode_squares_by_bingo,
        ),
    )
