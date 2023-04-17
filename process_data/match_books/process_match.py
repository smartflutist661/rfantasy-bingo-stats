"""
Created on Apr 7, 2023

@author: fred
"""
from collections import defaultdict
from typing import (
    AbstractSet,
    Mapping,
    Optional,
    cast,
)

from thefuzz import process  # type: ignore

from ..types.defined_types import BookOrAuthor


def process_new_pair(
    dupes: defaultdict[BookOrAuthor, set[BookOrAuthor]],
    all_matches_to_ignore: defaultdict[BookOrAuthor, set[BookOrAuthor]],
    unscanned_items: set[BookOrAuthor],
    item_to_process: BookOrAuthor,
    match_score: int,
) -> None:
    """Process an unscanned title/author pair"""

    dedupes = set().union(*(dupes.values()))
    all_choices = set(dupes.keys()) | dedupes | unscanned_items
    new_matches_to_ignore: AbstractSet[BookOrAuthor] = set()

    results = process.extractBests(
        query=item_to_process,
        choices=all_choices,
        score_cutoff=match_score,
        limit=len(all_choices),
    )
    existing_match_keys = set()
    possible_matches = {item_to_process}
    if results is not None and len(results) > 0:
        print(f"Matching {item_to_process}:")
        for item_match, _ in results:
            if item_match in dedupes:
                existing_match_keys.add(find_existing_match(dupes, item_match))
            elif item_match in dupes.keys():
                existing_match_keys.add(item_match)
            else:
                possible_matches.add(item_match)

        all_match_choices = (
            frozenset(possible_matches | existing_match_keys)
            - all_matches_to_ignore[item_to_process]
        )

        if len(all_match_choices) > 1:
            best_match, other_matches = get_best_match(original_matched_items=all_match_choices)

            if best_match in (all_choices - all_match_choices) & dedupes:
                old_best = best_match
                best_match = find_existing_match(dupes, old_best)
                print(f"{old_best} already deduped to {best_match}. Using {best_match}.")

            new_matches_to_ignore = all_match_choices - (
                other_matches | {best_match, item_to_process}
            )

        else:
            print(f"No new matches for {item_to_process}.")
            best_match = None

    else:
        best_match = None

    all_matches_to_ignore[item_to_process] |= new_matches_to_ignore
    for match_to_ignore in new_matches_to_ignore:
        all_matches_to_ignore[match_to_ignore].add(item_to_process)

    if best_match is None:
        print(f"No duplicates found for {item_to_process}")
        dupes[item_to_process] |= set()
    else:
        # Intersection discards matches removed in `get_best_match`
        possible_matches &= other_matches
        existing_match_keys &= other_matches

        # This discards the match chosen from one of these two sets
        possible_matches.discard(best_match)
        existing_match_keys.discard(best_match)

        unify_matches(
            dupes=dupes,
            best_match=best_match,
            other_matches=frozenset(possible_matches),
            existing_match_keys=frozenset(existing_match_keys),
        )

        # Drop matches that were just unified
        unscanned_items -= possible_matches
        unscanned_items -= existing_match_keys
        unscanned_items.discard(best_match)


def find_existing_match(
    dupes: Mapping[BookOrAuthor, AbstractSet[BookOrAuthor]],
    current_match: BookOrAuthor,
) -> BookOrAuthor:
    """Determine which key to use for existing match"""

    for existing_match_key, dupe_tuples in dupes.items():
        if current_match in dupe_tuples:
            return existing_match_key

    raise ValueError(
        f"{current_match} was found in existing dupes, but matching key could not be found."
    )


def get_best_match(
    original_matched_items: AbstractSet[BookOrAuthor],
) -> tuple[Optional[BookOrAuthor], frozenset[BookOrAuthor]]:
    """Process all possible matches for a book"""

    matched_items = set(original_matched_items)
    choice = "d"
    while choice == "d":
        match_choices = tuple(matched_items)
        print("Choose the best version:")
        for choice_num, match_choice in enumerate(match_choices):
            print(f"[{choice_num}] {match_choice}")
        print()
        print("[r] Remove one or more matches")
        print("[c] Enter a better version of all")
        print("[e] Save and exit")
        choice = input("Selection: ")
        if choice == "r":
            while len(matched_items) > 1 and choice != "d":
                choice = input("Match to remove ([d] for done): ")
                if choice != "d":
                    matched_items.remove(match_choices[int(choice)])
        elif choice == "c":
            return cast(
                BookOrAuthor,
                input("Enter a better version, being sure to use the proper format:\n"),
            ), frozenset(matched_items)

    if len(matched_items) > 1:
        return match_choices[int(choice)], frozenset(matched_items)
    return None, frozenset()


def unify_matches(
    dupes: defaultdict[BookOrAuthor, set[BookOrAuthor]],
    best_match: BookOrAuthor,
    other_matches: frozenset[BookOrAuthor],
    existing_match_keys: frozenset[BookOrAuthor],
) -> None:
    """Unify all books associated with other match and existing key to best match"""

    for existing_key in existing_match_keys:
        dupes[best_match] |= dupes[existing_key]
        dupes[best_match].add(existing_key)
        del dupes[existing_key]
        print(f"Duplicates of {existing_key} swapped to duplicates of {best_match}")

    if len(other_matches) > 0:
        dupes[best_match] |= other_matches
        print(
            f"{', '.join(other_matches)} recorded as duplicate{'s'*(len(other_matches) > 1)} of {best_match}"
        )
