"""
Created on Apr 21, 2024

@author: fred
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import (
    Any,
    Optional,
)


@dataclass(frozen=True)
class YearlyBingoStatistics:
    """
    Summary statistics for comparing year-over-year changes in Bingo

    Mostly a convenience class for deserializing manually-acquired data
    """

    total_participant_count: int
    total_card_count: int
    total_square_count: Optional[int]
    total_story_count: Optional[int]
    unique_story_count: Optional[int]
    total_author_count: Optional[int]
    unique_author_count: Optional[int]
    hard_mode_cards: Optional[int]
    hard_mode_squares: Optional[int]
    hero_mode_cards: Optional[int]
    total_misspellings: Optional[int]

    @classmethod
    def from_data(cls, data: Any) -> YearlyBingoStatistics:
        """Create BingoStatistics from JSON data"""
        return cls(
            total_participant_count=int(data["total_participant_count"]),
            total_card_count=int(data["total_card_count"]),
            total_square_count=(
                int(data["total_square_count"]) if data["total_square_count"] is not None else None
            ),
            total_story_count=(
                int(data["total_story_count"]) if data["total_story_count"] is not None else None
            ),
            unique_story_count=(
                int(data["unique_story_count"]) if data["unique_story_count"] is not None else None
            ),
            total_author_count=(
                int(data["total_author_count"]) if data["total_author_count"] is not None else None
            ),
            unique_author_count=(
                int(data["unique_author_count"])
                if data["unique_author_count"] is not None
                else None
            ),
            hard_mode_cards=(
                int(data["hard_mode_cards"]) if data["hard_mode_cards"] is not None else None
            ),
            hard_mode_squares=(
                int(data["hard_mode_squares"]) if data["hard_mode_squares"] is not None else None
            ),
            hero_mode_cards=(
                int(data["hero_mode_cards"]) if data["hero_mode_cards"] is not None else None
            ),
            total_misspellings=(
                int(data["total_misspellings"]) if data["total_misspellings"] is not None else None
            ),
        )
