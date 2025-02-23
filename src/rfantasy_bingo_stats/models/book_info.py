from enum import StrEnum
from math import isnan
from typing import (
    Any,
    Optional,
)

from pydantic.functional_validators import field_validator
from pydantic.main import BaseModel
from pydantic.type_adapter import TypeAdapter

from rfantasy_bingo_stats.models.defined_types import (
    Book,
    Series,
    SortedMapping,
)


class Genre(StrEnum):
    HOR = "Horror"
    U = "Unknown"


class StoryType(StrEnum):
    SHRT = "Short Story"
    ANTH = "Anthology"
    COLL = "Collection"
    NOVELLA = "Novella"
    NOVEL = "Novel"
    WEB = "Webnovel"
    GRPH = "Graphic Novel"
    LN = "Light Novel"
    U = "Unknown"


class AgeRange(StrEnum):
    A = "Adult"
    YA = "Young Adult"
    MG = "Middle Grade"
    C = "Children's"


class BookInfo(BaseModel):
    """Information about a single author"""

    standalone: Optional[bool] = None
    self_published: Optional[bool] = None
    queer: Optional[bool] = None
    narrator: Optional[str] = None
    series: Optional[Series] = None
    universe: Optional[str] = None
    genre: Genre = Genre.U
    publication_year: Optional[int] = None

    @field_validator("standalone", "self_published", "queer", mode="plain")
    @classmethod
    def opt_bool(cls, data: Any) -> Optional[bool]:  # type: ignore[explicit-any]
        if data is None or isnan(data):
            return None
        return bool(data)


BookInfoAdapter: TypeAdapter[SortedMapping[Book, BookInfo]] = TypeAdapter(
    SortedMapping[Book, BookInfo]
)
