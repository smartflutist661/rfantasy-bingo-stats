from dataclasses import dataclass


@dataclass(frozen=True)
class FitProps:
    """Properties of a skewed Gaussian fit"""

    mean: float
    var: float
    skew: float
