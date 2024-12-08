"""
Created on Apr 7, 2023

@author: fred
"""
import json
import traceback
from types import MappingProxyType as MAP
from typing import Mapping

from ..data.filepaths import DUPE_RECORD_FILEPATH
from ..types.defined_types import Book
from ..types.recorded_states import RecordedStates
from .process_match import process_new_pair


def get_possible_matches(
    books: frozenset[Book],
    match_score: int,
    rescan_non_dupes: bool,
    known_states: RecordedStates,
) -> Mapping[Book, frozenset[Book]]:
    """Determine all possible misspellings for each title/author pair"""
    try:
        unscanned_pairs = set(
            books - (set(known_states.dupes.keys()) | set().union(*(known_states.dupes.values())))
        )
        if rescan_non_dupes is False:
            unscanned_pairs -= known_states.non_dupes
            non_dupe_str = ""
        else:
            non_dupe_str = f", of which {len(known_states.non_dupes)} are being rescanned"

        print(f"Scanning {len(unscanned_pairs)} unscanned books{non_dupe_str}.")
        while len(unscanned_pairs) > 0:
            title_author_pair = unscanned_pairs.pop()
            if rescan_non_dupes is True:
                # This may be replaced in the following call
                known_states.non_dupes.remove(title_author_pair)

            process_new_pair(
                known_states.dupes,
                known_states.non_dupes,
                unscanned_pairs,
                title_author_pair,
                match_score,
            )

    except ValueError:
        print("Saving progress and exiting")
    except Exception:  # pylint: disable=broad-exception-caught
        print("Unexpected error:")
        print(traceback.format_exc())
        print("Saving progress and exiting")
    else:
        print("All title/author pairs scanned!")

    finally:
        with DUPE_RECORD_FILEPATH.open("w", encoding="utf8") as dupe_file:
            json.dump(known_states.to_data(), dupe_file, indent=2)
        print("Updated duplicates saved.")

    return MAP({k: frozenset(v) for k, v in known_states.dupes.items()})
