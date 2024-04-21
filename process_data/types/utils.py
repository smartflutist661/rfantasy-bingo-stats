"""
Created on Apr 7, 2023

@author: fred
"""
from collections import Counter
from typing import (
    Any,
    Mapping,
    cast,
)

from .defined_types import (
    Author,
    Book,
    CardID,
    SquareName,
)

ANY_DATA_TYPES = (list, dict, int, str, float, bool)
AnyData = list[Any] | dict[str, Any] | int | str | float | bool


def to_data(data: Any) -> AnyData:
    """Send basic types to JSON data recursively"""
    if isinstance(data, Mapping):
        dict_vals = {key: to_data(val) for key, val in data.items()}
        try:
            return dict(sorted(dict_vals.items()))
        except TypeError:
            return dict_vals
    if isinstance(data, (list, set)):
        list_vals = [to_data(val) for val in data]
        try:
            return sorted(list_vals)
        except TypeError:
            return list_vals
    if not isinstance(data, ANY_DATA_TYPES):
        try:
            return cast(AnyData, data.to_data())
        except Exception as exc:
            raise ValueError(f"Unable to process {type(data)}. Please implement.") from exc

    return data


def book_counter_from_data(data: dict[Any, Any]) -> Counter[Book]:
    """Shortcut for getting book counter from data"""
    return Counter({Book(str(key)): int(cast(int, val)) for key, val in data.items()})


def author_counter_from_data(data: dict[Any, Any]) -> Counter[Author]:
    """Shortcut for getting author counter from data"""
    return Counter({Author(str(key)): int(cast(int, val)) for key, val in data.items()})


def square_name_counter_from_data(data: dict[Any, Any]) -> Counter[SquareName]:
    """Shortcut for getting square name counter from data"""
    return Counter({SquareName(str(key)): int(cast(int, val)) for key, val in data.items()})


def card_id_counter_from_data(data: dict[Any, Any]) -> Counter[CardID]:
    """Shortcut for getting square name counter from data"""
    return Counter({CardID(str(key)): int(cast(int, val)) for key, val in data.items()})
