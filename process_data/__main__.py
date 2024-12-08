"""
Created on Apr 7, 2023

@author: fred
"""
import argparse
from collections import Counter

import pandas

from .calculate_statistics.get_bingo_cards import get_bingo_cards
from .data.current import (
    BINGO_DATA_FILEPATH,
    OUTPUT_MD_FILEPATH,
    SQUARE_NAMES,
)
from .data.filepaths import DUPE_RECORD_FILEPATH
from .data_operations.author_title_book_operations import (
    books_to_title_authors,
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
    add_to_markdown,
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


def collect_statistics(bingo_data: pandas.DataFrame, separator: str) -> None:
    """Collect statistics on normalized books"""
    all_title_authors = get_all_title_author_combos(bingo_data)
    unique_books = get_unique_books(all_title_authors, separator)

    unique_authors = set()
    for _, author in books_to_title_authors(unique_books, separator):
        unique_authors.add(author)

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


def main(args: argparse.Namespace) -> None:
    """Process bingo data"""
    if args.github_pat is not None:
        synchronize_github(args.github_pat)

    bingo_data = get_bingo_dataframe(BINGO_DATA_FILEPATH)

    recorded_duplicates = get_existing_states(DUPE_RECORD_FILEPATH)

    normalize_books(bingo_data, args.match_score, args.rescan_non_dupes, recorded_duplicates)

    print("Collecting statistics.")
    print()
    collect_statistics(bingo_data, recorded_duplicates.book_separator)

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
        "--rescan-non-dupes",
        action="store_true",
        help="""
        Pass this to check for duplicates on pairs that were previously not matched.
        Best paired with a lower `match-score` than the default.
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
