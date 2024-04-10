"""
Created on Apr 9, 2023

@author: fred
"""
from types import MappingProxyType as MAP
from typing import Mapping

from ...types.defined_types import (
    AuthorCol,
    HardModeCol,
    SquareName,
    TitleAuthorHMCols,
    TitleCol,
)

SHORT_STORY_SQUARE_NUM = "18"

SQUARE_NAMES: Mapping[TitleCol, SquareName] = MAP(
    {
        TitleCol("SQUARE 1: TITLE"): SquareName("Title with a Title"),
        TitleCol("SQUARE 2: TITLE"): SquareName("Superheroes"),
        TitleCol("SQUARE 3: TITLE"): SquareName("Bottom of the TBR"),
        TitleCol("SQUARE 4: TITLE"): SquareName("Magical Realism"),
        TitleCol("SQUARE 5: TITLE"): SquareName("Young Adult"),
        TitleCol("SQUARE 6: TITLE"): SquareName("Mundane Jobs"),
        TitleCol("SQUARE 7: TITLE"): SquareName("Published in the 2000s"),
        TitleCol("SQUARE 8: TITLE"): SquareName("Angels and Demons"),
        TitleCol(
            "SQUARE 9: TITLE OF COLLECTION/ANTHOLOGY (go to 9A if you did not do Hard Mode)"
        ): SquareName("Five Short Stories"),
        TitleCol("SQUARE 10: TITLE"): SquareName("Horror"),
        TitleCol("SQUARE 11: TITLE"): SquareName("Self Published or Indie Publisher"),
        TitleCol("SQUARE 12: TITLE"): SquareName("Set in the Middle East"),
        TitleCol("SQUARE 13: TITLE"): SquareName("Published in 2023"),
        TitleCol("SQUARE 14: TITLE"): SquareName("Multiverses"),
        TitleCol("SQUARE 15: TITLE"): SquareName("POC Author"),
        TitleCol("SQUARE 16: TITLE"): SquareName("Book Club or Readalong Book"),
        TitleCol("SQUARE 17: TITLE"): SquareName("Novella"),
        TitleCol("SQUARE 18: TITLE"): SquareName("Mythical Beasts"),
        TitleCol("SQUARE 19: TITLE"): SquareName("Elemental Magic"),
        TitleCol("SQUARE 20: TITLE"): SquareName("Myths and Retellings"),
        TitleCol("SQUARE 21: TITLE"): SquareName("Queernorm Setting"),
        TitleCol("SQUARE 22: TITLE"): SquareName("Coastal Setting"),
        TitleCol("SQUARE 23: TITLE"): SquareName("Druid"),
        TitleCol("SQUARE 24: TITLE"): SquareName("Features Robots"),
        TitleCol("SQUARE 25: TITLE"): SquareName("Sequel"),
    },
)


