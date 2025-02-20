from collections import Counter
from collections.abc import (
    Callable,
    Collection,
    Container,
    Iterable,
    Sequence,
)
from pathlib import Path
from typing import (
    Literal,
    Optional,
)

import numpy as np

from rfantasy_bingo_stats.calculate_statistics.get_bingo_cards import (
    BINGO_SIZE,
    POSSIBLE_BINGOS,
)
from rfantasy_bingo_stats.calculate_statistics.gini_function import calculate_gini_index
from rfantasy_bingo_stats.data_operations.author_title_book_operations import book_to_title_author
from rfantasy_bingo_stats.logger import LOGGER
from rfantasy_bingo_stats.models.bingo_statistics import BingoStatistics
from rfantasy_bingo_stats.models.bingo_type_statistics import BingoTypeStatistics
from rfantasy_bingo_stats.models.card_data import CardData
from rfantasy_bingo_stats.models.defined_types import (
    Author,
    BingoName,
    Book,
    BookOrAuthor,
    CardID,
    SquareName,
)


def format_book(book: Book) -> str:
    """Format a title/author pair into a string"""
    title_author = book_to_title_author(book)
    return f"**{title_author[0]}** by {title_author[1]}"


def format_square(square_name: SquareName) -> str:
    """Format a square name"""
    return f"**{square_name}**"


def format_top_list_with_ties(
    sorted_vals: Iterable[tuple[Book | Author | SquareName, float]],
    format_template: Callable[[Sequence[str], float], str],
    top_n: int,
) -> Iterable[str]:
    out_strs = []
    last_count: Optional[float] = None
    place_count = 1
    cur_ties = []
    for item, count in sorted_vals:
        if last_count is None:
            last_count = count

        if last_count == count:
            if isinstance(item, Book):
                cur_ties.append(format_book(item))
            elif isinstance(item, SquareName):
                cur_ties.append(format_square(item))
            elif isinstance(item, Author):
                cur_ties.append(item)
            else:
                raise TypeError(f"Unhandled top-list type {type(item)} for {item}")
        else:
            out_strs.append(format_template(cur_ties, last_count))

            place_count += 1
            if place_count > top_n:
                break

            cur_ties = []
            if isinstance(item, Book):
                cur_ties.append(format_book(item))
            elif isinstance(item, SquareName):
                cur_ties.append(format_square(item))
            elif isinstance(item, Author):
                cur_ties.append(item)
            else:
                raise TypeError(f"Unhandled top-list type {type(item)} for {item}")

        last_count = count
    return out_strs


def format_top_book_counts(unique_books: Counter[Book], top_n: int = 10) -> str:
    """Format counts of top N unique reads"""

    def formatter(cur_ties: Sequence[str], count: float) -> str:
        if len(cur_ties) == 1:
            return "- " + cur_ties[0] + f", read {count} times"
        if len(cur_ties) > 1:
            return "- TIE: " + " and ".join(cur_ties) + f", each read {count} times"
        raise ValueError("No results?")

    book_count_strs = format_top_list_with_ties(unique_books.most_common(), formatter, top_n)

    return "\n".join(book_count_strs)


def format_bottom_square_counts(bingo_stats: BingoStatistics, bottom_n: int = 3) -> str:
    """Format most-incomplete squares"""

    def formatter(cur_ties: Sequence[str], count: float) -> str:
        if len(cur_ties) > 1:
            return " and ".join(cur_ties) + f", blank on {count} cards each"
        if len(cur_ties) == 1:
            return "".join(cur_ties) + f", blank on {count} cards"
        raise ValueError("No results?")

    incomplete_square_strs = format_top_list_with_ties(
        bingo_stats.incomplete_squares.most_common(), formatter, bottom_n
    )

    return "; ".join(incomplete_square_strs)


def format_dedupe_counts(bingo_stats: BingoStatistics, top_n: int = 10) -> str:
    """Format the counts of book variations"""

    def formatter(cur_ties: Sequence[str], count: float) -> str:
        if len(cur_ties) == 1:
            return "- " + cur_ties[0] + f", with {count} variations"
        if len(cur_ties) > 1:
            return "- TIE: " + " and ".join(cur_ties) + f", with {count} variations each"

        raise ValueError("No results?")

    book_vars = format_top_list_with_ties(
        bingo_stats.bad_spellings_by_book.most_common(), formatter, top_n
    )

    book_str = "\n".join(book_vars)

    return f"""The books with the most variation in title or author spellings were:

{book_str}"""


