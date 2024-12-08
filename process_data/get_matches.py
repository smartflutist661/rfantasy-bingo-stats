"""
Created on Apr 7, 2023

@author: fred
"""
import json
from types import MappingProxyType as MAP
from typing import Mapping

from .constants import DUPE_RECORD_FILEPATH
from .get_data import get_existing_states
from .process_match import process_new_pair


def get_possible_matches(
    title_author_pairs: frozenset[str],
    match_score: int,
) -> Mapping[str, frozenset[str]]:
    """Determine all possible misspellings for each title/author pair"""
    known_states = get_existing_states(DUPE_RECORD_FILEPATH)
    try:
        unscanned_pairs = set(
            title_author_pairs
            - (
                set(known_states.dupes.keys())
                | set().union(*(known_states.dupes.values()))
                | known_states.non_dupes
            )
        )

        while len(unscanned_pairs) > 0:
            title_author_pair = unscanned_pairs.pop()
            process_new_pair(
                known_states.dupes,
                known_states.non_dupes,
                unscanned_pairs,
                title_author_pair,
                match_score,
            )

    except Exception:  # pylint: disable=broad-exception-caught
        print("Saving progress and exiting")

    finally:
        with DUPE_RECORD_FILEPATH.open("w", encoding="utf8") as dupe_file:
            json.dump(known_states.to_data(), dupe_file)

    return MAP({k: frozenset(v) for k, v in known_states.dupes.items()})
