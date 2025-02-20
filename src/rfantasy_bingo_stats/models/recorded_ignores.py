from pydantic.main import BaseModel

from rfantasy_bingo_stats.models.defined_types import (
    Author,
    Book,
    SortedDefaultdict,
    SortedSet,
)


class RecordedIgnores(BaseModel):
    """Duplicates that were ignored in the past"""

    ignored_author_dupes: SortedDefaultdict[Author, SortedSet[Author]]
    ignored_book_dupes: SortedDefaultdict[Book, SortedSet[Book]]
