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
        title="Most people read a couple of unique books",
        subtitle="Number of cards with each count of unique books read",
        filename="per_card_uniques.png",
    )

    plot_card_hist(
        counter=bingo_stats.incomplete_cards,
        title="Read over three rows, probably read a whole card",
        subtitle="Number of cards with each count of incomplete squares",
        filename="per_card_incompletes.png",
    )

    plot_card_hist(
        counter=bingo_stats.hard_mode_by_card,
        title="Law of Large Numbers with a goal",
        subtitle="Number of cards with a particular count of hard mode squares",
        filename="per_card_hms.png",
    )

    plot_count_hist(
        counter=bingo_stats.overall_uniques.unique_authors,
        title="Most authors were only read once",
        subtitle="Number of reads per author, in 10-read bins",
        filename="per_author_reads.png",
    )

    plot_count_hist(
        counter=bingo_stats.overall_uniques.unique_books,
        title="Most books were only read once",
        subtitle="Number of reads per book, in 10-read bins",
        filename="per_book_reads.png",
    )

    if show_plots:
        plt.show()


# I feel like it should be possible to fit these pre-histogram
def plot_card_hist(
    counter: Counter[Any],
    title: str,
    subtitle: str,
    filename: str,
) -> None:
    """Plot histogram of unique values"""

    plt.figure(figsize=(16, 9))

    max_val = 26

    bin_vals = np.arange(max_val + 1)

    edges = bin_vals - 0.5

    plt.hist(counter.values(), bins=edges)

    plt.suptitle(title, fontsize=26, weight="bold", alpha=0.75, wrap=True)
    plt.title(subtitle, fontsize=19, alpha=0.85, wrap=True)
    plt.xticks(range(max_val))
    plt.xlim(-1, max_val)
    ymax = plt.gca().get_ylim()[1]
    plt.ylim(-0.01 * ymax, None)
    plt.tick_params(labelsize=18)
    plt.axhline(y=0, color="black", linewidth=1.3, alpha=0.7)
    plt.axvline(x=-0.75, color="black", linewidth=1.3, alpha=0.3)

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
    subtitle: str,
    filename: str,
) -> None:
    """Plot histogram of unique values"""

    edges = np.arange(0, counter.most_common(1)[0][1], 10)
    hist, _ = np.histogram(list(counter.values()), bins=edges)

    fig, (axis1, axis2) = plt.subplots(2, 1, sharex=True, figsize=(16, 9))

    plt.tick_params(labelsize=18)
    plt.axhline(y=0, color="black", linewidth=1.3, alpha=0.7)

    # Labels for entire figure
    fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor="none", top=False, bottom=False, left=False, right=False)
    plt.grid(False)
    plt.gca().yaxis.set_label_coords(-0.05, 0.5)
    plt.suptitle(title, fontsize=26, weight="bold", alpha=0.75, wrap=True)
    plt.title(subtitle, fontsize=19, alpha=0.85, wrap=True)

    # Plot on multiple axes, hide overlapping elements
    axis1.hist(counter.values(), bins=edges)
    axis2.hist(counter.values(), bins=edges)

    axis1.set_ylim(hist[1] - 0.2 * hist[1], None)
    axis2.set_ylim(-0.02 * 1.5 * hist[2], 1.2 * hist[2])
    tick_spacing = (hist[0] - hist[1]) / 10
    axis1.set_yticks(np.arange(hist[1], hist[0] + tick_spacing, tick_spacing))

    xmax = axis1.get_xlim()[1]
    axis1.set_xlim(-0.025 * xmax, None)

    xmin = axis1.get_xlim()[0]
    axis1.axvline(x=0.70 * xmin, color="black", linewidth=1.3, alpha=0.3)
    axis2.axvline(x=0.70 * xmin, color="black", linewidth=1.3, alpha=0.3)

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
