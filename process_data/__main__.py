"""
Created on Apr 7, 2023

@author: fred
"""
import argparse
from collections import Counter

import pandas

from process_data.get_data import (
    books_to_title_authors,
    get_bingo_cards,
)

from .constants import (
    BINGO_DATA_FILEPATH,
    OUTPUT_MD_FILEPATH,
)
from .get_data import (
    get_all_title_author_combos,
    get_bingo_dataframe,
    get_unique_books,
)
from .get_matches import get_possible_matches
from .update_data import (
    add_to_markdown,
    update_bingo_dataframe,
)


def normalize_books(
    bingo_data: pandas.DataFrame,
    match_score: int,
    rescan_non_dupes: bool,
) -> None:
    """Normalize book titles and authors"""
    all_title_author_combos = get_all_title_author_combos(bingo_data)

    unique_books = get_unique_books(all_title_author_combos)

    print(f"Starting with {len(unique_books)} unique books.")

    print(
        "Processing possible misspellings."
        + " You may hit ctrl+C at any point to exit, or enter `e` at the prompt."
        + " Progress will be saved."
    )
    print()

    vals_to_replace = get_possible_matches(unique_books, match_score, rescan_non_dupes)

    update_bingo_dataframe(bingo_data, vals_to_replace)


# TODO: Collect many statistics based on old posts
def collect_statistics(bingo_data: pandas.DataFrame) -> None:
    """Collect statistics on normalized books"""
    all_title_authors = get_all_title_author_combos(bingo_data)
    unique_books = get_unique_books(all_title_authors)

    unique_authors = set()
    for _, author in books_to_title_authors(unique_books):
        unique_authors.add(author)

    markdown_lines: list[str] = []

    add_to_markdown(markdown_lines, "*Overall Stats*\n")

    bingo_cards, subbed_squares, incomplete_cards, incomplete_squares = get_bingo_cards(bingo_data)
    subbed_out_squares = Counter(subbed_out for subbed_out, _ in subbed_squares.keys())

    assert incomplete_cards.total() == incomplete_squares.total()

    total_card_count = len(bingo_cards)

    max_incomplete_squares = max(incomplete_cards.values())
    num_cards_almost_complete = Counter(
        num_incomplete for num_incomplete in incomplete_cards.values() if num_incomplete == 1
    )
    total_incomplete_squares = incomplete_cards.total()

    add_to_markdown(
        markdown_lines,
        f"* There were {total_card_count} cards submitted, {len(incomplete_cards)} of which were incomplete."
        + f" The minimum number of filled squares was {25 - max_incomplete_squares}."
        + f" {num_cards_almost_complete} were _this close_, with 24 filled squares."
        + f" {total_incomplete_squares} squares were left blank, leaving {total_card_count*25 - total_incomplete_squares} filled squares.",
    )

    add_to_markdown(
        markdown_lines,
        f"* There were {len(all_title_authors)} total stories, with {len(unique_books)} unique stories read,"
        + f" by {len(unique_authors)} unique authors.",
    )

    incomplete_count_counts = Counter(incomplete_squares.values())
    print(incomplete_count_counts[0])

    incomplete_square_strs = []
    for incomplete_square, blank_count in incomplete_squares.most_common(3):
        incomplete_square_strs.append(f"{incomplete_square}, blank on {blank_count} cards")
    incomplete_square_str = "; ".join(incomplete_square_strs)
    add_to_markdown(
        markdown_lines, f"* The top three squares left blank were {incomplete_square_str}. "
    )
    add_to_markdown(markdown_lines, f"* ")

    book_count = Counter(all_title_authors)

    print(f"The ten most-read books were {book_count.most_common(10)}.")

    with OUTPUT_MD_FILEPATH.open("w", encoding="utf8") as md_file:
        md_file.write("\n".join(markdown_lines))


def main(args: argparse.Namespace) -> None:
    """Process bingo data"""
    bingo_data = get_bingo_dataframe(BINGO_DATA_FILEPATH)

    normalize_books(bingo_data, args.match_score, args.rescan_non_dupes)

    collect_statistics(bingo_data)


def cli() -> argparse.Namespace:
    """Define command-line interface for this program"""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--match-score",
        type=int,
        default=90,
        help="""
        The minimum score to allow for a match. Fairly sensitive.
        Default = 90
        """,
    )

    parser.add_argument(
        "--rescan-non-dupes",
        action="store_true",
        help="""
        Pass this to check for duplicates on pairs that were previously not matched.
        Best paired with a lower `match-score` than the default.
        """,
    )

    return parser.parse_args()


if __name__ == "__main__":
    main(cli())
