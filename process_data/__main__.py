"""
Created on Apr 7, 2023

@author: fred
"""
import argparse

from .constants import BINGO_DATA_FILEPATH
from .get_data import (
    get_all_title_author_combos,
    get_bingo_dataframe,
    get_title_author_colpairs,
    get_unique_books,
)
from .get_matches import get_possible_matches
from .update_data import update_bingo_dataframe
from collections import Counter


def main(args: argparse.Namespace) -> None:
    """Process bingo data"""
    bingo_data = get_bingo_dataframe(BINGO_DATA_FILEPATH)

    print(
        "Processing possible misspellings."
        + " You may hit ctrl+C at any point to exit, or enter `e` at the prompt."
        + " Progress will be saved."
    )
    print()

    title_author_colpairs = get_title_author_colpairs(bingo_data)
    all_title_author_combos = get_all_title_author_combos(bingo_data, title_author_colpairs)

    unique_books = get_unique_books(all_title_author_combos)

    print(f"Starting with {len(unique_books)} unique books.")

    vals_to_replace = get_possible_matches(unique_books, args.match_score, args.rescan_non_dupes)

    update_bingo_dataframe(bingo_data, vals_to_replace, title_author_colpairs)

    all_title_author_combos = get_all_title_author_combos(bingo_data, title_author_colpairs)
    updated_unique_books = get_unique_books(all_title_author_combos)

    print(f"Updated data has {len(updated_unique_books)} unique books.")

    book_count = Counter(all_title_author_combos)

    print(f"The ten most-read books were {book_count.most_common(10)}.")


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
