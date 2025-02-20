from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas

from rfantasy_bingo_stats.models.recorded_ignores import RecordedIgnores
from rfantasy_bingo_stats.models.recorded_states import RecordedDupes


def get_existing_states(
    dupe_path: Path,
    ignore_path: Path,
) -> tuple[RecordedDupes, RecordedIgnores]:
    """Attempt to retrieve existing RecordedDupes, returning empty on failure"""
    try:
        with dupe_path.open("r", encoding="utf8") as dupe_file:
            dupes = RecordedDupes.model_validate_json(dupe_file.read())
        with ignore_path.open("r", encoding="utf8") as ignore_file:
            ignores = RecordedIgnores.model_validate_json(ignore_file.read())
        return dupes, ignores
    except IOError:
        return RecordedDupes(
            author_dupes=defaultdict(set), book_dupes=defaultdict(set)
        ), RecordedIgnores(
            ignored_author_dupes=defaultdict(set), ignored_book_dupes=defaultdict(set)
        )


def get_bingo_dataframe(bingo_data_filepath: Path) -> pandas.DataFrame:
    """Create a Pandas DataFrame of the bingo data, indexed on card number"""

    bingo_data = pandas.read_csv(bingo_data_filepath)
    bingo_data.set_index("CARD", inplace=True)

    # Just looping through everywhere, minimal performance implications?
    return bingo_data.replace({np.nan: None})