def format_most_subbed_squares(subbed_squares: Counter[SquareName], top_n: int = 3) -> str:
    """Format the sqaure subbed most often"""

    def formatter(cur_ties: Sequence[str], count: float) -> str:
        if len(cur_ties) > 1:
            return " and ".join(cur_ties) + f", substituted on {count} cards each"
        if len(cur_ties) == 1:
            return "".join(cur_ties) + f", substituted on {count} cards"
        raise ValueError("No results?")

    subbed_square_strs = format_top_list_with_ties(subbed_squares.most_common(), formatter, top_n)

    return "; ".join(subbed_square_strs)


def format_top_author_counts(unique_authors: Counter[Author], top_n: int = 10) -> str:
    """Format counts of top N unique authors"""

    def formatter(cur_ties: Sequence[str], count: float) -> str:
        if len(cur_ties) == 1:
            return "- " + cur_ties[0] + f", read {count} times"
        if len(cur_ties) > 1:
            return "- TIE: " + " and ".join(cur_ties) + f", each read {count} times"
        raise ValueError("No results?")

    author_count_strs = format_top_list_with_ties(unique_authors.most_common(), formatter, top_n)

    return "\n".join(author_count_strs)


def format_most_square_books(unique_squares_by_book: Counter[Book], top_n: int = 3) -> str:
    """Format the books used for the most different squares"""

    def formatter(cur_ties: Sequence[str], count: float) -> str:
        if len(cur_ties) == 1:
            return "- " + cur_ties[0] + f", used for {count} squares"
        if len(cur_ties) > 1:
            return "- TIE: " + " and ".join(cur_ties) + f", each used for {count} squares"
        raise ValueError("No results?")

    book_strs = format_top_list_with_ties(unique_squares_by_book.most_common(), formatter, top_n)

    return "\n".join(book_strs)


def format_most_square_authors(unique_squares_by_author: Counter[Author], top_n: int = 3) -> str:
    """Format the authors used for the most different squares"""

    def formatter(cur_ties: Sequence[str], count: float) -> str:
        if len(cur_ties) == 1:
            return "- " + cur_ties[0] + f", used for {count} squares"
        if len(cur_ties) > 1:
            return "- TIE: " + " and ".join(cur_ties) + f", each used for {count} squares"
        raise ValueError("No results?")

    book_strs = format_top_list_with_ties(unique_squares_by_author.most_common(), formatter, top_n)

    return "\n".join(book_strs)


def format_unique_author_books(books_per_author: Counter[Author], top_n: int = 10) -> str:
    """Format the counts of author varieties"""

    def formatter(cur_ties: Sequence[str], count: float) -> str:
        if len(cur_ties) == 1:
            return "- " + cur_ties[0] + f", with {count} unique books read"
        if len(cur_ties) > 1:
            return "- TIE: " + " and ".join(cur_ties) + f", each with {count} unique books read"
        raise ValueError("No results?")

    book_strs = format_top_list_with_ties(books_per_author.most_common(), formatter, top_n)

    return "\n".join(book_strs)


def format_favorite_square(
    bingo_stats: BingoStatistics,
    square_names: Container[SquareName] | Iterable[SquareName],
) -> str:
    """Format square completed most often"""
    fewest_incomplete = min(
        incomplete
        for square, incomplete in bingo_stats.incomplete_squares.items()
        if square in square_names
    )
    most_filled_squares = []
    for square_name, incomplete_count in bingo_stats.incomplete_squares.items():
        if incomplete_count == fewest_incomplete and square_name in square_names:
            most_filled_squares.append(square_name)

    multiple_favorites = len(most_filled_squares) > 1
    if multiple_favorites:
        fave_str = (
            ", ".join(format_square(square_name) for square_name in most_filled_squares[:-1])
            + f", and {format_square(most_filled_squares[-1])}"
        )
    else:
        fave_str = format_square(most_filled_squares[0])

    return (
        f"{fave_str} {'were' * multiple_favorites}{'was' * (not multiple_favorites)} "
        + f"only left blank {fewest_incomplete} "
        + f"time{'s'*(fewest_incomplete != 1)}{' each' * multiple_favorites}"
    )


