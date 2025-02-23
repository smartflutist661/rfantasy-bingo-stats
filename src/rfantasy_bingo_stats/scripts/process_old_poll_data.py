import argparse
from collections import Counter
from pathlib import Path
from typing import cast

import pandas

from rfantasy_bingo_stats.constants import PollDataPaths
from rfantasy_bingo_stats.data_operations.author_title_book_operations import title_author_to_book
from rfantasy_bingo_stats.data_operations.get_data import get_existing_states
from rfantasy_bingo_stats.data_operations.update_data import (
    update_poll_authors,
    update_poll_books,
)
from rfantasy_bingo_stats.models.defined_types import (
    Author,
    Title,
    TitleAuthor,
)
from rfantasy_bingo_stats.models.unagg_poll_results import UnaggregatedPollResults
from rfantasy_bingo_stats.normalization import (
    normalize_authors,
    normalize_books,
    update_author_info_map,
    update_book_info_map,
)


def main(_: argparse.Namespace) -> None:
    poll_data_dir = Path(__file__) / "old_poll_data_raw"
    all_poll_votes = {}
    for poll_data_filepath in poll_data_dir.iterdir():
        poll_name = poll_data_filepath.stem
        df = pandas.read_csv(poll_data_filepath)
        all_poll_votes[poll_name] = [
            cast(TitleAuthor, (Title(row["Name"]), Author(row["Author"])))
            for _, row in df.iterrows()
        ]

    unique_authors = frozenset(
        author for poll_votes in all_poll_votes.values() for _, author in poll_votes
    )

    recorded_dupes, recorded_ignores = get_existing_states()

    normalize_authors(
        unique_authors,
        match_score=90,
        rescan_non_dupes=False,
        recorded_dupes=recorded_dupes,
        recorded_ignores=recorded_ignores,
        skip_authors=False,
    )

    update_author_info_map(recorded_dupes)

    author_dedupe_map = recorded_dupes.get_author_dedupe_map()
    all_updated_votes = {}
    for poll_name, poll_votes in all_poll_votes.items():
        all_updated_votes[poll_name] = update_poll_authors(
            [poll_votes],
            author_dedupe_map,
        )[0]

    unique_books = frozenset(
        title_author_to_book(title_author)
        for updated_votes in all_updated_votes.values()
        for title_author in updated_votes
    )
    normalize_books(
        unique_books,
        match_score=90,
        rescan_non_dupes=False,
        recorded_dupes=recorded_dupes,
        recorded_ignores=recorded_ignores,
    )

    book_dedupe_map = recorded_dupes.get_book_dedupe_map()
    all_cleaned_votes = {}
    for poll_name, updated_votes in all_updated_votes.items():
        all_cleaned_votes[poll_name] = update_poll_books(
            [updated_votes],
            book_dedupe_map,
        )[0]

    update_book_info_map(recorded_dupes)

    for poll_name, cleaned_votes in all_cleaned_votes.items():
        poll_type, year = poll_name.rsplit("_", maxsplit=1)
        poll_year = int(year)
        unagg_res = UnaggregatedPollResults(
            poll_type=poll_type,
            year=poll_year,
            results=Counter(cleaned_votes),
        )
        with PollDataPaths(poll_type, poll_year).unagg_results.open("w") as unagg_res_file:
            unagg_res_file.write(unagg_res.model_dump_json(indent=2))


def cli() -> None:
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    cli()
