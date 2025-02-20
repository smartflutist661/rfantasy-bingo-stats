import argparse
from datetime import date

import numpy as np

from rfantasy_bingo_stats.constants import YearlyDataPaths
from rfantasy_bingo_stats.models.bingo_statistics import BingoStatistics
from rfantasy_bingo_stats.models.defined_types import Author
from rfantasy_bingo_stats.scripts.utils import calc_percentiles


def main(args: argparse.Namespace) -> None:
    with YearlyDataPaths(args.year).output_stats.open("r", encoding="utf8") as stats_file:
        bingo_stats = BingoStatistics.model_validate_json(stats_file.read())

    percentiles = {
        author: percentile
        for percentile, author in calc_percentiles(
            bingo_stats.overall_uniques.unique_authors,
            np.arange(0, 100, 100 / (len(bingo_stats.overall_uniques.unique_authors) * 10)),
        )
    }

    place = 0
    last_count = -1
    for total_place, (author, count) in enumerate(
        bingo_stats.overall_uniques.unique_authors.most_common()
    ):
        if count != last_count:
            place += 1
            last_count = count

        if author == args.author:
            print(  # noqa: T201
                f" \t -----> {author}: Place {place} | Read count {count} |"
                + f" Percentile by count {percentiles[author]:.1f} | Percentile by total place {100*total_place/len(bingo_stats.overall_uniques.unique_authors):.1f} <-----"
            )
        else:
            print(  # noqa: T201
                f"{author}: Place {place} | Read count {count} |"
                + f" Percentile {percentiles[author]:.1f} | Percentile by total place {100*total_place/len(bingo_stats.overall_uniques.unique_authors):.1f}"
            )


def cli() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("author", type=Author)
    parser.add_argument("--year", type=int, default=date.today().year - 1)

    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    cli()