def format_least_subbed_square(
    subbed_squares: Counter[SquareName],
    square_names: Container[SquareName] | Iterable[SquareName],
) -> str:
    """Format the string for the least-subbed bingo square"""
    fewest_subbed = min(subbed_squares.values())
    fewest_subbed_squares = []
    for square_name, subbed_count in subbed_squares.items():
        if subbed_count == fewest_subbed and square_name in square_names:
            fewest_subbed_squares.append(square_name)

    multiple_low_subs = len(fewest_subbed_squares) > 1
    if multiple_low_subs:
        low_sub_string = (
            ", ".join(format_square(square_name) for square_name in fewest_subbed_squares[:-1])
            + f"{',' * (len(fewest_subbed_squares) > 2)} and {format_square(fewest_subbed_squares[-1])}"
        )
    else:
        low_sub_string = format_square(fewest_subbed_squares[0])

    if fewest_subbed == 0:
        return f"{low_sub_string} {'were' * multiple_low_subs}{'was' * (not multiple_low_subs)} never substituted"
    return (
        f"{low_sub_string} {'were' * multiple_low_subs}{'was' * (not multiple_low_subs)} "
        + f"only left blank {fewest_subbed} time{'s'*(fewest_subbed != 1)}{' each' * multiple_low_subs}"
    )


def format_square_stats(
    square_num: int,
    square_name: SquareName,
    bingo_stats: BingoStatistics,
) -> str:
    """Format stats for a single square"""
    square_uniques = bingo_stats.square_uniques[square_name]
    return f"""### {square_num}. {square_name}

#### Most Read Books

{format_top_book_counts(square_uniques.unique_books, 5)}

**TOTAL**: {square_uniques.unique_books.total()} books read, with {len(square_uniques.unique_books)} unique titles.
{bingo_stats.hard_mode_by_square[square_name]} books were claimed to qualify for hard mode.
{get_used_once(square_uniques.unique_books)} books were used only once for this square.
Skipped {bingo_stats.incomplete_squares[square_name]} times. Substituted {bingo_stats.subbed_out_squares[square_name]} times.

#### Most Read Authors

{format_top_author_counts(square_uniques.unique_authors, 5)}

**TOTAL**: {square_uniques.unique_authors.total()} total authors read, with {len(square_uniques.unique_authors)} unique.
{get_used_once(square_uniques.unique_authors)} authors were used only once for this square.
"""


def format_all_squares(
    bingo_stats: BingoStatistics,
    square_names: Iterable[SquareName],
) -> str:
    """Format stats for every square"""
    square_strs = []
    for square_num, square_name in enumerate(square_names):
        square_strs.append(format_square_stats(square_num + 1, square_name, bingo_stats))
    return "\n".join(square_strs)


def format_farragini(
    bingo_stats: BingoStatistics,
    square_names: Iterable[SquareName],
    top_n: int = 3,
) -> str:
    """Format a table of FarraGini indices"""
    table_strs: list[tuple[str, str, str]] = [
        ("SQUARE", "BOOK", "AUTHOR"),
        ("---------", ":---------:", ":---------:"),
    ]
    book_ginis = {}
    author_ginis = {}
    for square_name in square_names:
        book_gini = (
            calculate_gini_index(
                tuple(bingo_stats.square_uniques[square_name].unique_books.values())
            )
            * 100
        )
        author_gini = (
            calculate_gini_index(
                tuple(bingo_stats.square_uniques[square_name].unique_authors.values())
            )
            * 100
        )
        book_ginis[square_name] = book_gini
        author_ginis[square_name] = author_gini
        table_strs.append((square_name, f"{book_gini:.1f}", f"{author_gini:.1f}"))

    highest_book_ginis = sorted(book_ginis.items(), key=lambda item: item[1], reverse=True)
    highest_author_ginis = sorted(author_ginis.items(), key=lambda item: item[1], reverse=True)

    def formatter(cur_ties: Sequence[str], _: float) -> str:
        if len(cur_ties) == 1:
            return "- " + cur_ties[0]
        if len(cur_ties) > 1:
            return "- TIE: " + " and ".join(cur_ties)
        raise ValueError("No results?")

    high_book_gini_strs = format_top_list_with_ties(highest_book_ginis, formatter, top_n)
    low_book_gini_strs = format_top_list_with_ties(reversed(highest_book_ginis), formatter, top_n)
    high_author_gini_strs = format_top_list_with_ties(highest_author_ginis, formatter, top_n)
    low_author_gini_strs = format_top_list_with_ties(
        reversed(highest_author_ginis), formatter, top_n
    )

    table_str = "\n".join("|" + "|".join(row) + "|" for row in table_strs)
    low_book_gini_str = "The squares with the most variety in books:\n" + "\n".join(
        low_book_gini_strs
    )
    low_author_gini_str = "The squares with the most variety in authors:\n" + "\n".join(
        low_author_gini_strs
    )
    high_book_gini_str = "The squares with the least variety in books:\n" + "\n".join(
        high_book_gini_strs
    )
    high_author_gini_str = "The squares with the least variety in authors:\n" + "\n".join(
        high_author_gini_strs
    )
    return (
        table_str
        + "\n\n"
        + low_book_gini_str
        + "\n\n"
        + low_author_gini_str
        + "\n\n"
        + high_book_gini_str
        + "\n\n"
        + high_author_gini_str
    )


