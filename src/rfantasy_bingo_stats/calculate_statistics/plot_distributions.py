from collections import Counter
from collections.abc import Sequence
from copy import deepcopy
from dataclasses import dataclass
from typing import (
    Optional,
    SupportsFloat,
)

import numpy as np
import plotly.graph_objects
from plotly.graph_objects import Figure
from plotly.subplots import make_subplots

from rfantasy_bingo_stats.constants import (
    YOY_DATA_FILEPATH,
    BingoYearDataPaths,
)
from rfantasy_bingo_stats.models.bingo_statistics import BingoStatistics
from rfantasy_bingo_stats.models.defined_types import (
    Author,
    Book,
    CardID,
)
from rfantasy_bingo_stats.models.yearly_stats import YearStatsAdapter


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


@dataclass
class Plot:
    figure: Figure
    caption: str = "[placeholder_caption]"

    def to_html(self) -> str:
        return (
            self.figure.to_html(full_html=False, include_plotlyjs=False)
            + f'<p class="caption">{self.caption}</p>'
        )


@dataclass
class YOYPlots:
    participants: Plot
    misspellings: Plot
    hm_per_nonhm_card: Plot
    hero_mode: Plot
    cards_per_person: Plot
    squares_per_card: Plot
    hard_mode: Plot
    uniqueness: Plot


@dataclass
class YearlyPlots:
    uniques: Plot
    incompletes: Plot
    hard_mode: Plot
    bingos: Plot
    hm_bingos: Plot
    author_reads: Plot
    book_reads: Plot


@dataclass
class Plots:
    yoy_plots: YOYPlots
    yearly_plots: YearlyPlots


BASE_LAYOUT: dict = {  # type: ignore[type-arg]
    "title": {
        "text": "[Placeholder Title]",
        "x": 0.5,
        "xanchor": "center",
        "font": {
            "size": 26,
            "color": "rgba(0, 0, 0, 0.75)",
            "weight": "bold",
        },
        "subtitle": {
            "font": {
                "color": "rgba(0, 0, 0, 0.85)",
                "size": 20,
            },
        },
    },
    "xaxis": {
        "gridcolor": "#cbcbcb",
        "tickfont": {
            "size": 18,
        },
    },
    "yaxis": {
        "gridcolor": "#cbcbcb",
        "tickfont": {
            "size": 18,
        },
    },
    "paper_bgcolor": "#f0f0f0",
    "plot_bgcolor": "#f0f0f0",
}


def yoy_single_plot(
    title: str,
    years: Sequence[int],
    y_data: Sequence[int | float | None],
    hover_template: str,
    percentage: bool = False,
) -> Figure:
    if len(title) > 55:
        raise ValueError(f"Title too long: {title}")
    plot = plotly.graph_objects.Figure()
    plot.add_trace(
        plotly.graph_objects.Scatter(
            mode="lines",
            x=years,
            y=y_data,  # type: ignore[arg-type]
            hovertemplate=f"{hover_template}<extra></extra>",
            showlegend=False,
            line={"width": 4},
        ),
    )
    layout = deepcopy(BASE_LAYOUT)
    layout["title"]["subtitle"]["text"] = title
    layout["xaxis"]["range"] = [min(years), None]
    if percentage:
        layout["yaxis"]["tickformat"] = ".1%"
    plot.update_layout(layout)

    return plot


def yoy_double_plot(
    title: str,
    years: Sequence[int],
    y1_data: Sequence[int | float | None],
    y2_data: Sequence[int | float | None],
    y1_label: str,
    y2_label: str,
    hover_template: str,
    percentage: bool = False,
) -> Figure:
    if len(title) > 55:
        raise ValueError(f"Title too long: {title}")
    plot = plotly.graph_objects.Figure()
    plot.add_trace(
        plotly.graph_objects.Scatter(
            mode="lines",
            x=years,
            y=y1_data,  # type: ignore[arg-type]
            hovertemplate=f"{hover_template}<extra></extra>",
            name=y1_label,
            meta=y1_label.lower(),
            line={"width": 4},
        ),
    )
    plot.add_trace(
        plotly.graph_objects.Scatter(
            mode="lines",
            x=years,
            y=y2_data,  # type: ignore[arg-type]
            hovertemplate=f"{hover_template}<extra></extra>",
            name=y2_label,
            meta=y2_label.lower(),
            line={"width": 4},
        ),
    )
    layout = deepcopy(BASE_LAYOUT)
    layout["title"]["subtitle"]["text"] = title
    layout["xaxis"]["range"] = [min(years), None]
    if percentage:
        layout["yaxis"]["tickformat"] = ".1%"
    plot.update_layout(layout)

    return plot


