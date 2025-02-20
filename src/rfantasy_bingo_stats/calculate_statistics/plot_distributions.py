import json
from collections import Counter
from pathlib import Path
from types import MappingProxyType as MAP
from typing import (
    Any,
    Optional,
    SupportsFloat,
)

import matplotlib.pyplot as plt
import numpy as np
from lmfit.model import ModelResult  # type: ignore[import-untyped]

from rfantasy_bingo_stats.constants import (
    YOY_DATA_FILEPATH,
    YearlyDataPaths,
)
from rfantasy_bingo_stats.models.bingo_statistics import BingoStatistics
from rfantasy_bingo_stats.models.fit_props import FitProps
from rfantasy_bingo_stats.models.yearly_stats import YearlyBingoStatistics


def none_divide(num: Optional[SupportsFloat], denom: Optional[SupportsFloat]) -> Optional[float]:
    if num is None or denom is None:
        return None
    return float(num) / float(denom)


def none_subtract(lhs: Optional[SupportsFloat], rhs: Optional[SupportsFloat]) -> Optional[float]:
    if lhs is None or rhs is None:
        return None
    return float(lhs) - float(rhs)


def none_multiply(lhs: Optional[SupportsFloat], rhs: Optional[SupportsFloat]) -> Optional[float]:
    if lhs is None or rhs is None:
        return None
    return float(lhs) * float(rhs)


def create_yoy_plots(output_root: Path, show_plots: bool) -> None:
    """Plot distributions of interest"""

    output_root.mkdir(exist_ok=True)

    plt.style.use("fivethirtyeight")

    with YOY_DATA_FILEPATH.open("r", encoding="utf8") as yoy_file:
        yoy_data = MAP(
            {
                int(key): YearlyBingoStatistics.from_data(val)
                for key, val in json.load(yoy_file).items()
            }
        )

    years = []
    total_participant_counts = []
    total_card_counts = []
    total_story_counts = []
    hard_mode_square_counts = []
    hard_mode_card_counts = []
    hero_mode_card_counts = []
    misspelling_counts = []
    participants_vs_cards = []
    squares_vs_cards = []
    total_vs_unique_stories = []
    total_vs_unique_authors = []
    hard_mode_square_per_noncard_counts = []
    hard_mode_square_per_card_counts = []
    for year, stats in yoy_data.items():
        stats_path = YearlyDataPaths(year).output_stats
        if stats_path.exists():
            with stats_path.open("r", encoding="utf8") as stats_file:
                bingo_stats = BingoStatistics.from_data(json.load(stats_file))
                books_read_more_than_once = Counter(
                    {
                        book: read_count
                        for book, read_count in bingo_stats.overall_uniques.unique_books.items()
                        if read_count > 1
                    }
                )
                total_books_read_more_than_once = books_read_more_than_once.total()
        else:
            total_books_read_more_than_once = None

        years.append(year)
        total_participant_counts.append(stats.total_participant_count)
        total_card_counts.append(stats.total_card_count)
        total_story_counts.append(stats.total_story_count)

        hard_mode_square_counts.append(
            none_divide(stats.hard_mode_squares, stats.total_square_count)
        )
        hard_mode_card_counts.append(none_divide(stats.hard_mode_cards, stats.total_card_count))
        hard_mode_square_per_noncard_counts.append(
            none_divide(
                none_subtract(stats.hard_mode_squares, none_multiply(stats.hard_mode_cards, 25)),
                none_subtract(stats.total_card_count, stats.hard_mode_cards),
            )
        )
        hard_mode_square_per_card_counts.append(
            none_divide(stats.hard_mode_squares, stats.total_card_count)
        )
        hero_mode_card_counts.append(none_divide(stats.hero_mode_cards, stats.total_card_count))
        misspelling_counts.append(
            none_divide(stats.total_misspellings, total_books_read_more_than_once)
        )
        participants_vs_cards.append(stats.total_card_count / stats.total_participant_count)
        squares_vs_cards.append(none_divide(stats.total_square_count, stats.total_card_count))
        total_vs_unique_stories.append(
            none_divide(stats.unique_story_count, stats.total_story_count)
        )
        total_vs_unique_authors.append(
            none_divide(stats.unique_author_count, stats.total_author_count)
        )

    plt.figure(figsize=(16, 9))
    plt.suptitle(
        "COVID-19 was good for Bingo",
        fontsize=26,
        weight="bold",
        alpha=0.75,
        wrap=True,
    )
    plt.title(
        "Total participants over time",
        fontsize=19,
        alpha=0.85,
        wrap=True,
    )
    plt.plot(years, total_participant_counts)
    plt.xlim(min(years), None)
    plt.savefig(output_root / "participants_change.png")

    plt.figure(figsize=(16, 9))
    plt.suptitle(
        "Misspellings improve slightly",
        fontsize=26,
        weight="bold",
        alpha=0.75,
        wrap=True,
    )
    plt.title(
        "Misspellings compared to the number of books read more than once",
        fontsize=19,
        alpha=0.85,
        wrap=True,
    )
    plt.plot(years, misspelling_counts)  # type: ignore[arg-type]
    plt.xlim(min(years), None)
    plt.savefig(output_root / "misspellings_change.png")

    plt.figure(figsize=(16, 9))
    plt.suptitle(
        "Hard mode squares are the majority, cards not so much",
        fontsize=26,
        weight="bold",
        alpha=0.75,
        wrap=True,
    )
    plt.title(
        "Hard mode cards and squares compared to the total number of cards and squares",
        fontsize=19,
        alpha=0.85,
        wrap=True,
    )
    plt.plot(years, hard_mode_square_counts, label="Squares")  # type: ignore[arg-type]
    plt.plot(years, hard_mode_card_counts, label="Cards")  # type: ignore[arg-type]
    plt.legend()
    plt.ylim(-0.01, None)
    plt.xlim(min(years), None)
    plt.savefig(output_root / "hard_mode_change.png")

    plt.figure(figsize=(16, 9))
    plt.suptitle(
        "Is hard mode getting easier?",
        fontsize=26,
        weight="bold",
        alpha=0.75,
        wrap=True,
    )
    plt.title(
        "Hard mode squares per non-HM card",
        fontsize=19,
        alpha=0.85,
        wrap=True,
    )
    plt.plot(years, hard_mode_square_per_noncard_counts)  # type: ignore[arg-type]
    plt.xlim(min(years), None)
    plt.savefig(output_root / "hard_mode_noncard_change.png")

    plt.figure(figsize=(16, 9))
    plt.suptitle(
        "More people are reviewing what they read",
        fontsize=26,
        weight="bold",
        alpha=0.75,
        wrap=True,
    )
    plt.title(
        "Hero mode cards compared to the total number of cards",
        fontsize=19,
        alpha=0.85,
        wrap=True,
    )
    plt.plot(years, hero_mode_card_counts)  # type: ignore[arg-type]
    plt.xlim(min(years), None)
    plt.savefig(output_root / "hero_mode_change.png")

    plt.figure(figsize=(16, 9))
    plt.suptitle(
        "More people do multiple cards",
        fontsize=26,
        weight="bold",
        alpha=0.75,
        wrap=True,
    )
    plt.title(
        "Cards per participant over time",
        fontsize=19,
        alpha=0.85,
        wrap=True,
    )
    plt.plot(years, participants_vs_cards)
    plt.xlim(min(years), None)
    plt.savefig(output_root / "multi_card_change.png")

    plt.figure(figsize=(16, 9))
    plt.suptitle(
        "Blackout has been common since the beginning",
        fontsize=26,
        weight="bold",
        alpha=0.75,
        wrap=True,
    )
    plt.title(
        "Squares per card over time",
        fontsize=19,
        alpha=0.85,
        wrap=True,
    )
    plt.plot(years, squares_vs_cards)  # type: ignore[arg-type]
    plt.xlim(min(years), None)
    plt.savefig(output_root / "complete_squares_change.png")

    plt.figure(figsize=(16, 9))
    plt.suptitle(
        "Uniqueness has decreased",
        fontsize=26,
        weight="bold",
        alpha=0.75,
        wrap=True,
    )
    plt.title(
        "Unique vs total stories and authors over time",
        fontsize=19,
        alpha=0.85,
        wrap=True,
    )
    plt.plot(years, total_vs_unique_stories, label="Stories")  # type: ignore[arg-type]
    plt.plot(years, total_vs_unique_authors, label="Authors")  # type: ignore[arg-type]
    plt.legend()
    plt.xlim(min(years), None)
    plt.savefig(output_root / "uniques_change.png")

    if show_plots:
        plt.show()