def format_square_table(
    bingo_stats: BingoStatistics,
    square_names: Iterable[SquareName],
) -> str:
    """Format a table of FarraGini indices"""
    table_strs: list[tuple[str, str, str]] = [
        ("SQUARE", "% COMPLETE", "% HARD MODE"),
        ("---------", ":---------:", ":---------:"),
    ]
    total_cards = bingo_stats.total_card_count
    for square_name in square_names:
        total_cards_with_square = total_cards - bingo_stats.subbed_out_squares[square_name]
        table_strs.append(
            (
                square_name,
                f"{100 - bingo_stats.incomplete_squares[square_name]/total_cards_with_square*100:.1f}",
                f"{bingo_stats.hard_mode_by_square[square_name]/total_cards_with_square*100:.1f}",
            )
        )
    return "\n".join("|" + "|".join(row) + "|" for row in table_strs)


def format_subbed_stats(bingo_stats: BingoStatistics) -> str:
    """Format stats on squares that were subbed for others"""

    subbed_in_squares = Counter(subbed_in for _, subbed_in in bingo_stats.subbed_squares.keys())

    subbed_in_books: Counter[Book] = Counter()
    subbed_in_authors: Counter[Author] = Counter()
    for square_name in subbed_in_squares:
        books = bingo_stats.square_uniques[square_name].unique_books
        authors = bingo_stats.square_uniques[square_name].unique_authors
        subbed_in_books += books
        subbed_in_authors += authors

    return f"""Out of {bingo_stats.total_card_count} cards, {bingo_stats.subbed_out_squares.total()} used the Substitution rule.

### Books

{format_top_book_counts(subbed_in_books, 3)}

### Authors

{format_top_author_counts(subbed_in_authors, 3)}

### Squares

{format_most_subbed_squares(subbed_in_squares, 3)}."""


def get_used_once(unique_counts: Counter[BookOrAuthor]) -> int:
    return Counter(unique_counts.values())[1]


def get_single_ties(
    ranked_vals: Sequence[tuple[BingoName, int]],
    high_or_low: Literal["high", "low"],
) -> tuple[Sequence[BingoName], int]:
    if high_or_low == "high":
        index = 0
    else:
        index = -1
    cur_top, top_count = ranked_vals[index]
    cur_count = top_count
    all_tops = []
    while cur_count == top_count:
        all_tops.append(cur_top)
        if index >= 0:
            index += 1
        else:
            index -= 1
        cur_top, cur_count = ranked_vals[index]

    return all_tops, top_count


def format_inline_bingo_ties(
    ties: Sequence[str],
    hard_or_easy: Literal["hard", "easi"],
    card_or_square: Literal["card", "square"],
) -> str:
    multiples = len(ties) > 1
    if multiples:
        fave_str = (
            ", ".join(bingo_name for bingo_name in ties[:-1])
            + f"{','*(len(ties)>2)} and {ties[-1]}"
        )
    else:
        fave_str = ties[0]

    return (
        f"The {hard_or_easy}est bingo{'s'*multiples} by number of {card_or_square}s"
        + f" {'were' * multiples}{'was' * (not multiples)} {fave_str}"
    )


