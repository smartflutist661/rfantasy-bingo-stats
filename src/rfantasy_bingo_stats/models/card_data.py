from collections.abc import Mapping

from pydantic.main import BaseModel

from rfantasy_bingo_stats.models.defined_types import (
    SquareName,
    TitleAuthorHMCols,
    TitleCol,
)


class CardData(BaseModel):
    """All summary statistics for a year of Bingo"""

    sheet_name: str
    subbed_by_square: bool
    short_story_square_num: int
    square_names: Mapping[TitleCol, SquareName]
    novel_title_author_hm_cols: tuple[TitleAuthorHMCols, ...]
    short_story_title_author_hm_cols: tuple[TitleAuthorHMCols, ...]

    @property
    def all_title_author_hm_columns(self) -> tuple[TitleAuthorHMCols, ...]:
        return self.novel_title_author_hm_cols + self.short_story_title_author_hm_cols
