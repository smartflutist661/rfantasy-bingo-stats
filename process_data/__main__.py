"""
Created on Apr 7, 2023

@author: fred
"""
import argparse
import json

import numpy
import pandas

from .calculate_statistics.get_stats import (
    create_markdown,
    get_summary_statistics,
)
from .data.current import (
    BINGO_DATA_FILEPATH,
    OUTPUT_DF_FILEPATH,
    OUTPUT_STATS_FILEPATH,
)
from .data.filepaths import DUPE_RECORD_FILEPATH
from .data_operations.author_title_book_operations import (
    get_all_authors,
    get_all_title_author_combos,
    get_unique_authors,
    get_unique_books,
)
from .data_operations.get_data import (
    get_bingo_dataframe,
    get_existing_states,
)
from .data_operations.update_data import (
    comma_separate_authors,
    update_bingo_authors,
    update_bingo_books,
)
from .git_operations import (
    commit_push_pr,
    synchronize_github,
)
from .match_books.get_matches import (
    get_possible_matches,
    update_dedupes_from_authors,
)
from .types.recorded_states import RecordedStates


def normalize_books(
    bingo_data: pandas.DataFrame,
    match_score: int,
    rescan_non_dupes: bool,
    recorded_states: RecordedStates,
) -> None:
    """Normalize book titles and authors"""

    all_authors = get_all_authors(bingo_data)

    unique_authors = get_unique_authors(all_authors)

    print(f"Starting with {len(unique_authors)} unique authors.")

    print(
        "Processing possible misspellings."
        + " You may hit ctrl+C at any point to exit, or enter `e` at the prompt."
        + " Progress will be saved."
    )
    print()

    get_possible_matches(unique_authors, match_score, rescan_non_dupes, recorded_states, "Author")

    comma_separate_authors(recorded_states)

    print("Updating Bingo authors.")
    author_dedupes = update_bingo_authors(
        bingo_data, recorded_states.author_dupes, recorded_states.book_separator
    )
    print("Bingo authors updated.")

    all_title_author_combos = get_all_title_author_combos(bingo_data)

    unique_books = get_unique_books(all_title_author_combos, recorded_states.book_separator)

    print(f"Starting with {len(unique_books)} unique books.")

    print(
        "Processing possible misspellings."
        + " You may hit ctrl+C at any point to exit, or enter `e` at the prompt."
        + " Progress will be saved."
    )
    print()

    get_possible_matches(unique_books, match_score, rescan_non_dupes, recorded_states, "Book")

    print("Collecting all misspellings.")
    update_dedupes_from_authors(recorded_states, author_dedupes)

    print("Updating Bingo books.")
    update_bingo_books(bingo_data, recorded_states.book_dupes)
    print("Bingo books updated.")


def collect_statistics(bingo_data: pandas.DataFrame) -> None:
    """Collect statistics on normalized books and create a rough draft post"""

    bingo_stats = get_summary_statistics(bingo_data)

    with OUTPUT_STATS_FILEPATH.open("w", encoding="utf8") as stats_file:
        json.dump(bingo_stats.to_data(), stats_file, indent=2)

    create_markdown(bingo_stats)


def main(args: argparse.Namespace) -> None:
    """Process bingo data"""
    if args.github_pat is not None:
        synchronize_github(args.github_pat)

    if args.skip_updates is False:
        bingo_data = get_bingo_dataframe(BINGO_DATA_FILEPATH)

        recorded_duplicates = get_existing_states(DUPE_RECORD_FILEPATH)

        normalize_books(bingo_data, args.match_score, args.rescan_keys, recorded_duplicates)
    else:
        with OUTPUT_DF_FILEPATH.open("r") as bingo_data_file:
            bingo_data = pandas.read_csv(bingo_data_file)
            bingo_data = bingo_data.replace(numpy.nan, None)

    print("Collecting statistics.")
    collect_statistics(bingo_data)

    if args.github_pat is not None:
        print()
        print("Pushing changes and opening pull request.")
        commit_push_pr(args.github_pat)


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
        "--rescan-keys",
        action="store_true",
        help="""
        Pass this to check for duplicates on pairs that were previously not matched.
        Best paired with a lower `match-score` than the default.
        """,
    )

    parser.add_argument(
        "--skip-updates",
        action="store_true",
        help="""
        Use the most recent version of the updated Bingo data instead of 
        """,
    )

    parser.add_argument(
        "--github-pat",
        type=str,
        default=None,
        help="""
        Pass this to automatically commit and push changes to GitHub.
        """,
    )

    return parser.parse_args()


if __name__ == "__main__":
    main(cli())
