"""
Created on Apr 7, 2023

@author: fred
"""
from collections import defaultdict
from typing import Optional

from thefuzz import process  # type: ignore

from .types.match_choice import MatchChoice


def process_new_pair(
    dupes: defaultdict[str, set[str]],
    non_dupes: set[str],
    unscanned_pairs: set[str],
    title_author_pair: str,
    match_score: int,
) -> None:
    """Process an unscanned title/author pair"""
    res = process.extractOne(
        title_author_pair,
        (set(dupes.keys()) | set().union(*(dupes.values())) | non_dupes),
        score_cutoff=match_score,
    )
    if res is not None:
        title_author_match, score = res
        print(title_author_match)
        if title_author_match in dupes.keys():
            process_existing_match(dupes, title_author_match, title_author_pair, score)
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
            unscanned_pairs,
            score_cutoff=match_score,
        )

        if res is not None:
            title_author_match, score = res if res is not None else (None, None)
            process_new_match(dupes, title_author_pair, title_author_match, score)
            unscanned_pairs.remove(title_author_match)
        else:
            print(f"No duplicates found for {title_author_pair}")
            non_dupes.add(title_author_pair)


def process_existing_match(
    dupes: dict[str, set[str]],
    existing_match: str,
    new_match: str,
    score: int,
    existing_match_key: Optional[str] = None,
) -> None:
    """If the current pair matched an existing pair, add it"""
    print(f"Tentative match: {new_match} -> {existing_match}, score {score}")
    if existing_match_key is not None:
        in_val_str = f" to {existing_match_key}"
    else:
        in_val_str = ""
    print(f"{existing_match} already deduplicated{in_val_str}.")
    if existing_match_key is not None:
        existing_match = existing_match_key

    print("Choose the best version:")
    print(f"[{MatchChoice.SAVE.value}] {new_match}")
    print(f"[{MatchChoice.SWAP.value}] {existing_match}")
    print(f"[{MatchChoice.SKIP.value}] Not a match")
    print("[e] Save and exit")
    choice = MatchChoice(int(input("Selection: ")))

    if choice == MatchChoice.SAVE:
        dupes[existing_match].add(new_match)
        print(f"{new_match} recorded as duplicate of {existing_match}")
    elif choice == MatchChoice.SWAP:
        dupes[new_match] |= dupes[existing_match]
        print(f"Duplicates of {existing_match} swapped to duplicates of {new_match}")
        dupes[new_match].add(existing_match)
        print(f"{existing_match} recorded as duplicate of {new_match}")
        del dupes[existing_match]
    print()


def process_new_match(
    dupes: dict[str, set[str]],
    title_author_pair: str,
    title_author_match: str,
    score: int,
) -> None:
    """If two previously-unseen pairs matched, add them both"""
    print(f"Tentative match found: {title_author_pair} -> {title_author_match}, score {score}")
    print("Choose the best version:")
    print(f"[{MatchChoice.SAVE.value}] {title_author_pair}")
    print(f"[{MatchChoice.SWAP.value}] {title_author_match}")
    print(f"[{MatchChoice.SKIP.value}] Not a match")
    print("[e] Save and exit")
    choice = MatchChoice(int(input("Selection: ")))

    if choice == MatchChoice.SAVE:
        dupes[title_author_pair].add(title_author_match)
        print(f"{title_author_match} recorded as duplicate of {title_author_pair}")
    elif choice == MatchChoice.SWAP:
        dupes[title_author_match].add(title_author_pair)
        print(f"{title_author_pair} recorded as duplicate of {title_author_match}")

    print()
