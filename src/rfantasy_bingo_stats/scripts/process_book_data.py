import argparse
from collections import defaultdict

from rfantasy_bingo_stats.constants import BOOK_INFO_FILEPATH
from rfantasy_bingo_stats.data_operations.get_data import get_existing_states
from rfantasy_bingo_stats.models.book_info import (
    BookInfo,
    BookInfoAdapter,
)
from rfantasy_bingo_stats.models.defined_types import Book

SHEETS = ()


def main(_: argparse.Namespace) -> None:
    """
    NOTE: This currently _overwrites_, does not _update_
    """

    recorded_dupes, __ = get_existing_states()

    final_book_data: defaultdict[Book, BookInfo] = defaultdict(BookInfo)
    for book in recorded_dupes.book_dupes.keys():
        final_book_data[  # pylint: disable=pointless-statement  # The point of this statement is to init empty book data
            book
        ]

    with BOOK_INFO_FILEPATH.open("w", encoding="utf8") as book_info_file:
        book_info_file.write(BookInfoAdapter.dump_json(final_book_data, indent=2).decode("utf8"))


def cli() -> None:
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    cli()
