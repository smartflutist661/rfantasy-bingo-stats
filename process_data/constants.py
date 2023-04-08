"""
Created on Apr 7, 2023

@author: fred
"""
from pathlib import Path
from types import MappingProxyType as MAP
from typing import (
    Mapping,
    cast,
)

from .types.defined_types import (
    SquareName,
    SquareNumber,
    TitleAuthorHMCols,
    TitleCol,
)

BINGO_DATA_FILEPATH: Path = Path(__file__).parent.parent / "bingo_data.ods"
DUPE_RECORD_FILEPATH: Path = Path(__file__).parent / "resolved_duplicates.json"

OUTPUT_DF_FILEPATH: Path = Path(__file__).parent / "updated_bingo_data.csv"
OUTPUT_MD_FILEPATH: Path = Path(__file__).parent / "bingo_stats_rough_draft.md"

CUSTOM_SEPARATOR = " /// "

SHORT_STORY_SQUARE_NUM = "18"


SQUARE_NAMES: Mapping[TitleCol, SquareName] = MAP(
    cast(
        dict[TitleCol, SquareName],
        {
            "SQUARE 1: TITLE": "LGBTQIA List Book",
            "SQUARE 2: TITLE": "Weird Ecology",
            "SQUARE 3: TITLE": "Two or More Authors",
            "SQUARE 4: TITLE": "Historical SFF",
            "SQUARE 5: TITLE": "Set In Space",
            "SQUARE 6: TITLE": "Stand-alone",
            "SQUARE 7: TITLE": "Anti-Hero",
            "SQUARE 8: TITLE": "Book Club or Readalong Book",
            "SQUARE 9: TITLE": "Cool Weapon",
            "SQUARE 10: TITLE": "Revolutions and Rebellions",
            "SQUARE 11: TITLE": "Name in the Title",
            "SQUARE 12: TITLE": "Author Uses Initials",
            "SQUARE 13: TITLE": "Published in 2022",
            "SQUARE 14: TITLE": "Urban Fantasy",
            "SQUARE 15: TITLE": "Set in Africa",
            "SQUARE 16: TITLE": "Non-Human Protagonist",
            "SQUARE 17: TITLE": "Wibbly Wobbly Timey Wimey",
            "SQUARE 18: TITLE OF COLLECTION/ANTHOLOGY (go to 18A if you did 5 short stories)": "Five Short Stories",
            "SQUARE 19: TITLE": "Mental Health",
            "SQUARE 20: TITLE": "Self-Published",
            "SQUARE 21: TITLE": "Award Finalist",
            "SQUARE 22: TITLE": "BIPOC Author",
            "SQUARE 23: TITLE": "Shapeshifters",
            "SQUARE 24: TITLE": "No Ifs, Ands, or Buts",
            "SQUARE 25: TITLE": "Family Matters",
        },
    )
)


NOVEL_TITLE_AUTHOR_HM_COLS: tuple[TitleAuthorHMCols, ...] = cast(
    tuple[TitleAuthorHMCols, ...],
    (
        ("SQUARE 1: TITLE", "SQUARE 1: AUTHOR"),
        ("SQUARE 2: TITLE", "SQUARE 2: AUTHOR"),
        ("SQUARE 3: TITLE", "SQUARE 3: AUTHOR"),
        ("SQUARE 4: TITLE", "SQUARE 4: AUTHOR"),
        ("SQUARE 5: TITLE", "SQUARE 5: AUTHOR"),
        ("SQUARE 6: TITLE", "SQUARE 6: AUTHOR"),
        ("SQUARE 7: TITLE", "SQUARE 7: AUTHOR"),
        ("SQUARE 8: TITLE", "SQUARE 8: AUTHOR"),
        ("SQUARE 9: TITLE", "SQUARE 9: AUTHOR"),
        ("SQUARE 10: TITLE", "SQUARE 10: AUTHOR"),
        ("SQUARE 11: TITLE", "SQUARE 11: AUTHOR"),
        ("SQUARE 12: TITLE", "SQUARE 12: AUTHOR"),
        ("SQUARE 13: TITLE", "SQUARE 13: AUTHOR"),
        ("SQUARE 14: TITLE", "SQUARE 14: AUTHOR"),
        ("SQUARE 15: TITLE", "SQUARE 15: AUTHOR"),
        ("SQUARE 16: TITLE", "SQUARE 16: AUTHOR"),
        ("SQUARE 17: TITLE", "SQUARE 17: AUTHOR"),
        (
            "SQUARE 18: TITLE OF COLLECTION/ANTHOLOGY (go to 18A if you did 5 short stories)",
            "SQUARE 18: AUTHOR/EDITOR (go to 18A if you did 5 short stories)",
        ),
        ("SQUARE 19: TITLE", "SQUARE 19: AUTHOR"),
        ("SQUARE 20: TITLE", "SQUARE 20: AUTHOR"),
        ("SQUARE 21: TITLE", "SQUARE 21: AUTHOR"),
        ("SQUARE 22: TITLE", "SQUARE 22: AUTHOR"),
        ("SQUARE 23: TITLE", "SQUARE 23: AUTHOR"),
        ("SQUARE 24: TITLE", "SQUARE 24: AUTHOR"),
        ("SQUARE 25: TITLE", "SQUARE 25: AUTHOR"),
    ),
)

SHORT_STORY_TITLE_AUTHOR_HM_COLS = cast(
    tuple[TitleAuthorHMCols, ...],
    (
        (
            "SQUARE 18A: Title of Short Story #1 (Do not fill out if you read all of a collection/anthology)",
            "SQUARE 18A: Author of Short Story #1)",
        ),
        (
            "SQUARE 18B: Title of Short Story #2 (Do not fill out if you read all of a collection/anthology)",
            "SQUARE 18B: Author of Short Story #2",
        ),
        (
            "SQUARE 18C: Title of Short Story #3 (Do not fill out if you read all of a collection/anthology)",
            "SQUARE 18C: Author of Short Story #3",
        ),
        (
            "SQUARE 18D: Title of Short Story #4 (Do not fill out if you read all of a collection/anthology)",
            "SQUARE 18D: Author of Short Story #4",
        ),
        (
            "SQUARE 18E: Title of Short Story #5 (Do not fill out if you read all of a collection/anthology)",
            "SQUARE 18E: Author of Short Story #5",
        ),
    ),
)

ALL_TITLE_AUTHOR_HM_COLUMNS = NOVEL_TITLE_AUTHOR_HM_COLS + SHORT_STORY_TITLE_AUTHOR_HM_COLS
