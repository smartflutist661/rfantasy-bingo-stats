from collections import Counter
from collections.abc import (
    Callable,
    Container,
    Iterable,
    Sequence,
)
from dataclasses import dataclass
from enum import StrEnum
from typing import (
    Literal,
    Optional,
    TypeVar,
)

from rfantasy_bingo_stats.data_operations.author_title_book_operations import book_to_title_author
from rfantasy_bingo_stats.models.bingo_statistics import BingoStatistics
from rfantasy_bingo_stats.models.defined_types import (
    Author,
    BingoName,
    Book,
    BookOrAuthor,
    SquareName,
)


@dataclass
class SummaryStats:
    most_avoided: tuple[SquareName, int]
    least_avoided: tuple[SquareName, int]
    mean_uniques: float
    all_hm_count: int
    almost_hm_count: int
    no_hm_count: int
    avg_hm_per_card: float
    avg_reads_per_book: float
    avg_reads_per_author: float
    max_square_ratio_book: Book
    max_square_ratio_author: Author


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
            out_strs.append(format_template(sorted(cur_ties), last_count))

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
            return "- ***TIE***: " + " and ".join(cur_ties) + f", each read {count} times"
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
            return "- ***TIE***: " + " and ".join(cur_ties) + f", with {count} variations each"

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
            return "- ***TIE***: " + " and ".join(cur_ties) + f", each read {count} times"
        raise ValueError("No results?")

    author_count_strs = format_top_list_with_ties(unique_authors.most_common(), formatter, top_n)

    return "\n".join(author_count_strs)


def format_most_square_books(unique_squares_by_book: Counter[Book], top_n: int = 3) -> str:
    """Format the books used for the most different squares"""

    def formatter(cur_ties: Sequence[str], count: float) -> str:
        if len(cur_ties) == 1:
            return "- " + cur_ties[0] + f", used for {count} squares"
        if len(cur_ties) > 1:
            return "- ***TIE***: " + " and ".join(cur_ties) + f", each used for {count} squares"
        raise ValueError("No results?")

    book_strs = format_top_list_with_ties(unique_squares_by_book.most_common(), formatter, top_n)

    return "\n".join(book_strs)


def format_most_reads_per_square_books(
    unique_books: Counter[Book], unique_squares_by_book: Counter[Book], top_n: int = 3
) -> str:
    """Format the books used the most times per square"""
    reads_per_square = Counter(
        {book: reads / unique_squares_by_book[book] for book, reads in unique_books.items()}
    )

    def formatter(cur_ties: Sequence[str], count: float) -> str:
        if len(cur_ties) == 1:
            return "- " + cur_ties[0] + f", read {count} times per square"
        if len(cur_ties) > 1:
            return "- ***TIE***: " + " and ".join(cur_ties) + f", read {count} times per square"
        raise ValueError("No results?")

    book_strs = format_top_list_with_ties(reads_per_square.most_common(), formatter, top_n)

    return "\n".join(book_strs)


def format_most_square_authors(unique_squares_by_author: Counter[Author], top_n: int = 3) -> str:
    """Format the authors used for the most different squares"""

    def formatter(cur_ties: Sequence[str], count: float) -> str:
        if len(cur_ties) == 1:
            return "- " + cur_ties[0] + f", used for {count} squares"
        if len(cur_ties) > 1:
            return "- ***TIE***: " + " and ".join(cur_ties) + f", each used for {count} squares"
        raise ValueError("No results?")

    book_strs = format_top_list_with_ties(unique_squares_by_author.most_common(), formatter, top_n)

    return "\n".join(book_strs)


def format_unique_author_books(books_per_author: Counter[Author], top_n: int = 10) -> str:
    """Format the counts of author varieties"""

    def formatter(cur_ties: Sequence[str], count: float) -> str:
        if len(cur_ties) == 1:
            return "- " + cur_ties[0] + f", with {count} unique books read"
        if len(cur_ties) > 1:
            return (
                "- ***TIE***: " + " and ".join(cur_ties) + f", each with {count} unique books read"
            )
        raise ValueError("No results?")

    book_strs = format_top_list_with_ties(books_per_author.most_common(), formatter, top_n)

    return "\n".join(book_strs)


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
    fewest_subbed_squares.sort()

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
    most_filled_squares.sort()

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


StrEnumT = TypeVar("StrEnumT", bound=StrEnum)


def format_author_demo(
    overall_demo_count: Counter[StrEnumT],
    unique_demo_count: Counter[StrEnumT],
    demo_name: Literal["ETHNICITY", "GENDER", "NATIONALITY"],
) -> str:
    table_strs: list[tuple[str, str, str]] = [
        (demo_name, "% OVERALL", "% UNIQUE"),
        ("---------", ":---------:", ":---------:"),
    ]
    enum_type = type(list(overall_demo_count.keys())[0])
    for demo in sorted(set(overall_demo_count.keys()) - {"Unknown"}) + [enum_type("Unknown")]:  # type: ignore[arg-type]
        overall_prop = (overall_demo_count[demo] / overall_demo_count.total()) * 100
        unique_prop = (unique_demo_count[demo] / unique_demo_count.total()) * 100
        if demo_name != "NATIONALITY" or unique_prop > 1:
            table_strs.append(
                (
                    demo.value,
                    f"{overall_prop:.1f}",
                    f"{unique_prop:.1f}",
                )
            )
    return "\n".join("|" + "|".join(row) + "|" for row in table_strs)