NOVEL_TITLE_AUTHOR_HM_COLS: tuple[TitleAuthorHMCols, ...] = (
    (
        TitleCol("SQUARE 1: TITLE"),
        AuthorCol("SQUARE 1: AUTHOR"),
        HardModeCol("SQUARE 1: HARD MODE"),
    ),
    (
        TitleCol("SQUARE 2: TITLE"),
        AuthorCol("SQUARE 2: AUTHOR"),
        HardModeCol("SQUARE 2: HARD MODE"),
    ),
    (
        TitleCol("SQUARE 3: TITLE"),
        AuthorCol("SQUARE 3: AUTHOR"),
        HardModeCol(""),
    ),
    (
        TitleCol("SQUARE 4: TITLE"),
        AuthorCol("SQUARE 4: AUTHOR"),
        HardModeCol("SQUARE 4: HARD MODE"),
    ),
    (
        TitleCol("SQUARE 5: TITLE"),
        AuthorCol("SQUARE 5: AUTHOR"),
        HardModeCol("SQUARE 5: HARD MODE"),
    ),
    (
        TitleCol("SQUARE 6: TITLE"),
        AuthorCol("SQUARE 6: AUTHOR"),
        HardModeCol("SQUARE 6: HARD MODE"),
    ),
    (
        TitleCol("SQUARE 7: TITLE"),
        AuthorCol("SQUARE 7: AUTHOR"),
        HardModeCol("SQUARE 7: HARD MODE"),
    ),
    (
        TitleCol("SQUARE 8: TITLE"),
        AuthorCol("SQUARE 8: AUTHOR"),
        HardModeCol("SQUARE 8: HARD MODE"),
    ),
    (
        TitleCol("SQUARE 9: TITLE OF COLLECTION/ANTHOLOGY (go to 9A if you did not do Hard Mode)"),
        AuthorCol("SQUARE 9: AUTHOR/EDITOR (go to 9A if you did not do Hard Mode)"),
        HardModeCol("SQUARE 9: HARD MODE"),
    ),
    (
        TitleCol("SQUARE 10: TITLE"),
        AuthorCol("SQUARE 10: AUTHOR"),
        HardModeCol("SQUARE 10: HARD MODE"),
    ),
    (
        TitleCol("SQUARE 11: TITLE"),
        AuthorCol("SQUARE 11: AUTHOR"),
        HardModeCol("SQUARE 11: HARD MODE"),
    ),
    (
        TitleCol("SQUARE 12: TITLE"),
        AuthorCol("SQUARE 12: AUTHOR"),
        HardModeCol("SQUARE 12: HARD MODE: Author is of Middle Eastern heritage."),
    ),
    (
        TitleCol("SQUARE 13: TITLE"),
        AuthorCol("SQUARE 13: AUTHOR"),
        HardModeCol(
            "SQUARE 13: HARD MODE: It's also a debut novel--as in it's the author's first published novel."
        ),
    ),
    (
        TitleCol("SQUARE 14: TITLE"),
        AuthorCol("SQUARE 14: AUTHOR"),
        HardModeCol(
            "SQUARE 14: HARD MODE: Characters do not walk through a literal door in order to get to another world."
        ),
    ),
    (
        TitleCol("SQUARE 15: TITLE"),
        AuthorCol("SQUARE 15: AUTHOR"),
        HardModeCol("SQUARE 15: HARD MODE: Novel takes place in a futuristic, sci-fi world."),
    ),
    (
        TitleCol("SQUARE 16: TITLE"),
        AuthorCol("SQUARE 16: AUTHOR"),
        HardModeCol("SQUARE 16: HARD MODE: Must read a current selection of either a book club or readalong and participate in the discussion."),
    ),
    (
        TitleCol("SQUARE 17: TITLE"),
        AuthorCol("SQUARE 17: AUTHOR"),
        HardModeCol("SQUARE 17: HARD MODE: Novella is NOT published by Tordotcom Publishing."),
    ),
    (
        TitleCol("SQUARE 18: TITLE"),
        AuthorCol("SQUARE 18: AUTHOR"),
        HardModeCol("SQUARE 18: HARD MODE: No dragons or dragon-like creatures (e.g. wyverns, the draccus in The Name of the Wind)."),
    ),
    (
        TitleCol("SQUARE 19: TITLE"),
        AuthorCol("SQUARE 19: AUTHOR"),
        HardModeCol("SQUARE 19: HARD MODE: Not V. E. Schwab’s Shades of Magic series or Jim Butcher’s Codex Alera series."),
    ),
    (
        TitleCol("SQUARE 20: TITLE"),
        AuthorCol("SQUARE 20: AUTHOR"),
        HardModeCol("SQUARE 20: HARD MODE: Not Greek or Roman mythology."),
    ),
    (
        TitleCol("SQUARE 21: TITLE"),
        AuthorCol("SQUARE 21: AUTHOR"),
        HardModeCol("SQUARE 21: HARD MODE: Not a futuristic setting. Takes place in a time akin to ours, in the past, or in a fantasy world that has no science fiction elements."),
    ),
    (
        TitleCol("SQUARE 22: TITLE"),
        AuthorCol("SQUARE 22: AUTHOR"),
        HardModeCol("SQUARE 22: HARD MODE: The book also features seafaring."),
    ),
    (
        TitleCol("SQUARE 23: TITLE"),
        AuthorCol("SQUARE 23: AUTHOR"),
        HardModeCol("SQUARE 23: HARD MODE: Not The Iron Druid Chronicles by Kevin Hearne."),
    ),
    (
        TitleCol("SQUARE 24: TITLE"),
        AuthorCol("SQUARE 24: AUTHOR"),
        HardModeCol("SQUARE 24: HARD MODE: Robot is the protagonist."),
    ),
    (
        TitleCol("SQUARE 25: TITLE"),
        AuthorCol("SQUARE 25: AUTHOR"),
        HardModeCol("SQUARE 25: HARD MODE: Book 3 or later in the series."),
    ),
)

SHORT_STORY_TITLE_AUTHOR_HM_COLS: tuple[TitleAuthorHMCols, ...] = (
    (
        TitleCol(
            "SQUARE 9A: Title of Short Story #1 (Do not fill out if you read a collection/anthology, go to 9 above)"
        ),
        AuthorCol("SQUARE 9A: Author of Short Story #1"),
        HardModeCol(""),
    ),
    (
        TitleCol(
            "SQUARE 9B: Title of Short Story #2 (Do not fill out if you read a collection/anthology, go to 9 above)"
        ),
        AuthorCol("SQUARE 9B: Author of Short Story #2"),
        HardModeCol(""),
    ),
    (
        TitleCol(
            "SQUARE 9C: Title of Short Story #3 (Do not fill out if you read a collection/anthology, go to 9 above)"
        ),
        AuthorCol("SQUARE 9C: Author of Short Story #3"),
        HardModeCol(""),
    ),
    (
        TitleCol(
            "SQUARE 9D: Title of Short Story #4 (Do not fill out if you read a collection/anthology, go to 9 above)"
        ),
        AuthorCol("SQUARE 9D: Author of Short Story #4"),
        HardModeCol(""),
    ),
    (
        TitleCol(
            "SQUARE 9E: Title of Short Story #5 (Do not fill out if you read a collection/anthology, go to 9 above)"
        ),
        AuthorCol("SQUARE 9E: Author of Short Story #5"),
        HardModeCol(""),
    ),
)

ALL_TITLE_AUTHOR_HM_COLUMNS = NOVEL_TITLE_AUTHOR_HM_COLS + SHORT_STORY_TITLE_AUTHOR_HM_COLS
