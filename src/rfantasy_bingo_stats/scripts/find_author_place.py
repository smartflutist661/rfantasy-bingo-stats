"""
Created on Apr 25, 2023

@author: fred
"""

import argparse
import json
from datetime import date

import numpy as np

from rfantasy_bingo_stats.constants import YearlyDataPaths
from rfantasy_bingo_stats.scripts.utils import calc_percentiles
from rfantasy_bingo_stats.types.bingo_statistics import BingoStatistics
from rfantasy_bingo_stats.types.defined_types import Author


def main(args: argparse.Namespace) -> None:
    with YearlyDataPaths(args.year).output_stats.open("r", encoding="utf8") as stats_file:
        bingo_stats = BingoStatistics.from_data(json.load(stats_file))

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


def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("author", type=Author)
    parser.add_argument("--year", type=int, default=date.today().year - 1)

    return parser.parse_args()


if __name__ == "__main__":
    main(cli())
