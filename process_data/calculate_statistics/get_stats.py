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
from ..data_operations.update_data import add_to_markdown
from ..types.defined_types import (
    Author,
    Book,
    TitleAuthor,
)
from .get_bingo_cards import get_bingo_cards


def create_markdown(
    bingo_data: pandas.DataFrame,
    all_title_authors: tuple[TitleAuthor, ...],
    unique_authors: frozenset[Author],
    unique_books: frozenset[Book],
) -> None:
    """Create a Markdown draft of stats"""
    markdown_lines: list[str] = []

    print()
    add_to_markdown(markdown_lines, "**Overall Stats**\n")

    bingo_cards, subbed_squares, incomplete_cards, incomplete_squares = get_bingo_cards(bingo_data)

    assert incomplete_cards.total() == incomplete_squares.total()

    total_card_count = len(bingo_cards)

    max_incomplete_squares = max(
        incomplete for incomplete in incomplete_cards.values() if incomplete != 25
    )

    num_cards_almost_complete = Counter(incomplete_cards.values())
    total_incomplete_squares = incomplete_cards.total()

    add_to_markdown(
        markdown_lines,
        f"* There were {total_card_count} cards submitted, {len(incomplete_cards)} of which were incomplete."
        + f" The minimum number of filled squares was {25 - max_incomplete_squares}."
        + f" {num_cards_almost_complete[1]} were _this close_, with 24 filled squares."
        + f" {total_incomplete_squares} squares were left blank, leaving {total_card_count*25 - total_incomplete_squares} filled squares.",
    )

    add_to_markdown(
        markdown_lines,
        f"* There were {len(all_title_authors)} total stories, with {len(unique_books)} unique stories read,"
        + f" by {len(unique_authors)} unique authors.",
    )

    fewest_incomplete = min(
        incomplete
        for square, incomplete in incomplete_squares.items()
        if square in SQUARE_NAMES.values()
    )
    most_filled_squares = []
    for square_name, incomplete_count in incomplete_squares.items():
        if incomplete_count == fewest_incomplete and square_name in SQUARE_NAMES.values():
            most_filled_squares.append(square_name)

    multiple_favorites = len(most_filled_squares) > 1
    if multiple_favorites:
        favorite_square_string = (
            ", ".join(most_filled_squares[:-1]) + f", and {most_filled_squares[-1]}"
        )
    else:
        favorite_square_string = most_filled_squares[0]

    incomplete_square_strs = []
    for incomplete_square, blank_count in incomplete_squares.most_common(3):
        incomplete_square_strs.append(f"{incomplete_square}, blank on {blank_count} cards")
    incomplete_square_str = "; ".join(incomplete_square_strs)

    add_to_markdown(
        markdown_lines,
        f"* The top three squares left blank were: {incomplete_square_str}."
        + f" On the other hand, {favorite_square_string} {'were' * multiple_favorites}{'was' * (not multiple_favorites)}"
        + f" only left blank {fewest_incomplete} time{'s'*(fewest_incomplete > 1)}{' each' * multiple_favorites}.",
    )

    subbed_out_squares = Counter(subbed_out for subbed_out, _ in subbed_squares.keys())
    subbed_square_strs = []

    for subbed_square, subbed_count in subbed_out_squares.most_common(3):
        subbed_square_strs.append(f"{subbed_square}, substituted on {subbed_count} cards")
    subbed_square_str = "; ".join(subbed_square_strs)

    fewest_subbed = min(subbed_count for square, subbed_count in subbed_out_squares.items())
    fewest_subbed_squares = []
    for square_name, subbed_count in subbed_out_squares.items():
        if subbed_count == fewest_subbed and square_name in SQUARE_NAMES.values():
            fewest_subbed_squares.append(square_name)

    multiple_low_subs = len(fewest_subbed_squares) > 1
    if multiple_low_subs:
        low_sub_string = (
            ", ".join(fewest_subbed_squares[:-1]) + f", and {fewest_subbed_squares[-1]}"
        )
    else:
        low_sub_string = fewest_subbed_squares[0]

    add_to_markdown(
        markdown_lines,
        f"* The three squares most often substituted were: {subbed_square_str}."
        + f" {low_sub_string} {'were' * multiple_low_subs}{'was' * (not multiple_low_subs)}"
        + f" only left blank {fewest_subbed} time{'s'*(fewest_subbed > 1)}{' each' * multiple_low_subs}.\n",
    )
    total_avoidance = incomplete_squares + subbed_out_squares
    most_avoided_square, most_avoided_count = total_avoidance.most_common(1)[0]
    add_to_markdown(
        markdown_lines,
        f"This means that {most_avoided_square} was the least favorite overall,"
        + f" skipped or substituted a total of {most_avoided_count} times.\n",
    )

    book_count = Counter(all_title_authors)

    book_count_strs = []
    for title_author, count in book_count.most_common(10):
        book_count_strs.append(", by ".join(title_author) + f", read {count} times")
    book_count_str = "\n* ".join(book_count_strs)
    add_to_markdown(markdown_lines, f"The ten most-read books were\n\n* {book_count_str}")

    with OUTPUT_MD_FILEPATH.open("w", encoding="utf8") as md_file:
        md_file.write("\n".join(markdown_lines))
