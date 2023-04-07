"""
Created on Apr 7, 2023

@author: fred
"""
from __future__ import annotations

from collections import defaultdict
from enum import Enum
import json
from pathlib import Path
from types import MappingProxyType as MAP
from typing import Mapping, Optional, Any

import pandas
from pyexcel_ods3 import get_data  # type: ignore
from thefuzz import process  # type: ignore
from dataclasses import dataclass, fields
import argparse


@dataclass
class KnownDupes:
    dupes: defaultdict[str, set[str]]

    @classmethod
    def from_data(cls, data: Any) -> KnownDupes:
        return cls(
            dupes=defaultdict(
                set,
                {str(key): {str(v) for v in val} for key, val in data["dupes"].items()},
            )
        )

    def to_data(self) -> dict[str, Any]:
        out = {}

        for k, v in {
            field.name: getattr(self, field.name) for field in fields(self)
        }.items():
            out[k] = to_data(v)

        return out

    @classmethod
    def empty(cls) -> KnownDupes:
        return cls(dupes=defaultdict(set))


DUPE_RECORD_FILEPATH = Path(__file__).parent / "resolved_duplicates.json"


def to_data(data: Any) -> Any:
    if isinstance(data, dict):
        for k, v in data.items():
            return {k: to_data(v) for k, v in data.items()}
    elif isinstance(data, (list, set)):
        return [to_data(v) for v in data]

    return data


def get_existing_dupes(
    dupe_path: Path,
) -> KnownDupes:
    try:
        with dupe_path.open("r", encoding="utf8") as dupe_file:
            return KnownDupes.from_data(json.load(dupe_file))
    except IOError:
        return KnownDupes.empty()


class MatchChoice(Enum):
    save = 1
    swap = 2
    skip = 3


def process_existing_match(
    dupes: dict[str, set[str]],
    existing_match: str,
    new_match: str,
    score: int,
    existing_match_key: Optional[str] = None,
) -> None:
    print(f"Tentative match: {new_match} -> {existing_match}, score {score}")
    if existing_match_key is not None:
        in_val_str = f" to {existing_match_key}"
    else:
        in_val_str = ""
    print(f"{existing_match} already deduplicated{in_val_str}.")
    if existing_match_key is not None:
        existing_match = existing_match_key

    print("Choose the best version:")
    print(f"[{MatchChoice.save.value}] {new_match}")
    print(f"[{MatchChoice.swap.value}] {existing_match}")
    print(f"[{MatchChoice.skip.value}] Not a match")
    print(f"[e] Save and exit")
    choice = MatchChoice(int(input("Selection: ")))

    if choice == MatchChoice.save:
        dupes[existing_match].add(new_match)
        print(f"{new_match} recorded as duplicate of {existing_match}")
    elif choice == MatchChoice.swap:
        dupes[new_match] |= dupes[existing_match]
        print(f"Duplicates of {existing_match} swapped to duplicates of {new_match}")
        dupes[new_match].add(existing_match)
        print(f"{existing_match} recorded as duplicate of {new_match}")
        del dupes[existing_match]
    print()


def process_new_match(
    dupes: dict[str, set[str]],
    title_author_pair: str,
    title_author_match: Optional[str],
    score: int,
) -> None:
    if title_author_match is not None:
        print(
            f"Tentative match found: {title_author_pair} -> {title_author_match}, score {score}"
        )
        print("Choose the best version:")
        print(f"[{MatchChoice.save.value}] {title_author_pair}")
        print(f"[{MatchChoice.swap.value}] {title_author_match}")
        print(f"[{MatchChoice.skip.value}] Not a match")
        print(f"[e] Save and exit")
        choice = MatchChoice(int(input("Selection: ")))

        if choice == MatchChoice.save:
            dupes[title_author_pair].add(title_author_match)
            print(f"{title_author_match} recorded as duplicate of {title_author_pair}")
        elif choice == MatchChoice.swap:
            dupes[title_author_match].add(title_author_pair)
            print(f"{title_author_pair} recorded as duplicate of {title_author_match}")
    else:
        print(f"No duplicates found for {title_author_pair}")
        dupes[title_author_pair]
    print()


def get_possible_matches(
    title_author_pairs: frozenset[str],
    match_score: int,
) -> Mapping[str, frozenset[str]]:
    try:
        known_dupes = get_existing_dupes(DUPE_RECORD_FILEPATH)
        dupes = known_dupes.dupes
        unmatched_pairs = set(
            title_author_pairs - (set(dupes.keys()) | set().union(*(dupes.values())))
        )

        while len(unmatched_pairs) > 0:
            title_author_pair = unmatched_pairs.pop()
            res = process.extractOne(
                title_author_pair,
                set(dupes.keys()) | set().union(*(dupes.values())),
                score_cutoff=match_score,
            )
            if res is not None:
                title_author_match, score = res
                print(title_author_match)
                if title_author_match in dupes.keys():
                    process_existing_match(
                        dupes, title_author_match, title_author_pair, score
                    )
                else:
                    for existing_match_key, dupe_tuples in dupes.items():
                        if title_author_match in dupe_tuples:
                            process_existing_match(
                                dupes,
                                title_author_match,
                                title_author_pair,
                                score,
                                existing_match_key,
                            )
                            break
            else:
                res = process.extractOne(
                    title_author_pair,
                    unmatched_pairs,
                    score_cutoff=match_score,
                )

                title_author_match, score = res if res is not None else (None, None)
                process_new_match(dupes, title_author_pair, title_author_match, score)
                if title_author_match is not None:
                    unmatched_pairs.remove(title_author_match)
    except:
        print("Saving progress and exiting")

    finally:
        with DUPE_RECORD_FILEPATH.open("w", encoding="utf8") as dupe_file:
            json.dump(KnownDupes(dupes).to_data(), dupe_file)

    return MAP({k: frozenset(v) for k, v in dupes.items()})


def main(args: argparse.Namespace) -> None:
    raw_bingo_data = dict(get_data(str(args.data_path)))

    column_names = raw_bingo_data["Uncorrectd 2022 Data"][0]

    title_author_colnames = tuple(
        (col_name_1, col_name_2)
        for col_name_1 in column_names
        for col_name_2 in column_names
        if "TITLE" in col_name_1
        and "AUTHOR" in col_name_2
        and col_name_1.split(":")[0] == col_name_2.split(":")[0]
    )

    bingo_data = pandas.DataFrame(
        raw_bingo_data["Uncorrectd 2022 Data"][1:],
        columns=column_names,
    ).set_index("CARD")
    pandas.set_option("display.max_columns", None)
    pandas.set_option("display.width", None)

    title_author_pairs: list[tuple[str, str]] = []
    for title_col, author_col in title_author_colnames:
        title_author_pairs.extend(zip(bingo_data[title_col], bingo_data[author_col]))

    print(
        "Processing possible misspellings."
        + " You may hit ctrl+C at any point to exit, or enter `e` at the prompt."
        + " Progress will be saved."
    )
    unique_pairs = frozenset(
        {" by ".join(str(elem) for elem in pair) for pair in title_author_pairs}
    )
    get_possible_matches(unique_pairs, args.match_score)


def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--data_path",
        type=Path,
        default=Path(__file__).parent.parent / "bingo_data.ods",
        help="Path to ODS file with raw Bingo data.",
    )

    parser.add_argument(
        "--match-score",
        type=int,
        default=90,
        help="""
        The minimum score to allow for a match. Fairly sensitive.
        Default = 90
        """,
    )

    return parser.parse_args()


if __name__ == "__main__":
    # print(MatchChoice(2))
    main(cli())
