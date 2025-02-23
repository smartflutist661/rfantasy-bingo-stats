from typing import Optional

from pydantic.fields import Field
from pydantic.main import BaseModel

from rfantasy_bingo_stats.constants import CURRENT_YEAR


class BingoArgs(BaseModel):
    show_plots: bool = Field(
        description="Pass to display plots as well as saving them.",
    )
    year: int = Field(
        default=CURRENT_YEAR - 1,
        description="Pass to process a year other than the current.",
    )


class PollArgs(BaseModel):
    poll_post_id: Optional[str] = Field(
        default=None,
        description="ID of the Reddit post hosting the poll",
    )
    poll_type: str = Field(description="Poll class, e.g. Top Novels")
    force_refresh: bool = Field(description="Force re-download of the poll results")
    year: int = Field(
        default=CURRENT_YEAR,
        description="Pass to process a year other than the current.",
    )


class Args(BaseModel):
    match_score: int = Field(
        default=90,
        description="""
        The minimum score to allow for a match. Fairly sensitive.
        Default = 90
        """,
    )
    rescan_keys: bool = Field(
        description="""
        Pass this to check for duplicates on pairs that were previously not matched.
        Best paired with a lower `match-score` than the default.
        """,
    )
    skip_updates: bool = Field(
        description="Use the existing resolved duplicates, don't attempt to find new duplicates",
    )
    skip_authors: bool = Field(
        description="Skip deduplicating authors, go straight to books",
    )
    github_pat: Optional[str] = Field(
        default=None,
        description="Pass to automatically commit and push changes to GitHub",
    )
