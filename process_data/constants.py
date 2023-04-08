"""
Created on Apr 7, 2023

@author: fred
"""
from pathlib import Path
from types import MappingProxyType as MAP

BINGO_DATA_FILEPATH: Path = Path(__file__).parent.parent / "bingo_data.ods"
DUPE_RECORD_FILEPATH: Path = Path(__file__).parent / "resolved_duplicates.json"

OUTPUT_DF_FILEPATH: Path = Path(__file__).parent / "updated_bingo_data.csv"

CUSTOM_SEPARATOR = " /// "

SQUARE_NAMES = MAP(
    {
        "SQUARE 1": "LGBTQIA List Book",
        "SQUARE 2": "Weird Ecology",
        "SQUARE 3": "Two or More Authors",
        "SQUARE 4": "Historical SFF",
        "SQUARE 5": "Set in Space",
        "SQUARE 6": "Standalone",
        "SQUARE 7": "Anti-Hero",
        "SQUARE 8": "Book Club/Readalong",
        "SQUARE 9": "Cool Weapon",
        "SQUARE 10": "Revolutions and Rebellions",
        "SQUARE 11": "Name in the Title",
        "SQUARE 12": "Author Uses Initials",
        "SQUARE 13": "Published in 2022",
        "SQUARE 14": "Urban Fantasy",
        "SQUARE 15": "Set in Africa",
        "SQUARE 16": "Non-Human Protagonist",
        "SQUARE 17": "Wibbly-Wobbly Timey-Wimey",
        "SQUARE 18": "Five Short Stories",
        "SQUARE 19": "Mental Health",
        "SQUARE 20": "Self-Published/Indie Publisher",
        "SQUARE 21": "Award Finalist",
        "SQUARE 22": "BIPOC Author",
        "SQUARE 23": "Shapeshifters",
        "SQUARE 24": "No Ifs, Ands, or Buts",
        "SQUARE 25": "Family Matters",
    }
)
