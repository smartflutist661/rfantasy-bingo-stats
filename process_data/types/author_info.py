"""
Created on Apr 7, 2023

@author: fred
"""
from dataclasses import dataclass
from typing import (
    Literal,
    Optional,
)

Gender = Literal["Man", "Woman", "Nonbinary", "Unknown"]
Race = Literal["White", "Black", "Asian", "Hispanic", "Native", "Unknown"]
Nationality = Literal["Unknown"]


@dataclass(frozen=True)
class AuthorInfo:
    """Information about a single author"""

    gender: Gender = "Unknown"
    race: Race = "Unknown"
    queer: Optional[bool] = None
    nationality: Nationality = "Unknown"
