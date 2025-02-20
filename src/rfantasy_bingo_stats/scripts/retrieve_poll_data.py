import argparse
import os
from pathlib import Path

import praw  # type: ignore[import-untyped]
from dotenv import load_dotenv

from rfantasy_bingo_stats.constants import POLL_DATA_PATH
from rfantasy_bingo_stats.models.raw_poll_data import RawPollData


def main(args: argparse.Namespace) -> None:
    load_dotenv(Path(__file__).parents[3] / ".env")

    reddit_client = praw.Reddit(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        user_agent="Poll Data Collection (by u/smartflutist661)",
    )
    top_level_comments = reddit_client.submission(args.post_id).comments
    top_level_comments.replace_more(limit=None)

    comment_bodies = []
    for comment in top_level_comments[1:]:
        comment_bodies.append(comment.body)

    with (POLL_DATA_PATH / f"raw_{args.poll_name.replace(' ', '_').lower()}.json").open(
        "w", encoding="utf8"
    ) as poll_data_file:
        poll_data_file.write(
            RawPollData(
                poll_post_id=args.post_id,
                poll_name=args.poll_name,
                comments=comment_bodies,
            ).model_dump_json(indent=2)
        )


def cli() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--post-id", type=str, default="1inoxxy")
    parser.add_argument("--poll-name", type=str, default="Top Novels 2025")

    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    cli()
