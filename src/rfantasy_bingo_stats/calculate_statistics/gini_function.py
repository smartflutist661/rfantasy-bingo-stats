import numpy as np
from numpy.typing import ArrayLike


def calculate_gini_index(values: ArrayLike) -> float:
    """Calculate the Gini coefficient of a numpy array."""
    array = np.array(values)

    # Values must be sorted:
    array = np.sort(array)

    # Index per array element:
    index_array = np.arange(1, array.shape[0] + 1)

    # Number of array elements:
    array_len = array.shape[0]

    # Total of index-weighted values
    num = np.sum((2 * index_array - array_len - 1) * array)

    # Normalize by length and total value
    denom = array_len * np.sum(array)

    # Gini coefficient:
    return float(num / denom)
