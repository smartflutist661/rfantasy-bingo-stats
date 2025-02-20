import argparse
from datetime import date

from rfantasy_bingo_stats.calculate_statistics.get_bingo_cards import get_bingo_cards
from rfantasy_bingo_stats.calculate_statistics.get_stats import format_book
from rfantasy_bingo_stats.constants import (
    DUPE_RECORD_FILEPATH,
    IGNORED_RECORD_FILEPATH,
    YearlyDataPaths,
)
from rfantasy_bingo_stats.data_operations.author_title_book_operations import title_author_to_book
from rfantasy_bingo_stats.data_operations.get_data import (
    get_bingo_dataframe,
    get_existing_states,
)
from rfantasy_bingo_stats.models.bingo_statistics import BingoStatistics
from rfantasy_bingo_stats.models.card_data import CardData
from rfantasy_bingo_stats.models.defined_types import CardID


def main(args: argparse.Namespace) -> None:
    year_data_paths = YearlyDataPaths(args.year)
    with year_data_paths.output_stats.open("r", encoding="utf8") as stats_file:
        bingo_stats = BingoStatistics.model_validate_json(stats_file.read())

    with year_data_paths.card_info.open("r", encoding="utf8") as card_data_file:
        card_data = CardData.model_validate_json(card_data_file.read())

    recorded_duplicates, _ = get_existing_states(DUPE_RECORD_FILEPATH, IGNORED_RECORD_FILEPATH)

    bingo_data = get_bingo_dataframe(year_data_paths.raw_data_path)

    cards = get_bingo_cards(bingo_data, card_data)

    book_dedupe_map = recorded_duplicates.get_book_dedupe_map()

    card_to_process = cards[args.card_id]
    overall_uniques = []
    square_uniques = []
    nonuniques = []
    for square_name, square in card_to_process.squares.items():
        if square is not None:
            book = title_author_to_book((square.title, square.author))
            if book in book_dedupe_map.keys():
                book = book_dedupe_map[book]

            total_uses = bingo_stats.overall_uniques.unique_books[book]
            square_uses = bingo_stats.square_uniques[square_name].unique_books[book]
            if total_uses == 1:
                overall_uniques.append(f"- {format_book(book)}, for {square_name}")
            elif square_uses == 1:
                square_uniques.append(f"- {format_book(book)}, for {square_name}")
            else:
                nonuniques.append(
                    f"- {format_book(book)} was used {total_uses} times total, {square_uses} times for the {square_name} square"
                )

    formatted_overall_uniques = "\n".join(overall_uniques)
    formatted_square_uniques = "\n".join(square_uniques)
    formatted_nonuniques = "\n".join(nonuniques)

    print(  # noqa: T201
        f"""
Your card had {len(overall_uniques)} unique books:

{formatted_overall_uniques}

Additionally, you were the only one to read a particular book for {len(square_uniques)} squares:

{formatted_square_uniques}

For the remaining books:

{formatted_nonuniques}
"""
    )


def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("--card-id", type=CardID, default="1")
    parser.add_argument("--year", type=int, default=date.today().year - 1)

    return parser.parse_args()


if __name__ == "__main__":
    main(cli())
