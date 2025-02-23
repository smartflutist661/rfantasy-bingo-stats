import os
import re
from argparse import ArgumentError
from pathlib import Path
from typing import cast

import praw  # type: ignore[import-untyped]
from dotenv.main import load_dotenv

from rfantasy_bingo_stats.cli import (
    Args,
    PollArgs,
)
from rfantasy_bingo_stats.constants import (
    DUPE_RECORD_FILEPATH,
    IGNORED_RECORD_FILEPATH,
    POLL_SPLIT_OPTIONS,
    PollDataPaths,
)
from rfantasy_bingo_stats.data_operations.author_title_book_operations import title_author_to_book
from rfantasy_bingo_stats.data_operations.get_data import (
    get_existing_states,
)
from rfantasy_bingo_stats.data_operations.update_data import (
    update_bingo_authors,
    update_bingo_books,
)
from rfantasy_bingo_stats.logger import LOGGER
from rfantasy_bingo_stats.models.defined_types import TitleAuthor
from rfantasy_bingo_stats.models.processed_poll_data import ProcessedPollData
from rfantasy_bingo_stats.models.raw_poll_data import RawPollData
from rfantasy_bingo_stats.normalization import (
    normalize_authors,
    normalize_books,
    update_author_info_map,
)


def retrieve_poll_data(poll_args: PollArgs, raw_data_path: Path) -> None:
    # Currently checking right before call
    assert poll_args.poll_post_id is not None
    load_dotenv(Path(__file__).parents[2] / ".env")

    reddit_client = praw.Reddit(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        user_agent="Poll Data Collection (by u/smartflutist661)",
    )
    top_level_comments = reddit_client.submission(poll_args.poll_post_id).comments
    top_level_comments.replace_more(limit=None)

    comment_bodies = []
    for comment in top_level_comments[1:]:
        comment_bodies.append(comment.body)

    with raw_data_path.open("w", encoding="utf8") as poll_data_file:
        poll_data_file.write(
            RawPollData(
                poll_post_id=poll_args.poll_post_id,
                poll_type=poll_args.poll_type,
                poll_year=poll_args.year,
                comments=tuple(comment_bodies),
            ).model_dump_json(indent=2)
        )


def validate_votes(data_paths: PollDataPaths) -> None:
    with data_paths.raw_data.open("r", encoding="utf8") as poll_data_file:
        raw_poll_data = RawPollData.model_validate_json(poll_data_file.read())

    title_author_votes = []
    for comment in raw_poll_data.comments:
        title_authors = []
        for line in comment.split("\n"):
            if line.strip() in {"", "[deleted]", "[removed]"}:
                continue
            potential_vote = (
                re.sub("|".join([r"^\* *", "^- *", r"\**", r"^[0-9]0?\.?"]), "", line)
                .replace("\xa0", " ")
                .strip()
            )
            potential_title_author = None
            for split_option in POLL_SPLIT_OPTIONS:
                if split_option in potential_vote:
                    potential_title_author = potential_vote.split(split_option)
                    break
            if potential_title_author is not None and len(potential_title_author) == 2:
                title_authors.append(cast(TitleAuthor, tuple(potential_title_author)))
            if len(title_authors) == 10:
                break
        title_author_votes.append(title_authors)

    processed_poll_data = ProcessedPollData(
        poll_type=raw_poll_data.poll_type,
        poll_year=raw_poll_data.poll_year,
        votes=tuple(tuple(title_authors) for title_authors in title_author_votes),
    )
    with data_paths.processed_votes.open("w", encoding="utf8") as poll_data_file:
        poll_data_file.write(processed_poll_data.model_dump_json(indent=2))


def poll_main(args: Args, poll_args: PollArgs) -> None:
    data_paths = PollDataPaths(poll_args.poll_type, poll_args.year)

    if poll_args.force_refresh or not data_paths.raw_data.exists():
        if poll_args.poll_post_id is None:
            err = ArgumentError(
                argument=None,
                message="You must supply the Reddit post ID in order to download new poll results",
            )
            err.argument_name = "poll-post-id"
            raise err
        retrieve_poll_data(poll_args, data_paths.raw_data)

    validate_votes(data_paths)

    with data_paths.processed_votes.open("r", encoding="utf8") as poll_data_file:
        valid_votes = ProcessedPollData.model_validate_json(poll_data_file.read())

    return

    LOGGER.info("Loading data.")
    recorded_duplicates, recorded_ignores = get_existing_states(
        DUPE_RECORD_FILEPATH, IGNORED_RECORD_FILEPATH
    )

    if args.skip_updates is False:
        unique_authors = frozenset(author for _, author in valid_votes.votes)
        normalize_authors(
            unique_authors,
            args.match_score,
            args.rescan_keys,
            recorded_duplicates,
            recorded_ignores,
            args.skip_authors,
        )
        # TODO: Do validated votes need to be updated?
        LOGGER.info("Updating Bingo authors.")
        updated_data, author_dedupes = update_bingo_authors(
            bingo_data.copy(deep=True),
            recorded_duplicates.author_dupes,
            card_data.all_title_author_hm_columns,
            data_paths.output_df,
        )
        LOGGER.info("Bingo authors updated.")

        unique_books = frozenset(
            title_author_to_book(title_author) for title_author in valid_votes.votes
        )
        # TODO: These should probably be normalized as Series from the get-go instead
        normalize_books(
            unique_books,
            args.match_score,
            args.rescan_keys,
            recorded_duplicates,
            recorded_ignores,
        )

        LOGGER.info("Updating Bingo books.")
        update_bingo_books(
            updated_data,
            recorded_duplicates.book_dupes,
            card_data.all_title_author_hm_columns,
            data_paths.output_df,
        )
        LOGGER.info("Bingo books updated.")

    author_data = update_author_info_map(recorded_duplicates)
    LOGGER.info("Wrote corrected author info.")
    # TODO: Map books to series
    # TODO: Collect final poll data
    # TODO: Compare to most recent poll of same type
    LOGGER.info("Collecting statistics.")
    collect_statistics(
        cards, recorded_duplicates, data_paths, card_data, author_data, args.show_plots
    )
