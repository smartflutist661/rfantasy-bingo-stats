from dataclasses import dataclass
from typing import (
    Mapping,
    Optional,
)

from rfantasy_bingo_stats.models.defined_types import (
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
