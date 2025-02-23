from collections.abc import Mapping

from rfantasy_bingo_stats.calculate_statistics.get_bingo_cards import (
    get_bingo_cards,
    get_bingo_stats,
)
from rfantasy_bingo_stats.calculate_statistics.get_stats import create_markdown
from rfantasy_bingo_stats.calculate_statistics.plot_distributions import (
    create_yearly_plots,
    create_yoy_plots,
)
from rfantasy_bingo_stats.cli import (
    Args,
    BingoArgs,
)
from rfantasy_bingo_stats.constants import BingoYearDataPaths
from rfantasy_bingo_stats.data_operations.get_data import (
    get_bingo_dataframe,
    get_existing_states,
    get_unique_bingo_authors,
    get_unique_bingo_books,
)
from rfantasy_bingo_stats.data_operations.update_data import (
    update_bingo_authors,
    update_bingo_books,
)
from rfantasy_bingo_stats.logger import LOGGER
from rfantasy_bingo_stats.match_books.get_matches import update_dedupes_from_authors
from rfantasy_bingo_stats.models.author_info import AuthorInfo
from rfantasy_bingo_stats.models.bingo_card import BingoCard
from rfantasy_bingo_stats.models.card_data import CardData
from rfantasy_bingo_stats.models.defined_types import (
    Author,
    CardID,
)
from rfantasy_bingo_stats.models.recorded_states import RecordedDupes
from rfantasy_bingo_stats.normalization import (
    normalize_authors,
    normalize_books,
    update_author_info_map,
)


def collect_statistics(
    cards: Mapping[CardID, BingoCard],
    recorded_states: RecordedDupes,
    yearly_paths: BingoYearDataPaths,
    card_data: CardData,
    author_data: Mapping[Author, AuthorInfo],
    show_plots: bool,
) -> None:
    """Collect statistics on normalized books and create a rough draft post"""

    bingo_stats = get_bingo_stats(cards, recorded_states, card_data, author_data)

    with yearly_paths.output_stats.open("w", encoding="utf8") as stats_file:
        stats_file.write(bingo_stats.model_dump_json(indent=2))

    create_markdown(bingo_stats, card_data, yearly_paths.output_md)

    create_yearly_plots(bingo_stats, yearly_paths.output_image_root, show_plots)

    create_yoy_plots(yearly_paths.output_image_root, show_plots)


def bingo_main(args: Args, bingo_args: BingoArgs) -> None:
    data_paths = BingoYearDataPaths(bingo_args.year)

    with data_paths.card_info.open("r", encoding="utf8") as card_data_file:
        card_data = CardData.model_validate_json(card_data_file.read())

    bingo_data = get_bingo_dataframe(data_paths.raw_data)

    LOGGER.info("Loading data.")
    recorded_duplicates, recorded_ignores = get_existing_states()

    if args.skip_updates is False:
        unique_authors = get_unique_bingo_authors(bingo_data, card_data)
        normalize_authors(
            unique_authors,
            args.match_score,
            args.rescan_keys,
            recorded_duplicates,
            recorded_ignores,
            args.skip_authors,
        )
        LOGGER.info("Updating Bingo authors.")
        updated_data, author_dedupes = update_bingo_authors(
            bingo_data.copy(deep=True),
            recorded_duplicates.author_dupes,
            card_data.all_title_author_hm_columns,
            data_paths.output_df,
        )
        LOGGER.info("Bingo authors updated.")

        LOGGER.info("Collecting author-based misspellings.")
        update_dedupes_from_authors(recorded_duplicates, author_dedupes)
        unique_books = get_unique_bingo_books(updated_data, card_data)
        normalize_books(
            unique_books,
            args.match_score,
            args.rescan_keys,
            recorded_duplicates,
            recorded_ignores,
        )

        LOGGER.info("Updating Bingo books.")
        update_bingo_books(
            updated_data,
            recorded_duplicates.book_dupes,
            card_data.all_title_author_hm_columns,
            data_paths.output_df,
        )
        LOGGER.info("Bingo books updated.")

    author_data = update_author_info_map(recorded_duplicates)
    LOGGER.info("Wrote corrected author info.")

    LOGGER.info("Collecting corrected bingo cards.")
    cards = get_bingo_cards(bingo_data, card_data)
    LOGGER.info("Collecting statistics.")
    collect_statistics(
        cards,
        recorded_duplicates,
        data_paths,
        card_data,
        author_data,
        bingo_args.show_plots,
    )
