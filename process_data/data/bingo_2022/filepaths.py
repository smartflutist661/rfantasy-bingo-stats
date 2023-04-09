"""
Created on Apr 7, 2023

@author: fred
"""
from pathlib import Path

BINGO_DATA_FILEPATH: Path = Path(__file__).parent / "raw_bingo_data.ods"

OUTPUT_DF_FILEPATH: Path = Path(__file__).parent / "updated_bingo_data.csv"
OUTPUT_MD_FILEPATH: Path = Path(__file__).parent / "bingo_stats_rough_draft.md"
