"""
Created on Apr 7, 2023

@author: fred
"""
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class AuthorInfo:
    """Information about a single author"""

    gender: Literal["man", "woman", "mixed", "nonbinary", "unknown"] = "unknown"
