"""
Created on Apr 7, 2023

@author: fred
"""

from enum import Enum


class MatchChoice(Enum):
    """Available choices when a possible match is found"""

    MATCH = 1
    NEW = 2
    SKIP = 3
