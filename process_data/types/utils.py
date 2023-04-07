"""
Created on Apr 7, 2023

@author: fred
"""
from typing import Any

ANY_DATA_TYPES = (list, dict, int, str, float, bool)
AnyData = list[Any] | dict[str, Any] | int | str | float | bool


def to_data(data: Any) -> AnyData:
    """Send basic types to JSON data recursively"""
    if isinstance(data, dict):
        return {key: to_data(val) for key, val in data.items()}
    if isinstance(data, (list, set)):
        return [to_data(val) for val in data]
    if not isinstance(data, ANY_DATA_TYPES):
        raise ValueError(f"Unable to process {type(data)}. Please implement.")

    return data
