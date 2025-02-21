import argparse
from argparse import ArgumentParser

import pandas
from pydantic import ValidationError
from pydantic.main import BaseModel

from rfantasy_bingo_stats.bingo_operations import bingo_main
from rfantasy_bingo_stats.cli import (
    Args,
    BingoArgs,
    PollArgs,
)
from rfantasy_bingo_stats.git_operations import (
    commit_push_pr,
    synchronize_github,
)
from rfantasy_bingo_stats.logger import LOGGER
from rfantasy_bingo_stats.poll_operations import poll_main

pandas.options.mode.copy_on_write = True


def model_to_args(parser: ArgumentParser, model: type[BaseModel]) -> None:
    """Add Pydantic model to an ArgumentParser"""
    for name, field in model.model_fields.items():
        assert field.annotation is not None
        if field.annotation is bool:
            parser.add_argument(
                f"--{name.replace('_', '-')}",
                action="store_false" if field.default is True else "store_true",
                help=field.description,
            )
        else:
            parser.add_argument(
                f"--{name.replace('_', '-')}",
                type=field.annotation,
                default=field.default,
                help=field.description,
            )


def cli() -> None:
    """Define command-line interface for this program"""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    bingo_parser = subparsers.add_parser("bingo")
    poll_parser = subparsers.add_parser("poll")

    model_to_args(parser, Args)
    model_to_args(bingo_parser, BingoArgs)
    model_to_args(poll_parser, PollArgs)

    all_args = vars(parser.parse_args())

    args = Args.model_validate(all_args)
    try:
        poll_args = PollArgs.model_validate(all_args)
    except ValidationError:
        poll_args = None

    try:
        bingo_args = BingoArgs.model_validate(all_args)
    except ValidationError:
        bingo_args = None

    if args.github_pat is not None:
        synchronize_github(args.github_pat)

    # There are no required args for bingo, but one arg is required for polls
    # Abuse this fact to determine which path to execute
    if poll_args is None:
        assert bingo_args is not None
        bingo_main(args, bingo_args)
    else:
        poll_main(args, poll_args)

    if args.github_pat is not None:
        LOGGER.info("Pushing changes and opening pull request.")
        commit_push_pr(args.github_pat)


if __name__ == "__main__":
    cli()
