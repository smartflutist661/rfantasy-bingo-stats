"""
Created on Apr 7, 2023

@author: fred
"""
from pathlib import Path

ROOT = Path(__file__).parent

BINGO_DATA_FILEPATH: Path = ROOT / "raw_bingo_data.ods"

OUTPUT_DF_FILEPATH: Path = ROOT / "updated_bingo_data.csv"
OUTPUT_MD_FILEPATH: Path = ROOT / "bingo_stats_rough_draft.md"
OUTPUT_STATS_FILEPATH: Path = ROOT / "bingo_stats.json"

OUTPUT_IMAGE_ROOT: Path = ROOT / "plots"
