from collections import Counter
from typing import (
    Iterable,
    TypeVar,
)

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
