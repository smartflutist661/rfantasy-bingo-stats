"""
Created on Apr 7, 2023

@author: fred
"""
import argparse
import json

import pandas

from .calculate_statistics.get_bingo_cards import get_bingo_stats
from .calculate_statistics.get_stats import create_markdown
from .calculate_statistics.plot_distributions import create_all_plots
from .data.current import (
    BINGO_DATA_FILEPATH,
    OUTPUT_STATS_FILEPATH,
)
from .data.filepaths import (
    DUPE_RECORD_FILEPATH,
    IGNORED_RECORD_FILEPATH,
)
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
from .types.defined_types import Author
from .types.recorded_ignores import RecordedIgnores
from .types.recorded_states import RecordedDupes


def normalize_books(
    bingo_data: pandas.DataFrame,
    match_score: int,
    rescan_non_dupes: bool,
    recorded_dupes: RecordedDupes,
    recorded_ignores: RecordedIgnores,
    skip_authors: bool,
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

    if not skip_authors:
        get_possible_matches(
            unique_authors,
            match_score,
            rescan_non_dupes,
            recorded_dupes,
            recorded_ignores,
            "Author",
        )

    comma_separate_authors(recorded_dupes)

    if not skip_authors:
        unique_single_authors = frozenset(
            {
                Author(single_author)
                for author in recorded_dupes.author_dupes.keys()
                for single_author in author.split(", ")
            }
        )

        get_possible_matches(
            unique_single_authors | unique_authors,
            match_score,
            rescan_non_dupes,
            recorded_dupes,
            recorded_ignores,
            "Author",
        )

    author_dedupe_map = recorded_dupes.get_author_dedupe_map()

    for author in tuple(recorded_dupes.author_dupes.keys()):
        final_author = author
        for single_author in author.split(", "):
            single_author = Author(single_author)
            updated_single_author = author_dedupe_map.get(single_author, single_author)
            final_author = Author(final_author.replace(single_author, updated_single_author))
        if final_author != author:
            recorded_dupes.author_dupes[final_author] |= recorded_dupes.author_dupes[author]
            recorded_dupes.author_dupes[final_author].add(author)
            del recorded_dupes.author_dupes[author]

    with DUPE_RECORD_FILEPATH.open("w", encoding="utf8") as dupe_file:
        json.dump(recorded_dupes.to_data(), dupe_file, indent=2)

    print("Updating Bingo authors.")
    updated_data, author_dedupes = update_bingo_authors(
        bingo_data, recorded_dupes.author_dupes, recorded_dupes.book_separator
    )
    print("Bingo authors updated.")

    print("Collecting all misspellings.")
    update_dedupes_from_authors(recorded_dupes, author_dedupes)

    all_title_author_combos = get_all_title_author_combos(updated_data)

    unique_books = get_unique_books(all_title_author_combos, recorded_dupes.book_separator)

    print(f"Starting with {len(unique_books)} unique books.")

    print(
        "Processing possible misspellings."
        + " You may hit ctrl+C at any point to exit, or enter `e` at the prompt."
        + " Progress will be saved."
    )
    print()

    get_possible_matches(
        unique_books, match_score, rescan_non_dupes, recorded_dupes, recorded_ignores, "Book"
    )

    print("Updating Bingo books.")
    update_bingo_books(updated_data, recorded_dupes.book_dupes)
    print("Bingo books updated.")


def collect_statistics(
    bingo_data: pandas.DataFrame, recorded_states: RecordedDupes, show_plots: bool
) -> None:
    """Collect statistics on normalized books and create a rough draft post"""

    bingo_stats = get_bingo_stats(bingo_data, recorded_states)

    with OUTPUT_STATS_FILEPATH.open("w", encoding="utf8") as stats_file:
        json.dump(bingo_stats.to_data(), stats_file, indent=2)

    create_markdown(bingo_stats)

    create_all_plots(bingo_stats, show_plots)


def main(args: argparse.Namespace) -> None:
    """Process bingo data"""
    if args.github_pat is not None:
        synchronize_github(args.github_pat)

    bingo_data = get_bingo_dataframe(BINGO_DATA_FILEPATH)

    print("Loading data.")
    recorded_duplicates, recorded_ignores = get_existing_states(
        DUPE_RECORD_FILEPATH, IGNORED_RECORD_FILEPATH, args.skip_updates
    )

    if args.skip_updates is False:
        normalize_books(
            bingo_data,
            args.match_score,
            args.rescan_keys,
            recorded_duplicates,
            recorded_ignores,
            args.skip_authors,
        )

    print("Collecting statistics.")
    collect_statistics(bingo_data, recorded_duplicates, args.show_plots)

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
        Use the existing resolved duplicates, don't attempt to find new duplicates 
        """,
    )

    parser.add_argument(
        "--skip-authors",
        action="store_true",
        help="""
        Skip deduplicating authors, go straight to books 
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

    parser.add_argument(
        "--show-plots",
        action="store_true",
        help="Pass to display plots as well as saving them.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    main(cli())