def create_yoy_plots(current_year: int) -> YOYPlots:
    """Plot distributions of interest"""

    with YOY_DATA_FILEPATH.open("r", encoding="utf8") as yoy_file:
        yoy_data = YearStatsAdapter.validate_json(yoy_file.read())

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
        # Don't create plots for past years if data is from future
        if year > current_year:
            break
        stats_path = BingoYearDataPaths(year).output_stats
        if stats_path.exists():
            with stats_path.open("r", encoding="utf8") as stats_file:
                bingo_stats = BingoStatistics.model_validate_json(stats_file.read())
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

    participants = Plot(
        figure=yoy_single_plot(
            title="Total participants over time",
            years=years,
            y_data=total_participant_counts,
            hover_template="%{y} participants",
        ),
    )
    misspellings = Plot(
        figure=yoy_single_plot(
            "% of entries misspelled of books read more than once",
            years,
            misspelling_counts,
            "%{y} of entries misspelled",
            percentage=True,
        ),
    )
    hm_per_nonhm_card = Plot(
        figure=yoy_single_plot(
            "Hard mode squares per non-HM card",
            years,
            hard_mode_square_per_noncard_counts,
            "%{y:.2f} hard mode squares",
        ),
    )
    hero_mode = Plot(
        figure=yoy_single_plot(
            "Hero mode cards vs. total number",
            years,
            hero_mode_card_counts,
            "%{y} of cards hero mode",
            percentage=True,
        ),
    )
    cards_per_person = Plot(
        figure=yoy_single_plot(
            "Cards per participant over time",
            years,
            participants_vs_cards,
            "%{y:.3f} cards per person",
        ),
    )
    squares_per_card = Plot(
        figure=yoy_single_plot(
            "Squares per card over time",
            years,
            squares_vs_cards,
            "%{y:.2f} complete squares per card",
        ),
    )

    hard_mode = Plot(
        figure=yoy_double_plot(
            "% of squares & cards done in hard mode",
            years,
            hard_mode_square_counts,
            hard_mode_card_counts,
            y1_label="Squares",
            y2_label="Cards",
            hover_template="%{y} of %{meta} hard mode",
            percentage=True,
        ),
    )

    uniqueness = Plot(
        figure=yoy_double_plot(
            "Unique vs. total stories & authors over time",
            years,
            total_vs_unique_stories,
            total_vs_unique_authors,
            y1_label="Stories",
            y2_label="Authors",
            hover_template="%{y} of %{meta} unique",
            percentage=True,
        ),
    )

    return YOYPlots(
        participants=participants,
        misspellings=misspellings,
        hm_per_nonhm_card=hm_per_nonhm_card,
        hero_mode=hero_mode,
        cards_per_person=cards_per_person,
        squares_per_card=squares_per_card,
        hard_mode=hard_mode,
        uniqueness=uniqueness,
    )


