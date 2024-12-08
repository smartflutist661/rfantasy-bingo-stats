"""
Created on Apr 7, 2023

@author: fred
"""
from collections import defaultdict
from types import MappingProxyType as MAP
from typing import (
    Mapping,
    cast,
)

from ..types.author_info import AuthorInfo
from ..types.defined_types import Author

AUTHOR_INFO: Mapping[Author, AuthorInfo] = MAP(
    defaultdict(
        AuthorInfo,
        cast(dict[Author, AuthorInfo], {}),
    )
)
