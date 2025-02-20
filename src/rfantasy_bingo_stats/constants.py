from dataclasses import dataclass
from datetime import date
from pathlib import Path

CURRENT_YEAR = date.today().year - 1

REMOTE_REPO = "smartflutist661/rfantasy-bingo-stats"
TITLE_AUTHOR_SEPARATOR = " /// "
SUBBED_SQUARE_SEPARATOR = " /// "

# Global paths
ROOT = Path(__file__).parent
BINGO_DATA_PATH = ROOT / "bingo_data"
DUPE_RECORD_FILEPATH: Path = BINGO_DATA_PATH / "resolved_duplicates.json"
IGNORED_RECORD_FILEPATH: Path = BINGO_DATA_PATH / "ignored_duplicates.json"
AUTHOR_INFO_FILEPATH: Path = BINGO_DATA_PATH / "author_records.json"
YOY_DATA_FILEPATH: Path = BINGO_DATA_PATH / "year_over_year_stats.json"


@dataclass(frozen=True)
class YearlyDataPaths:
    year: int

    @property
    def root(self) -> Path:
        return BINGO_DATA_PATH / f"bingo_{self.year}"

    @property
    def raw_data_path(self) -> Path:
        return self.root / "raw_bingo_data.csv"

    @property
    def output_image_root(self) -> Path:
        return self.root / "plots"

    @property
    def output_df(self) -> Path:
        return self.root / "updated_bingo_data.csv"

    @property
    def output_md(self) -> Path:
        return self.root / "bingo_stats_rough_draft.md"

    @property
    def output_stats(self) -> Path:
        return self.root / "bingo_stats.json"

    @property
    def card_info(self) -> Path:
        return self.root / "card_data.json"