def create_yearly_plots(bingo_stats: BingoStatistics) -> YearlyPlots:
    """Plot distributions of interest"""

    uniques = Plot(
        figure=plot_fixed_hist(
            counter=bingo_stats.card_uniques,
            title="# of cards with each count of unique books read",
            hover_template="%{y} cards with %{x} unique books",
            max_val=25,
        ),
    )

    incompletes = Plot(
        figure=plot_fixed_hist(
            counter=bingo_stats.incomplete_cards,
            title="# of cards with each count of incomplete squares",
            hover_template="%{y} cards with %{x} incomplete squares",
            max_val=25,
        ),
    )

    hard_mode = Plot(
        figure=plot_fixed_hist(
            counter=bingo_stats.hard_mode_by_card,
            title="# of cards with each count of hard mode squares",
            hover_template="%{y} cards with %{x} hard mode squares",
            max_val=25,
        ),
    )

    bingos = Plot(
        figure=plot_fixed_hist(
            counter=bingo_stats.normal_bingo_type_stats.complete_bingos_by_card,
            title="# of cards with each count of bingos",
            hover_template="%{y} cards with %{x} bingos",
            max_val=10,
        ),
    )

    hm_bingos = Plot(
        figure=plot_fixed_hist(
            counter=bingo_stats.hardmode_bingo_type_stats.complete_bingos_by_card,
            title="# of cards with each count of hard mode bingos",
            hover_template="%{y} cards with %{x} hard mode bingos",
            max_val=10,
        ),
    )

    author_reads = Plot(
        figure=plot_count_hist(
            counter=bingo_stats.overall_uniques.unique_authors,
            title="# of reads per author, in 10-read bins",
            hover_template="%{y} authors read %{x} times",
        ),
    )

    book_reads = Plot(
        figure=plot_count_hist(
            counter=bingo_stats.overall_uniques.unique_books,
            title="# of reads per book, in 10-read bins",
            hover_template="%{y} books read %{x} times",
        ),
    )

    return YearlyPlots(
        uniques=uniques,
        incompletes=incompletes,
        hard_mode=hard_mode,
        bingos=bingos,
        hm_bingos=hm_bingos,
        author_reads=author_reads,
        book_reads=book_reads,
    )


def plot_fixed_hist(
    counter: Counter[CardID],
    title: str,
    hover_template: str,
    max_val: int,
) -> Figure:
    """Plot histogram of unique values"""
    if len(title) > 55:
        raise ValueError(f"Title too long: {title}")

    plot = plotly.graph_objects.Figure()
    plot.add_trace(
        plotly.graph_objects.Histogram(
            x=list(counter.values()),
            xbins={"size": 1, "start": -0.5, "end": max_val + 0.5},
            hovertemplate=f"{hover_template}<extra></extra>",
        )
    )
    layout = deepcopy(BASE_LAYOUT)
    layout["title"]["subtitle"]["text"] = title
    layout["xaxis"]["range"] = [-1, max_val + 1]
    plot.update_layout(layout)

    return plot


def plot_count_hist(
    counter: Counter[Author] | Counter[Book],
    title: str,
    hover_template: str,
) -> Figure:
    """Plot histogram of unique values"""

    max_val = counter.most_common(1)[0][1] + 10
    edges = np.arange(0, max_val, 10)
    hist, _ = np.histogram(list(counter.values()), bins=edges)

    plot = make_subplots(rows=2, cols=1, vertical_spacing=0.05, shared_xaxes=True)
    trace = plotly.graph_objects.Histogram(
        x=list(counter.values()),
        xbins={"size": 10, "start": 0, "end": max_val},
        hovertemplate=f"{hover_template}<extra></extra>",
        marker={"color": "#636EFA"},
    )
    plot.append_trace(trace, row=1, col=1)
    plot.append_trace(trace, row=2, col=1)
    layout = deepcopy(BASE_LAYOUT)
    layout["title"]["subtitle"]["text"] = title
    layout["xaxis"]["range"] = [0, max_val]
    layout["showlegend"] = False
    layout["yaxis2"] = layout["yaxis"]
    layout["xaxis2"] = layout["xaxis"]
    plot.update_layout(layout)

    y_break_top = hist[1] - 0.2 * hist[1]
    y_break_bottom = 1.2 * hist[2]
    plot.update_yaxes(range=[y_break_top, None], row=1, col=1)
    plot.update_xaxes(visible=False, row=1, col=1)
    plot.update_yaxes(range=[0, y_break_bottom], row=2, col=1)

    plot.add_shape(
        type="line",
        xref="paper",
        yref="y domain",
        x0=-0.01,
        y0=-0.01,
        x1=0.01,
        y1=0.01,
        line={"color": "black", "width": 2},
    )
    plot.add_shape(
        type="line",
        xref="paper",
        yref="y2 domain",
        x0=-0.01,
        y0=0.99,
        x1=0.01,
        y1=1.01,
        line={"color": "black", "width": 2},
    )

    return plot
