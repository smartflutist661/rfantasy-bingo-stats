"""
Created on Apr 7, 2023

@author: fred
"""
from dataclasses import dataclass
from typing import (
    Literal,
    Optional,
)


@dataclass(frozen=True)
class AuthorInfo:
    """Information about a single author"""

    gender: Literal["Man", "Woman", "Nonbinary", "Unknown"] = "Unknown"
    race: Literal["White", "Black", "Asian", "Hispanic", "Native", "Unknown"] = "Unknown"
    queer: Optional[bool] = None
    nationality: Literal["Unknown"] = "Unknown"
