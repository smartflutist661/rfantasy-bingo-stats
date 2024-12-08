"""
Created on Apr 22, 2023

@author: fred
"""

from __future__ import annotations

from collections import Counter
from dataclasses import (
    dataclass,
    fields,
)
from typing import Any

from .defined_types import (
    BingoName,
    CardID,
)
from .utils import (
    AnyData,
    bingo_name_counter_from_data,
    card_id_counter_from_data,
    to_data,
)


@dataclass(frozen=True)
class BingoTypeStatistics:
    """Counters for unique books + authors"""

    complete_bingos_by_card: Counter[CardID]
    incomplete_bingos: Counter[BingoName]
    incomplete_squares_by_bingo: Counter[BingoName]

    @classmethod
    def from_data(cls, data: Any) -> BingoTypeStatistics:
        """Construct from JSON data"""
        return cls(
            complete_bingos_by_card=card_id_counter_from_data(data["complete_bingos_by_card"]),
            incomplete_bingos=bingo_name_counter_from_data(data["incomplete_bingos"]),
            incomplete_squares_by_bingo=bingo_name_counter_from_data(
                data["incomplete_squares_by_bingo"]
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
