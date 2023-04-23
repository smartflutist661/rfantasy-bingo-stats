"""
Created on Apr 22, 2023

@author: fred
"""
from collections import Counter
from typing import Any

import matplotlib.pyplot as plt  # type: ignore
import numpy as np
from lmfit.model import ModelResult  # type: ignore

from ..data.current import OUTPUT_IMAGE_ROOT
from ..types.bingo_statistics import BingoStatistics
from ..types.fit_props import FitProps

# from lmfit.models import SkewedGaussianModel  # type: ignore


def create_all_plots(bingo_stats: BingoStatistics, show_plots: bool) -> None:
    """Plot distributions of interest"""

    plt.style.use("fivethirtyeight")

    plot_card_hist(
        counter=bingo_stats.card_uniques,
        title="Unique Books per Card",
        x_label="Number of Unique Books",
        y_label="Number of Cards",
        filename="per_card_uniques.png",
    )

    plot_card_hist(
        counter=bingo_stats.incomplete_cards,
        title="Incomplete Squares per Card",
        x_label="Number of Incomplete Squares",
        y_label="Number of Cards",
        filename="per_card_incompletes.png",
    )

    plot_card_hist(
        counter=bingo_stats.hard_mode_by_card,
        title="Hard Mode Squares per Card",
        x_label="Number of Hard Mode Squares",
        y_label="Number of Cards",
        filename="per_card_hms.png",
    )

    plot_count_hist(
        bingo_stats.overall_uniques.unique_authors,
        "Reads per Unique Author",
        "Number of Reads",
        "Number of Authors",
        "per_author_reads.png",
    )

    plot_count_hist(
        bingo_stats.overall_uniques.unique_books,
        "Reads per Unique Book",
        "Number of Reads",
        "Number of Authors",
        "per_book_reads.png",
    )

    if show_plots:
        plt.show()


# I feel like it should be possible to fit these pre-histogram
def plot_card_hist(
    counter: Counter[Any],
    title: str,
    x_label: str,
    y_label: str,
    filename: str,
) -> None:
    """Plot histogram of unique values"""

    plt.figure(figsize=(19, 12))

    max_val = 26

    bin_vals = np.arange(max_val + 1)

    edges = bin_vals - 0.5

    plt.hist(counter.values(), bins=edges)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xticks(range(max_val))
    plt.xlim([edges[0], edges[-1]])

    # model = SkewedGaussianModel()
    # params = model.make_params(amplitude=len(counter), center=3, sigma=2, gamma=1)
    # hist, _ = np.histogram(list(counter.values()), bins=edges)
    # result = model.fit(hist, params, x=bin_vals[:-1])
    #
    # smoothed_x = np.arange(-1, 26, 0.01)
    # smoothed_y = result.model.func(smoothed_x, **result.best_values)
    # plt.plot(smoothed_x, smoothed_y)

    plt.savefig(OUTPUT_IMAGE_ROOT / filename)


def plot_count_hist(
    counter: Counter[Any],
    title: str,
    x_label: str,
    y_label: str,
    filename: str,
) -> None:
    """Plot histogram of unique values"""

    edges = np.arange(0, counter.most_common(1)[0][1], 10)
    hist, _ = np.histogram(list(counter.values()), bins=edges)

    fig, (axis1, axis2) = plt.subplots(2, 1, sharex=True, figsize=(19, 12))

    # Labels for entire figure
    fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor="none", top=False, bottom=False, left=False, right=False)
    plt.grid(False)
    plt.xlabel(x_label, labelpad=0.1)
    plt.ylabel(y_label)
    plt.gca().yaxis.set_label_coords(-0.05, 0.5)
    fig.suptitle(title)

    # Plot on multiple axes, hide overlapping elements
    axis1.hist(counter.values(), bins=edges)
    axis2.hist(counter.values(), bins=edges)

    axis1.set_ylim(hist[1] - 0.2 * hist[1], None)
    axis2.set_ylim(0, hist[2] + 0.2 * hist[2])
    axis1.set_yticks(np.arange(hist[1], hist[0] + 350, 350))

    axis1.spines["bottom"].set_visible(False)
    axis2.spines["top"].set_visible(False)
    axis1.xaxis.tick_top()
    axis1.tick_params(labeltop=False)
    axis2.xaxis.tick_bottom()

    # Add break marks
    diag_size = 0.01

    kwargs = {"transform": axis1.transAxes, "color": "k", "clip_on": False}
    axis1.plot((-diag_size, +diag_size), (-diag_size, +diag_size), **kwargs)
    axis1.plot((1 - diag_size, 1 + diag_size), (-diag_size, +diag_size), **kwargs)

    kwargs.update({"transform": axis2.transAxes})
    axis2.plot((-diag_size, +diag_size), (1 - diag_size, 1 + diag_size), **kwargs)
    axis2.plot((1 - diag_size, 1 + diag_size), (1 - diag_size, 1 + diag_size), **kwargs)

    plt.savefig(OUTPUT_IMAGE_ROOT / filename)


def get_fit_props(result: ModelResult) -> FitProps:
    """Get properties of a model fit"""
    best_vals = result.best_values
    cent = best_vals["center"]
    sig = best_vals["sigma"]
    gam = best_vals["gamma"]

    delt = gam * np.sqrt(1 / (1 + gam**2))

    mean = cent + np.sqrt(2 / np.pi) * sig * delt

    var = sig**2 * (1 - 2 * delt**2 / np.pi)

    skew = (2 - np.pi / 2) * (
        ((delt * np.sqrt(2 / np.pi)) ** 3) / (1 - 2 * delt**2 / np.pi) ** (3 / 2)
    )

    return FitProps(mean=mean, var=var, skew=skew)
