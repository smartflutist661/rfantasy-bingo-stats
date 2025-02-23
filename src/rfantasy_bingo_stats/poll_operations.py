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
    POLL_SPLIT_OPTIONS,
    PollDataPaths,
)
from rfantasy_bingo_stats.data_operations.author_title_book_operations import title_author_to_book
from rfantasy_bingo_stats.data_operations.get_data import (
    get_existing_states,
)
from rfantasy_bingo_stats.data_operations.update_data import (
    update_poll_authors,
    update_poll_books,
)
from rfantasy_bingo_stats.logger import LOGGER
from rfantasy_bingo_stats.models.cleaned_poll_data import CleanedPollData
from rfantasy_bingo_stats.models.defined_types import TitleAuthor
from rfantasy_bingo_stats.models.processed_poll_data import ProcessedPollData
from rfantasy_bingo_stats.models.raw_poll_data import RawPollData
from rfantasy_bingo_stats.normalization import (
    normalize_authors,
    normalize_books,
    update_author_info_map,
    update_book_info_map,
)


def retrieve_poll_data(poll_args: PollArgs) -> RawPollData:
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

    return RawPollData(
        poll_post_id=poll_args.poll_post_id,
        poll_type=poll_args.poll_type,
        poll_year=poll_args.year,
        comments=tuple(comment_bodies),
    )


def validate_votes(raw_votes: RawPollData) -> ProcessedPollData:

    title_author_votes = []
    for comment in raw_votes.comments:
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
                title_authors.append(
                    cast(TitleAuthor, tuple(val.strip() for val in potential_title_author))
                )
            if len(title_authors) == 10:
                break
        title_author_votes.append(tuple(title_authors))

    return ProcessedPollData(
        poll_type=raw_votes.poll_type,
        poll_year=raw_votes.poll_year,
        votes=tuple(title_author_votes),
    )


def poll_main(args: Args, poll_args: PollArgs) -> None:
    data_paths = PollDataPaths(poll_args.poll_type, poll_args.year)

    # Retrieve raw data or pull from cache
    if poll_args.force_refresh or not data_paths.raw_data.exists():
        if poll_args.poll_post_id is None:
            err = ArgumentError(
                argument=None,
                message="You must supply the Reddit post ID in order to download new poll results",
            )
            err.argument_name = "poll-post-id"
            raise err
        raw_votes = retrieve_poll_data(poll_args)
        with data_paths.raw_data.open("w", encoding="utf8") as poll_data_file:
            poll_data_file.write(raw_votes.model_dump_json(indent=2))
    else:
        with data_paths.raw_data.open("r", encoding="utf8") as poll_data_file:
            raw_votes = RawPollData.model_validate_json(poll_data_file.read())

    # Basic validation (split into title/author, limit comments to 10 votes each)
    valid_votes = validate_votes(raw_votes)
    with data_paths.processed_votes.open("w", encoding="utf8") as poll_data_file:
        poll_data_file.write(valid_votes.model_dump_json(indent=2))

    LOGGER.info("Loading data.")
    recorded_duplicates, recorded_ignores = get_existing_states()

    if args.skip_updates is False:
        unique_authors = frozenset(author for votes in valid_votes.votes for _, author in votes)
        normalize_authors(
            unique_authors,
            args.match_score,
            args.rescan_keys,
            recorded_duplicates,
            recorded_ignores,
            args.skip_authors,
        )
        LOGGER.info("Updating vote authors.")
        updated_votes = update_poll_authors(
            valid_votes.votes,
            recorded_duplicates.get_author_dedupe_map(),
        )
        LOGGER.info("Vote authors updated.")

        unique_books = frozenset(
            title_author_to_book(title_author) for votes in updated_votes for title_author in votes
        )
        normalize_books(
            unique_books,
            args.match_score,
            args.rescan_keys,
            recorded_duplicates,
            recorded_ignores,
        )

        LOGGER.info("Updating vote books.")
        cleaned_poll_results = update_poll_books(
            updated_votes,
            recorded_duplicates.get_book_dedupe_map(),
        )
        with data_paths.cleaned_votes.open("w", encoding="utf8") as cleaned_data_file:
            cleaned_data_file.write(
                CleanedPollData(
                    poll_type=valid_votes.poll_type,
                    poll_year=valid_votes.poll_year,
                    votes=cleaned_poll_results,
                ).model_dump_json(indent=2)
            )
        LOGGER.info("Vote books updated.")

    update_author_info_map(recorded_duplicates)
    update_book_info_map(recorded_duplicates)
    LOGGER.info("Wrote corrected metadata.")
