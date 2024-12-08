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
        TitleCol("SQUARE 1: TITLE"): SquareName("LGBTQIA List Book"),
        TitleCol("SQUARE 2: TITLE"): SquareName("Weird Ecology"),
        TitleCol("SQUARE 3: TITLE"): SquareName("Two or More Authors"),
        TitleCol("SQUARE 4: TITLE"): SquareName("Historical SFF"),
        TitleCol("SQUARE 5: TITLE"): SquareName("Set In Space"),
        TitleCol("SQUARE 6: TITLE"): SquareName("Stand-alone"),
        TitleCol("SQUARE 7: TITLE"): SquareName("Anti-Hero"),
        TitleCol("SQUARE 8: TITLE"): SquareName("Book Club or Readalong Book"),
        TitleCol("SQUARE 9: TITLE"): SquareName("Cool Weapon"),
        TitleCol("SQUARE 10: TITLE"): SquareName("Revolutions and Rebellions"),
        TitleCol("SQUARE 11: TITLE"): SquareName("Name in the Title"),
        TitleCol("SQUARE 12: TITLE"): SquareName("Author Uses Initials"),
        TitleCol("SQUARE 13: TITLE"): SquareName("Published in 2022"),
        TitleCol("SQUARE 14: TITLE"): SquareName("Urban Fantasy"),
        TitleCol("SQUARE 15: TITLE"): SquareName("Set in Africa"),
        TitleCol("SQUARE 16: TITLE"): SquareName("Non-Human Protagonist"),
        TitleCol("SQUARE 17: TITLE"): SquareName("Wibbly Wobbly Timey Wimey"),
        TitleCol(
            "SQUARE 18: TITLE OF COLLECTION/ANTHOLOGY (go to 18A if you did 5 short stories)"
        ): SquareName("Five Short Stories"),
        TitleCol("SQUARE 19: TITLE"): SquareName("Mental Health"),
        TitleCol("SQUARE 20: TITLE"): SquareName("Self-Published"),
        TitleCol("SQUARE 21: TITLE"): SquareName("Award Finalist"),
        TitleCol("SQUARE 22: TITLE"): SquareName("BIPOC Author"),
        TitleCol("SQUARE 23: TITLE"): SquareName("Shapeshifters"),
        TitleCol("SQUARE 24: TITLE"): SquareName("No Ifs, Ands, or Buts"),
        TitleCol("SQUARE 25: TITLE"): SquareName("Family Matters"),
    },
)


