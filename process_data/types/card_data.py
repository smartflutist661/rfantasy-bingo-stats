"""
Created on Apr 21, 2024

@author: fred
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import (
    dataclass,
    fields,
)
from types import MappingProxyType as MAP
from typing import Any

from .defined_types import (
    AuthorCol,
    HardModeCol,
    SquareName,
    TitleAuthorHMCols,
    TitleCol,
)
from .utils import (
    AnyData,
    to_data,
)


@dataclass(frozen=True)
class CardData:
    """All summary statistics for a year of Bingo"""

    short_story_square_num: int
    square_names: Mapping[TitleCol, SquareName]
    novel_title_author_hm_cols: tuple[TitleAuthorHMCols, ...]
    short_story_title_author_hm_cols: tuple[TitleAuthorHMCols, ...]

    @property
    def all_title_author_hm_columns(self) -> tuple[TitleAuthorHMCols, ...]:
        return self.novel_title_author_hm_cols + self.short_story_title_author_hm_cols

    @classmethod
    def from_data(cls, data: Any) -> CardData:
        """Create BingoStatistics from JSON data"""
        return cls(
            short_story_square_num=int(data["short_story_square_num"]),
            square_names=MAP(
                {TitleCol(str(key)): SquareName(str(val)) for key, val in data["square_names"]}
            ),
            novel_title_author_hm_cols=tuple(
                (TitleCol(val0), AuthorCol(val1), HardModeCol(val2))
                for val0, val1, val2 in data["novel_title_author_hm_cols"]
            ),
            short_story_title_author_hm_cols=tuple(
                (TitleCol(val0), AuthorCol(val1), HardModeCol(val2))
                for val0, val1, val2 in data["short_story_title_author_hm_cols"]
            ),
        )

    def to_data(self) -> dict[str, Any]:
        """Write to JSON data"""
        out: dict[str, AnyData] = {}
        for field_name, field_val in {
            field.name: getattr(self, field.name) for field in fields(self)
        }.items():
            out[field_name] = to_data(field_val)
        return out