def create_yearly_plots(bingo_stats: BingoStatistics, output_root: Path, show_plots: bool) -> None:
    """Plot distributions of interest"""

    output_root.mkdir(exist_ok=True)

    plt.style.use("fivethirtyeight")

    plot_card_hist(
        counter=bingo_stats.card_uniques,
        title="Most people read a couple of unique books",
        subtitle="Number of cards with each count of unique books read",
        filepath=output_root / "per_card_uniques.png",
    )

    plot_card_hist(
        counter=bingo_stats.incomplete_cards,
        title="Read more than three rows, probably read a whole card",
        subtitle="Number of cards with each count of incomplete squares",
        filepath=output_root / "per_card_incompletes.png",
    )

    plot_card_hist(
        counter=bingo_stats.hard_mode_by_card,
        title="Law of Large Numbers with a goal",
        subtitle="Number of cards with a particular count of hard mode squares",
        filepath=output_root / "per_card_hms.png",
    )

    plot_card_hist(
        counter=bingo_stats.normal_bingo_type_stats.complete_bingos_by_card,
        title="Non-blackout cards get surprisingly few bingos",
        subtitle="Number of cards with a particular count of bingos",
        filepath=output_root / "per_card_bingos.png",
    )

    plot_card_hist(
        counter=bingo_stats.hardmode_bingo_type_stats.complete_bingos_by_card,
        title="Cards that don't do all hard-mode don't pay attention to it at all",
        subtitle="Number of cards with a particular count of hard mode bingos",
        filepath=output_root / "per_card_hm_bingos.png",
    )

    plot_count_hist(
        counter=bingo_stats.overall_uniques.unique_authors,
        title="Most authors were only read once",
        subtitle="Number of reads per author, in 10-read bins",
        filepath=output_root / "per_author_reads.png",
    )

    plot_count_hist(
        counter=bingo_stats.overall_uniques.unique_books,
        title="Most books were only read once",
        subtitle="Number of reads per book, in 10-read bins",
        filepath=output_root / "per_book_reads.png",
    )

    if show_plots:
        plt.show()
    plt.close("all")


# I feel like it should be possible to fit these pre-histogram
def plot_card_hist(
    counter: Counter[Any],
    title: str,
    subtitle: str,
    filepath: Path,
) -> None:
    """Plot histogram of unique values"""

    plt.figure(figsize=(16, 9))

    max_val = 26

    bin_vals = np.arange(max_val + 1)

    edges = bin_vals - 0.5

    plt.hist(counter.values(), bins=edges)  # type: ignore[arg-type]

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

    plt.savefig(filepath)


def plot_count_hist(
    counter: Counter[Any],
    title: str,
    subtitle: str,
    filepath: Path,
) -> None:
    """Plot histogram of unique values"""

    edges = np.arange(0, counter.most_common(1)[0][1] + 10, 10)
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

    plt.savefig(filepath)


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