NOVEL_TITLE_AUTHOR_HM_COLS: tuple[TitleAuthorHMCols, ...] = (
    (
        TitleCol("SQUARE 1: TITLE"),
        AuthorCol("SQUARE 1: AUTHOR"),
        HardModeCol("SQUARE 1: HARD MODE: A book or series that received ten votes or less."),
    ),
    (
        TitleCol("SQUARE 2: TITLE"),
        AuthorCol("SQUARE 2: AUTHOR"),
        HardModeCol("SQUARE 2: HARD MODE: Not written by Jeff VanderMeer or China Miéville."),
    ),
    (
        TitleCol("SQUARE 3: TITLE"),
        AuthorCol("SQUARE 3: AUTHOR"),
        HardModeCol("SQUARE 3: HARD MODE: Three or more authors."),
    ),
    (
        TitleCol("SQUARE 4: TITLE"),
        AuthorCol("SQUARE 4: AUTHOR"),
        HardModeCol("SQUARE 4: HARD MODE: Not based in Britain or Ireland."),
    ),
    (
        TitleCol("SQUARE 5: TITLE"),
        AuthorCol("SQUARE 5: AUTHOR"),
        HardModeCol(
            "SQUARE 5: HARD MODE: Characters are not originally from Earth. It is acceptable for the characters to be descendants of Earthlings as long as they are not themselves from Earth."
        ),
    ),
    (
        TitleCol("SQUARE 6: TITLE"),
        AuthorCol("SQUARE 6: AUTHOR"),
        HardModeCol("SQUARE 6: HARD MODE: Not on r/Fantasy’s Favorite Standalones List."),
    ),
    (
        TitleCol("SQUARE 7: TITLE"),
        AuthorCol("SQUARE 7: AUTHOR"),
        HardModeCol("SQUARE 7: HARD MODE: A YA book with an anti-hero."),
    ),
    (
        TitleCol("SQUARE 8: TITLE"),
        AuthorCol("SQUARE 8: AUTHOR"),
        HardModeCol(
            "SQUARE 8: HARD MODE: Must read a current selection of either a book club or readalong and participate in the discussion."
        ),
    ),
    (
        TitleCol("SQUARE 9: TITLE"),
        AuthorCol("SQUARE 9: AUTHOR"),
        HardModeCol(
            "SQUARE 9: HARD MODE: Weapon has a unique name. Examples: Excalibur from Arthurian legend, Dragnipur in Malazan, Sting in Lord of the Rings, etc."
        ),
    ),
    (
        TitleCol("SQUARE 10: TITLE"),
        AuthorCol("SQUARE 10: AUTHOR"),
        HardModeCol("SQUARE 10: HARD MODE: Revolution/Rebellion is the main focus of the plot."),
    ),
    (
        TitleCol("SQUARE 11: TITLE"),
        AuthorCol("SQUARE 11: AUTHOR"),
        HardModeCol(
            "SQUARE 11: HARD MODE: The title has the character’s first and last name. Example: The First Fifteen Lives of Harry August."
        ),
    ),
    (
        TitleCol("SQUARE 12: TITLE"),
        AuthorCol("SQUARE 12: AUTHOR"),
        HardModeCol(
            "SQUARE 12: HARD MODE: Initials are a pseudonym and not from the author’s actual name. Examples: T. Kingfisher or K. J. Parker. ADDENDUM: Please do not go snooping to see if a name fits. If it isn't clear based on an author's webpage or social media, assume that it is their real name."
        ),
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
        HardModeCol("SQUARE 14: HARD MODE: Book has an LGBTQ+ POV character."),
    ),
    (
        TitleCol("SQUARE 15: TITLE"),
        AuthorCol("SQUARE 15: AUTHOR"),
        HardModeCol("SQUARE 15: HARD MODE: Author is of African heritage."),
    ),
    (
        TitleCol("SQUARE 16: TITLE"),
        AuthorCol("SQUARE 16: AUTHOR"),
        HardModeCol(
            "SQUARE 16: HARD MODE: Non-humanoid protagonist. No elves, angels, dwarves, hobbits, or humanoid aliens."
        ),
    ),
    (
        TitleCol("SQUARE 17: TITLE"),
        AuthorCol("SQUARE 17: AUTHOR"),
        HardModeCol(
            "SQUARE 17: HARD MODE: No time travel. Book involves something off about time that’s not necessarily time travel. Example: In The Chronicles of Narnia, time moves at a different speed in Narnia than in the real world."
        ),
    ),
    (
        TitleCol(
            "SQUARE 18: TITLE OF COLLECTION/ANTHOLOGY (go to 18A if you did 5 short stories)"
        ),
        AuthorCol("SQUARE 18: AUTHOR/EDITOR (go to 18A if you did 5 short stories)"),
        HardModeCol("SQUARE 18: HARD MODE: Read an entire SFF anthology or collection."),
    ),
    (
        TitleCol("SQUARE 19: TITLE"),
        AuthorCol("SQUARE 19: AUTHOR"),
        HardModeCol(
            "SQUARE 19: HARD MODE: Not The Stormlight Archive or any books in the linked list."
        ),
    ),
    (
        TitleCol("SQUARE 20: TITLE"),
        AuthorCol("SQUARE 20: AUTHOR"),
        HardModeCol(
            "SQUARE 20: HARD MODE: Self-published and has fewer than 100 ratings on Goodreads, OR an indie publisher that has done an AMA with r/Fantasy."
        ),
    ),
    (
        TitleCol("SQUARE 21: TITLE"),
        AuthorCol("SQUARE 21: AUTHOR"),
        HardModeCol("SQUARE 21: HARD MODE: Neither Hugo-nominated nor Nebula-nominate."),
    ),
    (
        TitleCol("SQUARE 22: TITLE"),
        AuthorCol("SQUARE 22: AUTHOR"),
        HardModeCol("SQUARE 22: HARD MODE: A book written by an Indigenous author."),
    ),
    (
        TitleCol("SQUARE 23: TITLE"),
        AuthorCol("SQUARE 23: AUTHOR"),
        HardModeCol(
            "SQUARE 23: HARD MODE: Most prominent shifter is not a wolf/dog shifter. For instance, werewolves can exist but can’t be the most notable shifter characters/main characters."
        ),
    ),
    (
        TitleCol("SQUARE 24: TITLE"),
        AuthorCol("SQUARE 24: AUTHOR"),
        HardModeCol("SQUARE 24: HARD MODE: Title is three words or more."),
    ),
    (
        TitleCol("SQUARE 25: TITLE"),
        AuthorCol("SQUARE 25: AUTHOR"),
        HardModeCol(
            "SQUARE 25: HARD MODE: Features at least three generations in a single family."
        ),
    ),
)

SHORT_STORY_TITLE_AUTHOR_HM_COLS: tuple[TitleAuthorHMCols, ...] = (
    (
        TitleCol(
            "SQUARE 18A: Title of Short Story #1 (Do not fill out if you read all of a collection/anthology)"
        ),
        AuthorCol("SQUARE 18A: Author of Short Story #1"),
        HardModeCol(""),
    ),
    (
        TitleCol(
            "SQUARE 18B: Title of Short Story #2 (Do not fill out if you read all of a collection/anthology)"
        ),
        AuthorCol("SQUARE 18B: Author of Short Story #2"),
        HardModeCol(""),
    ),
    (
        TitleCol(
            "SQUARE 18C: Title of Short Story #3 (Do not fill out if you read all of a collection/anthology)"
        ),
        AuthorCol("SQUARE 18C: Author of Short Story #3"),
        HardModeCol(""),
    ),
    (
        TitleCol(
            "SQUARE 18D: Title of Short Story #4 (Do not fill out if you read all of a collection/anthology)"
        ),
        AuthorCol("SQUARE 18D: Author of Short Story #4"),
        HardModeCol(""),
    ),
    (
        TitleCol(
            "SQUARE 18E: Title of Short Story #5 (Do not fill out if you read all of a collection/anthology)"
        ),
        AuthorCol("SQUARE 18E: Author of Short Story #5"),
        HardModeCol(""),
    ),
)

ALL_TITLE_AUTHOR_HM_COLUMNS = NOVEL_TITLE_AUTHOR_HM_COLS + SHORT_STORY_TITLE_AUTHOR_HM_COLS