def format_bingos(
    bingo_type_stats: BingoTypeStatistics,
    incomplete_cards: Collection[CardID],
) -> str:

    total_nonblackout_bingos = 0
    for card_id in incomplete_cards:
        total_nonblackout_bingos += bingo_type_stats.complete_bingos_by_card[card_id]

    ranked_bingos_by_card = bingo_type_stats.incomplete_bingos.most_common()
    ranked_bingos_by_squares = bingo_type_stats.incomplete_squares_by_bingo.most_common()

    hardest_bingos_by_card, hardest_bingo_by_card_count = get_single_ties(
        ranked_bingos_by_card, "high"
    )
    hardest_bingos_by_square, hardest_bingo_by_square_count = get_single_ties(
        ranked_bingos_by_squares, "high"
    )
    easiest_bingos_by_card, easiest_bingo_by_card_count = get_single_ties(
        ranked_bingos_by_card, "low"
    )
    easiest_bingos_by_square, easiest_bingo_by_square_count = get_single_ties(
        ranked_bingos_by_squares, "low"
    )

    cards_per_complete_bingo = Counter(bingo_type_stats.complete_bingos_by_card.values())

    bingo_str = f"""
There were {bingo_type_stats.complete_bingos_by_card.total()} complete bingos.
Non-blackout cards completed an average of {total_nonblackout_bingos/len(incomplete_cards):.1f} bingos.
There were {cards_per_complete_bingo[0]} cards that did not complete any bingos.

{format_inline_bingo_ties(hardest_bingos_by_card, 'hard', 'card')}, incomplete on {hardest_bingo_by_card_count} cards.
{format_inline_bingo_ties(hardest_bingos_by_square, 'hard', 'square')}, with a total of {hardest_bingo_by_square_count} squares left blank.

{format_inline_bingo_ties(easiest_bingos_by_card, 'easi', 'card')}, incomplete on {easiest_bingo_by_card_count} cards.
{format_inline_bingo_ties(easiest_bingos_by_square, 'easi', 'square')}, with a total of {easiest_bingo_by_square_count} squares left blank.

"""

    table_strs: list[tuple[str, str, str]] = [
        ("BINGO TYPE", "INCOMPLETE CARDS", "INCOMPLETE SQUARES"),
        ("---------", ":---------:", ":---------:"),
    ]
    for bingo_name in POSSIBLE_BINGOS.keys():
        table_strs.append(
            (
                bingo_name,
                str(bingo_type_stats.incomplete_bingos[bingo_name]),
                str(bingo_type_stats.incomplete_squares_by_bingo[bingo_name]),
            )
        )

    return bingo_str + "\n".join("|" + "|".join(row) + "|" for row in table_strs)


