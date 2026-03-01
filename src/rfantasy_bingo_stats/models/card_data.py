from collections.abc import Mapping
from re import sub
from typing import Optional

from pydantic.main import BaseModel

from rfantasy_bingo_stats.models.defined_types import (
    SquareName,
    TitleAuthorHMCols,
    TitleCol,
)


def square_name_to_file(s: str) -> str:
    """
    Sanitize square name for URL-intended filenames

    For simplicity, strip all except alphanumeric characters
    """
    return "-".join(
        sub(
            r"[^a-zA-Z0-9]+",
            " ",
            sub(
                r"[a-zA-Z0-9]+",
                lambda mo: " " + mo.group(0).lower(),  # type: ignore[operator] # Not sure why this thinks it's bytes
                s,
            ),
        ).split()
    )


class CardData(BaseModel):
    """All summary statistics for a year of Bingo"""

    sheet_name: str
    subbed_by_square: bool
    short_story_square_num: int
    square_names: Mapping[TitleCol, SquareName]
    novel_title_author_hm_cols: tuple[TitleAuthorHMCols, ...]
    short_story_title_author_hm_cols: tuple[TitleAuthorHMCols, ...]
    _square_names_to_files: Optional[Mapping[SquareName, str]] = None

    @property
    def all_title_author_hm_columns(self) -> tuple[TitleAuthorHMCols, ...]:
        return self.novel_title_author_hm_cols + self.short_story_title_author_hm_cols

    @property
    def square_names_to_files(self) -> Mapping[SquareName, str]:
        if self._square_names_to_files is None:
            out = {}
            for square_name in self.square_names.values():
                out[square_name] = square_name_to_file(square_name)
            self._square_names_to_files = out
        return self._square_names_to_files
