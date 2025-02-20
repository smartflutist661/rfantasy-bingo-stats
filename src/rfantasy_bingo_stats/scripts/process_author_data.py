import argparse
from collections import defaultdict
from io import StringIO
from typing import Optional

import pandas
import requests

from rfantasy_bingo_stats.constants import (
    AUTHOR_INFO_FILEPATH,
    DUPE_RECORD_FILEPATH,
    IGNORED_RECORD_FILEPATH,
)
from rfantasy_bingo_stats.data_operations.update_data import comma_separate_authors
from rfantasy_bingo_stats.logger import LOGGER
from rfantasy_bingo_stats.match_books.get_matches import get_possible_matches
from rfantasy_bingo_stats.models.author_info import (
    AuthorInfo,
    AuthorInfoAdapter,
)
from rfantasy_bingo_stats.models.defined_types import Author
from rfantasy_bingo_stats.models.recorded_ignores import RecordedIgnores
from rfantasy_bingo_stats.models.recorded_states import RecordedDupes

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

    with DUPE_RECORD_FILEPATH.open("r", encoding="utf8") as dupe_file:
        recorded_dupes = RecordedDupes.model_validate_json(dupe_file.read())
    with IGNORED_RECORD_FILEPATH.open("r", encoding="utf8") as ignore_file:
        recorded_ignores = RecordedIgnores.model_validate_json(ignore_file.read())

    unique_authors = frozenset(
        set(recorded_dupes.author_dupes.keys())
        | set().union(*(recorded_dupes.author_dupes.values()))
        | authors_with_info
    )

    LOGGER.info(
        f"Starting with {len(unique_authors)} unique authors.\n\n"
        + "Processing possible misspellings."
        + " You may hit ctrl+C at any point to exit, or enter `e` at the prompt."
        + " Progress will be saved.\n"
    )

    get_possible_matches(
        unique_authors,
        match_score=90,
        rescan_keys=False,
        known_states=recorded_dupes,
        known_ignores=recorded_ignores,
        ret_type="Author",
    )

    comma_separate_authors(recorded_dupes)

    unique_single_authors = frozenset(
        {
            Author(single_author)
            for author in recorded_dupes.author_dupes.keys()
            for single_author in author.split(", ")
        }
    )

    get_possible_matches(
        unique_single_authors | unique_authors,
        match_score=90,
        rescan_keys=False,
        known_states=recorded_dupes,
        known_ignores=recorded_ignores,
        ret_type="Author",
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
        dupe_file.write(recorded_dupes.model_dump_json(indent=2))
    with IGNORED_RECORD_FILEPATH.open("w", encoding="utf8") as ignore_file:
        ignore_file.write(recorded_ignores.model_dump_json(indent=2))

    author_dedupe_map = recorded_dupes.get_author_dedupe_map()

    final_author_data = defaultdict(AuthorInfo)
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

        final_author_data[deduped_author] = author_info

    for author in recorded_dupes.author_dupes.keys():
        # Single authors only
        if len(author.split(", ")) == 1:
            final_author_data[  # pylint: disable=pointless-statement  # The point of this statement is to init empty author data
                author
            ]

    with AUTHOR_INFO_FILEPATH.open("w", encoding="utf8") as author_info_file:
        author_info_file.write(
            AuthorInfoAdapter.dump_json(final_author_data, indent=2).decode("utf8")
        )

    pandas.DataFrame.from_dict(
        dict(
            sorted(
                AuthorInfoAdapter.dump_python(final_author_data).items(),
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
