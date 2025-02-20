from pathlib import Path

from pytest import fixture

from rfantasy_bingo_stats.constants import YearlyDataPaths
from rfantasy_bingo_stats.models.author_info import (
    AuthorInfoAdapter,
)
from rfantasy_bingo_stats.models.card_data import CardData
from rfantasy_bingo_stats.models.recorded_ignores import RecordedIgnores
from rfantasy_bingo_stats.models.recorded_states import RecordedDupes
from rfantasy_bingo_stats.models.yearly_stats import (
    YearStatsAdapter,
)

TEST_DATA_FOLDER = Path(__file__).parent / "test_data"
DUPE_TEST_FILEPATH = TEST_DATA_FOLDER / "resolved_duplicates.json"
IGNORED_TEST_FILEPATH = TEST_DATA_FOLDER / "ignored_duplicates.json"
YOY_TEST_FILEPATH = TEST_DATA_FOLDER / "year_over_year_stats.json"
AUTHOR_TEST_FILEPATH = TEST_DATA_FOLDER / "author_records.json"


@fixture(name="data_paths")
def get_data_paths() -> YearlyDataPaths:
    return YearlyDataPaths(2023)


def test_card_data_deser(data_paths: YearlyDataPaths) -> None:
    with data_paths.card_info.open("r", encoding="utf8") as card_data_file:
        CardData.model_validate_json(card_data_file.read())


def test_dupe_serde() -> None:
    with DUPE_TEST_FILEPATH.open("r", encoding="utf8") as dupe_file:
        orig = dupe_file.read()
    validated = RecordedDupes.model_validate_json(orig)
    dump = validated.model_dump_json(indent=2)
    assert orig == dump


def test_ignore_serde() -> None:
    with IGNORED_TEST_FILEPATH.open("r", encoding="utf8") as ignore_file:
        orig = ignore_file.read()
    validated = RecordedIgnores.model_validate_json(orig)
    dump = validated.model_dump_json(indent=2)
    assert orig == dump


def test_yoy_deser() -> None:
    with YOY_TEST_FILEPATH.open("r", encoding="utf8") as yoy_file:
        YearStatsAdapter.validate_json(yoy_file.read())


def test_author_data_serde() -> None:
    with AUTHOR_TEST_FILEPATH.open("r", encoding="utf8") as author_info_file:
        orig = author_info_file.read()
    validated = AuthorInfoAdapter.validate_json(orig)
    dump = AuthorInfoAdapter.dump_json(validated, indent=2).decode("utf8")
    assert orig == dump
