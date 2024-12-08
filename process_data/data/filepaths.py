"""
Created on Apr 7, 2023

@author: fred
"""
from pathlib import Path

DUPE_RECORD_FILEPATH: Path = Path(__file__).parent / "resolved_duplicates.json"
IGNORED_RECORD_FILEPATH: Path = Path(__file__).parent / "ignored_duplicates.json"
