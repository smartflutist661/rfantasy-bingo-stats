import argparse
from collections import defaultdict
from io import StringIO
from typing import Optional

import pandas
import requests

from rfantasy_bingo_stats.constants import AUTHOR_INFO_FILEPATH
from rfantasy_bingo_stats.data_operations.get_data import get_existing_states
from rfantasy_bingo_stats.models.author_info import (
    AuthorInfo,
    AuthorInfoAdapter,
)
from rfantasy_bingo_stats.models.defined_types import Author
from rfantasy_bingo_stats.normalization import normalize_authors

SHEETS = (1677825029, 216198433, 2062669059, 860591288)


def main(_: argparse.Namespace) -> None:
    """
    NOTE: This currently _overwrites_, does not _update_
    """

    dfs = []
    for sheet in SHEETS:
        response = requests.get(
            f"https://docs.google.com/spreadsheets/d/1_NmXe0lUB8cSdpHYutUU9wH4vK1abufYXbEUoTWzhRY/export?format=csv&gid={sheet}",
            timeout=5,
        )
        df = pandas.read_csv(StringIO(response.content.decode("utf8")))
        dfs.append(df)

    raw_author_data = pandas.concat(dfs).set_index("Author")
    raw_author_data["queer"] = (
        raw_author_data["queer"]
        .replace("TRUE", True)
        .replace("FALSE", False)
        .replace("Unknown", None)
    )
    author_data = AuthorInfoAdapter.validate_python(raw_author_data.to_dict(orient="index"))

    authors_with_info = set(author_data.keys())

    recorded_dupes, recorded_ignores = get_existing_states()

    unique_authors = frozenset(authors_with_info)

    normalize_authors(
        unique_authors,
        match_score=90,
        rescan_non_dupes=False,
        recorded_dupes=recorded_dupes,
        recorded_ignores=recorded_ignores,
        skip_authors=False,
    )
    author_dedupe_map = recorded_dupes.get_author_dedupe_map()

    final_book_data = defaultdict(AuthorInfo)
    for author, author_info in author_data.items():
        if author in recorded_dupes.author_dupes.keys():
            deduped_author: Optional[Author] = author
        else:
            deduped_author = author_dedupe_map.get(author)

        if deduped_author is None:
            raise KeyError(f"Failed to find {author}, this should not be possible.")

        if len(deduped_author.split(", ")) > 1:
            # Skip multi-author groups
            continue

        final_book_data[deduped_author] = author_info

    for author in recorded_dupes.author_dupes.keys():
        # Single authors only
        if len(author.split(", ")) == 1:
            final_book_data[  # pylint: disable=pointless-statement  # The point of this statement is to init empty author data
                author
            ]

    with AUTHOR_INFO_FILEPATH.open("w", encoding="utf8") as author_info_file:
        author_info_file.write(
            AuthorInfoAdapter.dump_json(final_book_data, indent=2).decode("utf8")
        )

    pandas.DataFrame.from_dict(
        dict(
            sorted(
                AuthorInfoAdapter.dump_python(final_book_data).items(),
                key=lambda item: item[0].split()[-1],
            )
        ),
        orient="index",
        columns=["gender", "ethnicity", "queer", "nationality"],
    ).to_csv("author_data_final.csv")


def cli() -> None:
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    cli()