def create_markdown(bingo_stats: BingoStatistics, card_data: CardData, output_path: Path) -> None:
    """Create a Markdown draft of stats"""

    most_avoided_square, most_avoided_count = bingo_stats.avoided_squares.most_common(1)[0]
    fav_index = 0
    least_avoided_square = ""
    while least_avoided_square not in card_data.square_names.values():
        fav_index -= 1
        least_avoided_square, least_avoided_count = bingo_stats.avoided_squares.most_common()[
            fav_index
        ]

    max_ratio = 0.0
    for book, square_count in bingo_stats.unique_squares_by_book.items():
        total_count = bingo_stats.overall_uniques.unique_books[book]
        if total_count >= 10:
            count_ratio = square_count / total_count
            if count_ratio > max_ratio:
                max_ratio = count_ratio
                max_square_ratio_book = book

    max_ratio = 0.0
    for author, square_count in bingo_stats.unique_squares_by_author.items():
        total_count = bingo_stats.overall_uniques.unique_authors[author]
        if total_count >= 10:
            count_ratio = square_count / total_count
            if count_ratio > max_ratio:
                max_ratio = count_ratio
                max_square_ratio_author = author

    mean_uniques = np.mean(list(bingo_stats.card_uniques.values()))

    hard_mode_by_card_counts = Counter(bingo_stats.hard_mode_by_card.values())

    avg_hm = np.mean(list(bingo_stats.hard_mode_by_card.values()))

    avg_reads_per_book = np.mean(list(bingo_stats.overall_uniques.unique_books.values()))
    avg_reads_per_author = np.mean(list(bingo_stats.overall_uniques.unique_authors.values()))

    markdown_lines = f"""# Preliminary Notes

Most of this post, and all of these statistics, were generated by a script I wrote, [available on GitHub](https://github.com/smartflutist661/rfantasy-bingo-stats),
Anyone is welcome to view the enhancments I currently have in mind, request new statistics, or contribute there.
You can find the raw data, corrected data, and some more extensive summary statistics at that link, as well.
See [this post](https://www.reddit.com/r/Fantasy/comments/12gyb45/cleaning_2022_and_future_bingo_data/) for some technical details.

Format has been shamelessly copied from previous bingo stats posts:

  - [2022](https://www.reddit.com/r/Fantasy/comments/12xs3c1/2022_rfantasy_bingo_statistics/)
  - [2021](https://www.reddit.com/r/Fantasy/comments/ude8f4/2021_rfantasy_bingo_stats/)
  - [2020](https://www.reddit.com/r/Fantasy/comments/npvigf/2020_rfantasy_bingo_statistics/)
  - [2019](https://www.reddit.com/r/Fantasy/comments/gjq0ym/2019_rfantasy_bingo_statistics/)
  - [2018](https://www.reddit.com/r/Fantasy/comments/bbm35a/2018_rfantasy_bingo_statistics/)
  - [2017](https://www.reddit.com/r/Fantasy/comments/89esvx/2017_fantasy_bingo_statistics/)
  - [2016](https://www.reddit.com/r/Fantasy/comments/62sp9h/2016_fantasy_bingo_statistics/)

Likewise, the following notes are shamelessly adapted.

1. Stories were not examined for fitness. If you used **1984** for **Novella**, it was included in the statistics for that square.
In addition, if you did something like, say, put **The Lost Metal** as a short story, I made no effort to figure out where it actually belonged.
2. When a series was specified, it was collapsed to the first book. Graphic novels, light novels, manga, and webserials were collapsed from issues to the overall series.
3. Books by multiple authors were counted once for each author. E.g.: **In the Heart of Darkness** by Eric Flint and David Drake counts as a read for both Eric Flint and David Drake.
*However*, books by a writing team with a single-author pseudonym, e.g. M.A. Carrick, were counted once for the pseudonym, and not for the authors behind the pseudonym.
4. Author demographic statistics are not included below, for two reasons: it quickly gets messy and culturally-specific,
and I didn't want to stalk all {len(bingo_stats.overall_uniques.unique_authors)} individual authors. Machinery for these calculations are included in the script, however,
so if anyone would like to supply demographic information, it is easy to include.
5. Short stories were excluded from most of the stats below. They *were* included in the total story count.

# And Now: The Stats
    
## Overall Stats

### Squares and Cards

- There were {bingo_stats.total_card_count} cards submitted, {len(bingo_stats.incomplete_cards)} of which were incomplete.
The minimum number of filled squares was {25 - bingo_stats.max_incomplete_squares}. {bingo_stats.incomplete_squares_per_card[1]} were *this close*, with 24 filled squares.
{bingo_stats.incomplete_squares.total()} squares were left blank, leaving {bingo_stats.total_card_count*25 - bingo_stats.incomplete_cards.total()} filled squares.
- There were {bingo_stats.total_story_count} total stories, with {len(bingo_stats.overall_uniques.unique_books)} unique stories read,
by {len(bingo_stats.overall_uniques.unique_authors)} unique authors ({bingo_stats.overall_uniques.unique_authors.total()} total).
{get_used_once(bingo_stats.overall_uniques.unique_books)} books and {get_used_once(bingo_stats.overall_uniques.unique_authors)} authors were used only once. 
- The top squares left blank were: {format_bottom_square_counts(bingo_stats)}. On the other hand, {format_favorite_square(bingo_stats, card_data.square_names.values())}.
- The three squares most often substituted were: {format_most_subbed_squares(bingo_stats.subbed_out_squares)}.
{format_least_subbed_square(bingo_stats.subbed_out_squares, card_data.square_names.values())}.
This means that {most_avoided_square} was the least favorite overall, skipped or substituted a total of {most_avoided_count} times, and
{least_avoided_square} was the favorite, skipped or substituted only {least_avoided_count} times.
- There were an average of {mean_uniques:.1f} unique books per card.
- {hard_mode_by_card_counts[25]} cards claimed an all-hard-mode card, while {hard_mode_by_card_counts[24]} cards were short by one square.
{hard_mode_by_card_counts[0]} cards claimed no hard-mode squares at all. The average number of hard-mode squares per card was {avg_hm:.1f}.
There were a total of {bingo_stats.hard_mode_by_square.total()} hard-mode squares claimed.

{format_square_table(bingo_stats, card_data.square_names.values())}

<INSERT PLOTS HERE>

### Books

The ten most-read books were:

{format_top_book_counts(bingo_stats.overall_uniques.unique_books)}

The books used for the most squares were:

{format_most_square_books(bingo_stats.unique_squares_by_book)}

{format_book(max_square_ratio_book)} was the book read at least 10 times with the highest ratio of squares to times read:
read {bingo_stats.overall_uniques.unique_books[max_square_ratio_book]} times for {bingo_stats.unique_squares_by_book[max_square_ratio_book]} squares.

<INSERT PLOT HERE>

One of those interesting stats phenomena: even though most cards only include a few unique books, most of the books read are unique.
There were an average of {avg_reads_per_book:.1f} reads per book.

### Authors

The ten most-read authors were:

{format_top_author_counts(bingo_stats.overall_uniques.unique_authors)}

The authors used for the most squares were:

{format_most_square_authors(bingo_stats.unique_squares_by_author)}

{max_square_ratio_author} was the author read at least 10 times with the highest ratio of squares to times read:
read {bingo_stats.overall_uniques.unique_authors[max_square_ratio_author]} times for {bingo_stats.unique_squares_by_author[max_square_ratio_author]} squares.

The authors with the most unique books read were:

{format_unique_author_books(bingo_stats.books_per_author)}

<INSERT_PLOT_HERE>

As with books, most authors were read only once.
There were an average of {avg_reads_per_author:.1f} reads per author.

### Bingos

#### Normal Mode
{format_bingos(bingo_stats.normal_bingo_type_stats, bingo_stats.incomplete_cards.keys())}

#### Hard Mode
{format_bingos(bingo_stats.hardmode_bingo_type_stats, [card_id for card_id, hm_count in bingo_stats.hard_mode_by_card.items() if hm_count != BINGO_SIZE**2])}

## Stats for Individual Squares

{format_all_squares(bingo_stats, card_data.square_names.values())}
## Substitutions

{format_subbed_stats(bingo_stats)}

## Variety

The FarraGini index, [introduced in 2017](https://www.reddit.com/r/Fantasy/comments/89esvx/2017_fantasy_bingo_statistics/) (see Part III),
attempts to measure the variety of books and authors read for each square.
Each entity's "income" for a square is the number of times it was used for that square,
so the index is analogous to its namesake, the [Gini index](https://en.wikipedia.org/wiki/Gini_coefficient):

Values close to 0 suggest a square was well-varied; 0 means no book was repeated for a square.
Values close to 100 suggest the same books were used repeatedly for a square; 100 means only one book was used for a square.

{format_farragini(bingo_stats, card_data.square_names.values())}

<INSERT COMMENTARY HERE>

## Year Over Year Changes

New this year: year-over-year statistics! For numbers from before 2022, I have scavenged from previous stats and data posts.

<INSERT PLOTS HERE>

## Wall of Shame

Quoting the [very first bingo stats post](https://www.reddit.com/r/Fantasy/comments/62sp9h/2016_fantasy_bingo_statistics/),

> You are all terrible spellers.

A "misspelling" for the purposes of these statistics is any book (title/author combination)
that does not match the version used as the canonical version during cleaning.
There were a total of {bingo_stats.bad_spellings_by_card.total()} misspellings.
(Note that this does not include short stories.)

{format_dedupe_counts(bingo_stats)}

What makes a book hard to "spell" correctly?

- Length
- Lots of articles or prepositions
- Non-ASCII characters
- Lots of authors
- Numbers
- Somewhat obviously, books that were published under multiple titles

Predictably, there's a lot of crossover between books with the most variations and the most-read books overall.
"""

    LOGGER.info(f"Markdown output:\n\n{markdown_lines}")

    with output_path.open("w", encoding="utf8") as md_file:
        md_file.write(markdown_lines)
