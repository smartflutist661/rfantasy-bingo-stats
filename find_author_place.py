"""
Created on Apr 25, 2023

@author: fred
"""
import argparse
import json
from collections import Counter
from typing import (
    Iterable,
    TypeVar,
)

import numpy as np

from process_data.types.bingo_statistics import BingoStatistics
from process_data.types.defined_types import Author
from process_data.constants import YearlyDataPaths
from datetime import date

T = TypeVar("T")


def calc_percentiles(
    cnts_dict: Counter[T],
    percentiles_to_calc: Iterable[float] = range(101),
) -> list[tuple[float, T]]:
    """Returns [(percentile, value)] with nearest rank percentiles.
    Percentile 0: <min_value>, 100: <max_value>.
    cnts_dict: { <value>: <count> }
    percentiles_to_calc: iterable for percentiles to calculate; 0 <= ~ <= 100
    """
    assert all(0 <= percentile <= 100 for percentile in percentiles_to_calc)
    percentiles = []
    num = sum(cnts_dict.values())
    cnts = sorted(cnts_dict.items(), key=lambda x: -x[1])
    curr_cnts_pos = 0  # current position in cnts
    curr_pos = cnts[0][1]  # sum of freqs up to current_cnts_pos
    for percentile in sorted(percentiles_to_calc):
        if percentile < 100:
            percentile_pos = percentile / 100.0 * num
            while curr_pos <= percentile_pos and curr_cnts_pos < len(cnts):
                curr_cnts_pos += 1
                curr_pos += cnts[curr_cnts_pos][1]
            percentiles.append((percentile, cnts[curr_cnts_pos][0]))
        else:
            percentiles.append((percentile, cnts[-1][0]))  # we could add a small value
    return percentiles


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
            print(
                f" \t -----> {author}: Place {place} | Read count {count} |"
                + f" Percentile by count {percentiles[author]:.1f} | Percentile by total place {100*total_place/len(bingo_stats.overall_uniques.unique_authors):.1f} <-----"
            )
        else:
            print(
                f"{author}: Place {place} | Read count {count} |"
                + f" Percentile {percentiles[author]:.1f} | Percentile by total place {100*total_place/len(bingo_stats.overall_uniques.unique_authors):.1f}"
            )


def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("author", type=Author)
    parser.add_argument("--year", type=int, default=date.today().year)

    return parser.parse_args()


if __name__ == "__main__":
    main(cli())
