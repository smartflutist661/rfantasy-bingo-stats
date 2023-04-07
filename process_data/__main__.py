"""
Created on Apr 7, 2023

@author: fred
"""
import argparse

from .constants import BINGO_DATA_FILEPATH
from .get_data import (
    get_bingo_dataframe,
    get_unique_title_author_combos,
)
from .get_matches import get_possible_matches


def main(args: argparse.Namespace) -> None:
    """Process bingo data"""
    bingo_data = get_bingo_dataframe(BINGO_DATA_FILEPATH)

    print(
        "Processing possible misspellings."
        + " You may hit ctrl+C at any point to exit, or enter `e` at the prompt."
        + " Progress will be saved."
    )

    unique_pairs = get_unique_title_author_combos(bingo_data)

    get_possible_matches(unique_pairs, args.match_score)


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

    return parser.parse_args()


if __name__ == "__main__":
    main(cli())
