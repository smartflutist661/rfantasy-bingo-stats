"""
Created on Apr 7, 2023

@author: fred
"""

import argparse
import json
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType as MAP

import pandas

from rfantasy_bingo_stats.calculate_statistics.get_bingo_cards import (
    get_bingo_cards,
    get_bingo_stats,
)
from rfantasy_bingo_stats.calculate_statistics.get_stats import create_markdown
from rfantasy_bingo_stats.calculate_statistics.plot_distributions import (
    create_yearly_plots,
    create_yoy_plots,
)
from rfantasy_bingo_stats.constants import (
    AUTHOR_INFO_FILEPATH,
    CURRENT_YEAR,
    DUPE_RECORD_FILEPATH,
    IGNORED_RECORD_FILEPATH,
    YearlyDataPaths,
)
from rfantasy_bingo_stats.data_operations.author_title_book_operations import (
    get_all_authors,
    get_all_title_author_combos,
    get_unique_authors,
    get_unique_books,
)
from rfantasy_bingo_stats.data_operations.get_data import (
    get_bingo_dataframe,
    get_existing_states,
)
from rfantasy_bingo_stats.data_operations.update_data import (
    comma_separate_authors,
    update_bingo_authors,
    update_bingo_books,
)
from rfantasy_bingo_stats.git_operations import (
    commit_push_pr,
    synchronize_github,
)
from rfantasy_bingo_stats.logger import LOGGER
from rfantasy_bingo_stats.match_books.get_matches import (
    get_possible_matches,
    update_dedupes_from_authors,
)
from rfantasy_bingo_stats.models.author_info import AuthorInfo
from rfantasy_bingo_stats.models.bingo_card import BingoCard
from rfantasy_bingo_stats.models.card_data import CardData
from rfantasy_bingo_stats.models.defined_types import (
    Author,
    CardID,
)
from rfantasy_bingo_stats.models.recorded_ignores import RecordedIgnores
from rfantasy_bingo_stats.models.recorded_states import RecordedDupes
from rfantasy_bingo_stats.models.utils import to_data

pandas.options.mode.copy_on_write = True


def normalize_books(
    bingo_data: pandas.DataFrame,
    card_data: CardData,
    match_score: int,
    rescan_non_dupes: bool,
    recorded_dupes: RecordedDupes,
    recorded_ignores: RecordedIgnores,
    skip_authors: bool,
    cleaned_data_output_path: Path,
) -> None:
    """Normalize book titles and authors"""

    all_authors = get_all_authors(bingo_data, card_data.all_title_author_hm_columns)

    unique_authors = get_unique_authors(all_authors)

    LOGGER.info(
        f"Starting with {len(unique_authors)} unique authors.\n\n"
        + "Processing possible misspellings."
        + " You may hit ctrl+C at any point to exit, or enter `e` at the prompt."
        + " Progress will be saved.\n"
    )

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

    # Correct multi-author groups
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

    LOGGER.info("Updating Bingo authors.")
    updated_data, author_dedupes = update_bingo_authors(
        bingo_data,
        recorded_dupes.author_dupes,
        card_data.all_title_author_hm_columns,
        cleaned_data_output_path,
    )
    LOGGER.info("Bingo authors updated.")

    LOGGER.info("Collecting all misspellings.")
    update_dedupes_from_authors(recorded_dupes, author_dedupes)

    all_title_author_combos = get_all_title_author_combos(
        updated_data, card_data.all_title_author_hm_columns
    )

    unique_books = get_unique_books(all_title_author_combos)

    LOGGER.info(
        f"Starting with {len(unique_books)} unique books.\n\n"
        + "Processing possible misspellings."
        + " You may hit ctrl+C at any point to exit, or enter `e` at the prompt."
        + " Progress will be saved.\n"
    )

    get_possible_matches(
        unique_books, match_score, rescan_non_dupes, recorded_dupes, recorded_ignores, "Book"
    )

    LOGGER.info("Updating Bingo books.")
    update_bingo_books(
        updated_data,
        recorded_dupes.book_dupes,
        card_data.all_title_author_hm_columns,
        cleaned_data_output_path,
    )
    LOGGER.info("Bingo books updated.")


def collect_statistics(
    cards: Mapping[CardID, BingoCard],
    recorded_states: RecordedDupes,
    yearly_paths: YearlyDataPaths,
    card_data: CardData,
    author_data: Mapping[Author, AuthorInfo],
    show_plots: bool,
) -> None:
    """Collect statistics on normalized books and create a rough draft post"""

    bingo_stats = get_bingo_stats(cards, recorded_states, card_data, author_data)

    with yearly_paths.output_stats.open("w", encoding="utf8") as stats_file:
        json.dump(bingo_stats.to_data(), stats_file, indent=2)

    create_markdown(bingo_stats, card_data, yearly_paths.output_md)

    create_yearly_plots(bingo_stats, yearly_paths.output_image_root, show_plots)

    create_yoy_plots(yearly_paths.output_image_root, show_plots)


def main(args: argparse.Namespace) -> None:
    """Process bingo data"""
    if args.github_pat is not None:
        synchronize_github(args.github_pat)

    if args.year is not None:
        data_paths = YearlyDataPaths(args.year)
    else:
        data_paths = YearlyDataPaths(CURRENT_YEAR)

    with data_paths.card_info.open("r", encoding="utf8") as card_data_file:
        card_data = CardData.from_data(json.load(card_data_file))

    bingo_data = get_bingo_dataframe(data_paths.raw_data_path)

    LOGGER.info("Loading data.")
    recorded_duplicates, recorded_ignores = get_existing_states(
        DUPE_RECORD_FILEPATH, IGNORED_RECORD_FILEPATH, args.skip_updates
    )

    if args.skip_updates is False:
        normalize_books(
            bingo_data.copy(deep=True),
            card_data,
            args.match_score,
            args.rescan_keys,
            recorded_duplicates,
            recorded_ignores,
            args.skip_authors,
            data_paths.output_df,
        )

    with AUTHOR_INFO_FILEPATH.open("r", encoding="utf8") as author_info_file:
        author_dedupe_map = recorded_duplicates.get_author_dedupe_map()
        author_data: Mapping[Author, AuthorInfo] = MAP(
            {
                author_dedupe_map.get(Author(key), Author(key)): AuthorInfo.from_data(val)
                for key, val in json.load(author_info_file).items()
            }
        )

    with AUTHOR_INFO_FILEPATH.open("w", encoding="utf8") as author_info_file:
        json.dump(to_data(author_data), author_info_file)
        LOGGER.info("Wrote corrected author info.")

    LOGGER.info("Collecting corrected bingo cards.")
    cards = get_bingo_cards(bingo_data, card_data)
    LOGGER.info("Collecting statistics.")
    collect_statistics(
        cards, recorded_duplicates, data_paths, card_data, author_data, args.show_plots
    )

    if args.github_pat is not None:
        LOGGER.info("Pushing changes and opening pull request.")
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

    parser.add_argument(
        "--year",
        type=int,
        help="Pass to process a year other than the current.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    main(cli())
