"""
Created on Apr 7, 2023

@author: fred
"""

from dataclasses import dataclass
from typing import (
    Mapping,
    Optional,
)

from .defined_types import (
    Author,
    SquareName,
    Title,
    TitleAuthor,
)


@dataclass(frozen=True)
class BingoSquare:
    """A single bingo square"""

    title: Title
    author: Author
    hard_mode: bool


@dataclass(frozen=True)
class ShortStorySquare(BingoSquare):
    """A short story square"""

    stories: tuple[TitleAuthor, ...]


@dataclass(frozen=True)
class BingoCard:
    squares: Mapping[SquareName, Optional[BingoSquare]]
    subbed_square_map: Mapping[SquareName, SquareName]
