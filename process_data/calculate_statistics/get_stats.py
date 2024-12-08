"""
Created on Apr 7, 2023

@author: fred
"""
from collections import Counter

import pandas

from ..data.current import (
    OUTPUT_MD_FILEPATH,
    SQUARE_NAMES,
)
from ..data_operations.author_title_book_operations import (
    get_all_title_author_combos,
    get_unique_title_author_counts,
)
from ..types.bingo_statistics import BingoStatistics
from ..types.defined_types import (
    SquareName,
    TitleAuthor,
)
from .get_bingo_cards import get_bingo_cards


def get_summary_statistics(bingo_data: pandas.DataFrame) -> BingoStatistics:
    """Do preliminary math and prepare to save to file"""
    all_title_authors = get_all_title_author_combos(bingo_data)
    unique_title_author_counts = get_unique_title_author_counts(all_title_authors)

    unique_author_counts = Counter(author for _, author in unique_title_author_counts.keys())

    bingo_cards, subbed_squares, incomplete_cards, incomplete_squares = get_bingo_cards(bingo_data)

    assert incomplete_cards.total() == incomplete_squares.total()

    subbed_out_squares = Counter(subbed_out for subbed_out, _ in subbed_squares.keys())

    return BingoStatistics(
        total_card_count=len(bingo_cards),
        incomplete_cards=incomplete_cards,
        incomplete_squares=incomplete_squares,
        max_incomplete_squares=max(
            incomplete for incomplete in incomplete_cards.values() if incomplete != 25
        ),
        incomplete_squares_per_card=Counter(incomplete_cards.values()),
        total_incomplete_squares=incomplete_cards.total(),
        total_story_count=len(all_title_authors),
        unique_title_authors=unique_title_author_counts,
        unique_story_count=len(unique_title_author_counts),
        unique_authors=unique_author_counts,
        unique_author_count=len(unique_author_counts),
        subbed_squares=subbed_squares,
        subbed_out_squares=subbed_out_squares,
        avoided_squares=incomplete_squares + subbed_out_squares,
    )


def format_title_author(title_author: TitleAuthor) -> str:
    """Format a title/author pair into a string"""
    return f"**{title_author[0]}**, by {title_author[1]}"


def format_square(square_name: SquareName) -> str:
    """Format a square name"""
    return f"**{square_name}**"


def format_top_book_counts(bingo_stats: BingoStatistics, top_n: int = 10) -> str:
    """Format counts of top N unique reads"""
    book_count_strs = []
    for title_author, count in bingo_stats.unique_title_authors.most_common(top_n):
        book_count_strs.append(f"* {format_title_author(title_author)}, read {count} times")
    return "\n".join(book_count_strs)


def format_bottom_square_counts(bingo_stats: BingoStatistics, bottom_n: int = 3) -> str:
    """Format most-incomplete squares"""
    incomplete_square_strs = []
    for incomplete_square, blank_count in bingo_stats.incomplete_squares.most_common(bottom_n):
        incomplete_square_strs.append(
            f"{format_square(incomplete_square)}, blank on {blank_count} cards"
        )
    return "; ".join(incomplete_square_strs)


def format_favorite_square(bingo_stats: BingoStatistics) -> str:
    """Format square completed most often"""
    fewest_incomplete = min(
        incomplete
        for square, incomplete in bingo_stats.incomplete_squares.items()
        if square in SQUARE_NAMES.values()
    )
    most_filled_squares = []
    for square_name, incomplete_count in bingo_stats.incomplete_squares.items():
        if incomplete_count == fewest_incomplete and square_name in SQUARE_NAMES.values():
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
        + f"time{'s'*(fewest_incomplete > 1)}{' each' * multiple_favorites}"
    )


def format_most_subbed_squares(bingo_stats: BingoStatistics, top_n: int = 3) -> str:
    """Format the sqaure subbed most often"""
    subbed_square_strs = []
    for subbed_square, subbed_count in bingo_stats.subbed_out_squares.most_common(top_n):
        subbed_square_strs.append(
            f"{format_square(subbed_square)}, substituted on {subbed_count} cards"
        )
    return "; ".join(subbed_square_strs)


def format_least_subbed_square(bingo_stats: BingoStatistics) -> str:
    """Format the string for the least-subbed bingo square"""
    fewest_subbed = min(bingo_stats.subbed_out_squares.values())
    fewest_subbed_squares = []
    for square_name, subbed_count in bingo_stats.subbed_out_squares.items():
        if subbed_count == fewest_subbed and square_name in SQUARE_NAMES.values():
            fewest_subbed_squares.append(square_name)

    multiple_low_subs = len(fewest_subbed_squares) > 1
    if multiple_low_subs:
        low_sub_string = (
            ", ".join(format_square(square_name) for square_name in fewest_subbed_squares[:-1])
            + f", and {format_square(fewest_subbed_squares[-1])}"
        )
    else:
        low_sub_string = format_square(fewest_subbed_squares[0])

    return (
        f"{low_sub_string} {'were' * multiple_low_subs}{'was' * (not multiple_low_subs)} "
        + f"only left blank {fewest_subbed} time{'s'*(fewest_subbed > 1)}{' each' * multiple_low_subs}"
    )


def create_markdown(bingo_stats: BingoStatistics) -> None:
    """Create a Markdown draft of stats"""

    most_avoided_square, most_avoided_count = bingo_stats.avoided_squares.most_common(1)[0]

    markdown_lines = f"""## Overall Stats

* There were {bingo_stats.total_card_count} cards submitted, {len(bingo_stats.incomplete_cards)} of which were incomplete.
The minimum number of filled squares was {25 - bingo_stats.max_incomplete_squares}. {bingo_stats.incomplete_squares_per_card[1]} were *this close*, with 24 filled squares.
{bingo_stats.total_incomplete_squares} squares were left blank, leaving {bingo_stats.total_card_count*25 - bingo_stats.total_incomplete_squares} filled squares.
* There were {bingo_stats.total_story_count} total stories, with {bingo_stats.unique_story_count} unique stories read, by {bingo_stats.unique_author_count} unique authors.
* The top three squares left blank were: {format_bottom_square_counts(bingo_stats)}. On the other hand, {format_favorite_square(bingo_stats)}.
* The three squares most often substituted were: {format_most_subbed_squares(bingo_stats)}. {format_least_subbed_square(bingo_stats)}.

This means that {most_avoided_square} was the least favorite overall, skipped or substituted a total of {most_avoided_count} times.

The ten most-read books were:
{format_top_book_counts(bingo_stats)}
"""

    print()
    print(markdown_lines)

    with OUTPUT_MD_FILEPATH.open("w", encoding="utf8") as md_file:
        md_file.write(markdown_lines)
