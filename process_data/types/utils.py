"""
Created on Apr 7, 2023

@author: fred
"""
from typing import (
    Any,
    Mapping,
    cast,
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
