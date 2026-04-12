""" """

# pylint: disable=line-too-long
from collections import Counter
from collections.abc import (
    Collection,
    Iterable,
    Sequence,
)
from pathlib import Path

import numpy as np

from rfantasy_bingo_stats.calculate_statistics.get_bingo_cards import (
    BINGO_SIZE,
    POSSIBLE_BINGOS,
)
from rfantasy_bingo_stats.calculate_statistics.gini_function import calculate_gini_index
from rfantasy_bingo_stats.calculate_statistics.plot_distributions import Plots
from rfantasy_bingo_stats.calculate_statistics.stats_format_utils import (
    SummaryStats,
    format_author_demo,
    format_book,
    format_bottom_square_counts,
    format_dedupe_counts,
    format_favorite_square,
    format_inline_bingo_ties,
    format_least_subbed_square,
    format_most_reads_per_square_books,
    format_most_square_authors,
    format_most_square_books,
    format_most_subbed_squares,
    format_top_author_counts,
    format_top_book_counts,
    format_top_list_with_ties,
    format_unique_author_books,
    get_single_ties,
    get_used_once,
)
from rfantasy_bingo_stats.constants import (
    REPO_ROOT,
)
from rfantasy_bingo_stats.logger import LOGGER
from rfantasy_bingo_stats.models.author_statistics import AuthorStatistics
from rfantasy_bingo_stats.models.bingo_statistics import BingoStatistics
from rfantasy_bingo_stats.models.bingo_type_statistics import BingoTypeStatistics
from rfantasy_bingo_stats.models.card_data import CardData
from rfantasy_bingo_stats.models.defined_types import (
    Author,
    Book,
    CardID,
    SquareName,
)
from rfantasy_bingo_stats.models.unique_statistics import UniqueStatistics


def format_square_stats(
    square_name: SquareName,
    bingo_stats: BingoStatistics,
) -> str:
    """Format stats for a single square"""
    square_uniques = bingo_stats.square_uniques[square_name]
    return f"""## Most Read Books

{format_top_book_counts(square_uniques.unique_books, 5)}

**TOTAL**: {square_uniques.unique_books.total()} books read, with {len(square_uniques.unique_books)} unique titles.
{bingo_stats.hard_mode_by_square[square_name]} books were claimed to qualify for hard mode.
{get_used_once(square_uniques.unique_books)} books were used only once for this square.
Skipped {bingo_stats.incomplete_squares[square_name]} times. Substituted {bingo_stats.subbed_out_squares[square_name]} times.

## Most Read Authors

{format_top_author_counts(square_uniques.unique_authors, 5)}

**TOTAL**: {square_uniques.unique_authors.total()} total authors read, with {len(square_uniques.unique_authors)} unique.
{get_used_once(square_uniques.unique_authors)} authors were used only once for this square.

### Author demographics

{format_author_statistics(bingo_stats.square_author_stats[square_name], bingo_stats.unique_square_author_stats[square_name])}
"""


def format_farragini(
    bingo_stats: BingoStatistics,
    square_names: Iterable[SquareName],
    top_n: int = 3,
) -> str:
    """Format a table of FarraGini indices"""
    table_strs: list[tuple[str, str, str]] = [
        ("SQUARE", "BOOK", "AUTHOR"),
        ("---------", ":---------:", ":---------:"),
    ]
    book_ginis = {}
    author_ginis = {}
    for square_name in square_names:
        book_gini = (
            calculate_gini_index(
                tuple(bingo_stats.square_uniques[square_name].unique_books.values())
            )
            * 100
        )
        author_gini = (
            calculate_gini_index(
                tuple(bingo_stats.square_uniques[square_name].unique_authors.values())
            )
            * 100
        )
        book_ginis[square_name] = book_gini
        author_ginis[square_name] = author_gini
        table_strs.append((square_name, f"{book_gini:.1f}", f"{author_gini:.1f}"))

    highest_book_ginis = sorted(book_ginis.items(), key=lambda item: item[1], reverse=True)
    highest_author_ginis = sorted(author_ginis.items(), key=lambda item: item[1], reverse=True)

    def formatter(cur_ties: Sequence[str], _: float) -> str:
        if len(cur_ties) == 1:
            return "- " + cur_ties[0]
        if len(cur_ties) > 1:
            return "- ***TIE***: " + " and ".join(cur_ties)
        raise ValueError("No results?")

    high_book_gini_strs = format_top_list_with_ties(highest_book_ginis, formatter, top_n)
    low_book_gini_strs = format_top_list_with_ties(reversed(highest_book_ginis), formatter, top_n)
    high_author_gini_strs = format_top_list_with_ties(highest_author_ginis, formatter, top_n)
    low_author_gini_strs = format_top_list_with_ties(
        reversed(highest_author_ginis), formatter, top_n
    )

    table_str = "\n".join("|" + "|".join(row) + "|" for row in table_strs)
    table_str += "\n{: .sortable}"
    low_book_gini_str = "The squares with the most variety in books:\n" + "\n".join(
        low_book_gini_strs
    )
    low_author_gini_str = "The squares with the most variety in authors:\n" + "\n".join(
        low_author_gini_strs
    )
    high_book_gini_str = "The squares with the least variety in books:\n" + "\n".join(
        high_book_gini_strs
    )
    high_author_gini_str = "The squares with the least variety in authors:\n" + "\n".join(
        high_author_gini_strs
    )
    return (
        table_str
        + "\n\n"
        + low_book_gini_str
        + "\n\n"
        + low_author_gini_str
        + "\n\n"
        + high_book_gini_str
        + "\n\n"
        + high_author_gini_str
    )


def format_square_table(
    bingo_stats: BingoStatistics,
    square_names: Iterable[SquareName],
) -> str:
    """Format a table of FarraGini indices"""
    table_strs: list[tuple[str, str, str]] = [
        ("SQUARE", "% COMPLETE", "% HARD MODE"),
        ("---------", ":---------:", ":---------:"),
    ]
    total_cards = bingo_stats.total_card_count
    for square_name in square_names:
        total_cards_with_square = total_cards - bingo_stats.subbed_out_squares[square_name]
        table_strs.append(
            (
                square_name,
                f"{100 - bingo_stats.incomplete_squares[square_name]/total_cards_with_square*100:.1f}",
                f"{bingo_stats.hard_mode_by_square[square_name]/total_cards_with_square*100:.1f}",
            )
        )
    return "\n".join("|" + "|".join(row) + "|" for row in table_strs)


def format_subbed_stats(bingo_stats: BingoStatistics) -> str:
    """Format stats on squares that were subbed for others"""

    subbed_in_squares = Counter(subbed_in for _, subbed_in in bingo_stats.subbed_squares.keys())

    subbed_in_books: Counter[Book] = Counter()
    subbed_in_authors: Counter[Author] = Counter()
    for square_name in subbed_in_squares:
        books = bingo_stats.square_uniques.get(square_name, UniqueStatistics()).unique_books
        authors = bingo_stats.square_uniques.get(square_name, UniqueStatistics()).unique_authors
        subbed_in_books += books
        subbed_in_authors += authors

    return f"""Out of {bingo_stats.total_card_count} cards, {bingo_stats.subbed_out_squares.total()} used the Substitution rule.

### Books

{format_top_book_counts(subbed_in_books, 3)}

### Authors

{format_top_author_counts(subbed_in_authors, 3)}

### Squares

{format_most_subbed_squares(subbed_in_squares, 3)}."""


def format_bingos(
    bingo_type_stats: BingoTypeStatistics,
    incomplete_cards: Collection[CardID],
) -> str:

    total_nonblackout_bingos = 0
    for card_id in incomplete_cards:
        total_nonblackout_bingos += bingo_type_stats.complete_bingos_by_card[card_id]

    ranked_bingos_by_card = bingo_type_stats.incomplete_bingos.most_common()
    ranked_bingos_by_squares = bingo_type_stats.incomplete_squares_by_bingo.most_common()

    hardest_bingos_by_card, hardest_bingo_by_card_count = get_single_ties(
        ranked_bingos_by_card, "high"
    )
    hardest_bingos_by_square, hardest_bingo_by_square_count = get_single_ties(
        ranked_bingos_by_squares, "high"
    )
    easiest_bingos_by_card, easiest_bingo_by_card_count = get_single_ties(
        ranked_bingos_by_card, "low"
    )
    easiest_bingos_by_square, easiest_bingo_by_square_count = get_single_ties(
        ranked_bingos_by_squares, "low"
    )

    cards_per_complete_bingo = Counter(bingo_type_stats.complete_bingos_by_card.values())

    bingo_str = f"""
There were {bingo_type_stats.complete_bingos_by_card.total()} complete bingos.
Non-blackout cards completed an average of {total_nonblackout_bingos/len(incomplete_cards):.1f} bingos.
There were {cards_per_complete_bingo[0]} cards that did not complete any bingos.

{format_inline_bingo_ties(hardest_bingos_by_card, 'hard', 'card')}, incomplete on {hardest_bingo_by_card_count} cards.
{format_inline_bingo_ties(hardest_bingos_by_square, 'hard', 'square')}, with a total of {hardest_bingo_by_square_count} squares left blank.

{format_inline_bingo_ties(easiest_bingos_by_card, 'easi', 'card')}, incomplete on {easiest_bingo_by_card_count} cards.
{format_inline_bingo_ties(easiest_bingos_by_square, 'easi', 'square')}, with a total of {easiest_bingo_by_square_count} squares left blank.

"""

    table_strs: list[tuple[str, str, str]] = [
        ("BINGO TYPE", "# CARDS INCOMPLETE", "# SQUARES INCOMPLETE"),
        ("---------", ":---------:", ":---------:"),
    ]
    for bingo_name in POSSIBLE_BINGOS.keys():
        table_strs.append(
            (
                bingo_name,
                str(bingo_type_stats.incomplete_bingos[bingo_name]),
                str(bingo_type_stats.incomplete_squares_by_bingo[bingo_name]),
            )
        )

    return bingo_str + "\n".join("|" + "|".join(row) + "|" for row in table_strs)


def format_author_statistics(
    overall_author_stats: AuthorStatistics,
    unique_author_stats: AuthorStatistics,
) -> str:
    eth_table = format_author_demo(
        overall_author_stats.ethnicity_count, unique_author_stats.ethnicity_count, "ETHNICITY"
    )
    nat_table = format_author_demo(
        overall_author_stats.nationality_count,
        unique_author_stats.nationality_count,
        "NATIONALITY",
    )
    gender_table = format_author_demo(
        overall_author_stats.gender_count, unique_author_stats.gender_count, "GENDER"
    )

    table_strs: list[tuple[str, str, str]] = [
        ("QUEER?", "% OVERALL", "% UNIQUE"),
        ("---------", ":---------:", ":---------:"),
    ]
    for demo in (True, False, None):
        overall_prop = (
            overall_author_stats.queer_count[demo] / overall_author_stats.queer_count.total()
        ) * 100
        unique_prop = (
            unique_author_stats.queer_count[demo] / unique_author_stats.queer_count.total()
        ) * 100
        if unique_prop > 1:
            table_strs.append(
                (
                    "Yes" if demo is True else "No" if demo is False else "Unknown",
                    f"{overall_prop:.1f}",
                    f"{unique_prop:.1f}",
                )
            )
    queer_table = "\n".join("|" + "|".join(row) + "|" for row in table_strs)
    return "\n\n".join([eth_table, nat_table, gender_table, queer_table])


def generate_reddit_post(
    bingo_stats: BingoStatistics, card_data: CardData, summary_stats: SummaryStats, year: int
) -> str:
    return f"""# New Bingo Stats Hub

This post was consistently too long to post in its entirety and making one comment per square was getting old.
In order to better support the length, I've spun up a GitHub Pages site to host all of the stats: https://smartflutist661.github.io/rfantasy-bingo-stats.
The remainder of this post is an _abbreviated_ version (no plots, no per-square statistics),
so I recommend just going to the page for [this year's stats](https://smartflutist661.github.io/rfantasy-bingo-stats/{year}).

# Preliminary Notes

Format has been shamelessly copied from previous bingo stats posts:
  - [2023](https://www.reddit.com/r/Fantasy/comments/1cd0kdk/statistics_for_the_2023_rfantasy_bingo/)
  - [2022](https://www.reddit.com/r/Fantasy/comments/12xs3c1/2022_rfantasy_bingo_statistics/)
  - [2021](https://www.reddit.com/r/Fantasy/comments/ude8f4/2021_rfantasy_bingo_stats/)
  - [2020](https://www.reddit.com/r/Fantasy/comments/npvigf/2020_rfantasy_bingo_statistics/)
  - [2019](https://www.reddit.com/r/Fantasy/comments/gjq0ym/2019_rfantasy_bingo_statistics/)
  - [2018](https://www.reddit.com/r/Fantasy/comments/bbm35a/2018_rfantasy_bingo_statistics/)
  - [2017](https://www.reddit.com/r/Fantasy/comments/89esvx/2017_fantasy_bingo_statistics/)
  - [2016](https://www.reddit.com/r/Fantasy/comments/62sp9h/2016_fantasy_bingo_statistics/)

1. Stories were not examined for fitness. If you used **1984** for **Novella**, it was included in the statistics for that square.
In addition, if you did something like, say, put **The Lost Metal** as a short story, I made no effort to figure out where it actually belonged.
2. When a series was specified, it was collapsed to the first book. Graphic novels, light novels, manga, and webserials were collapsed from issues to the overall series.
3. Books by multiple authors were counted once for each author.
E.g.: **In the Heart of Darkness** by Eric Flint and David Drake counts as a read for both Eric Flint and David Drake.
*However*, books by a writing team with a single-author pseudonym, e.g. M.A. Carrick, were counted once for the pseudonym, and not for the authors behind the pseudonym.
4. Author demographic statistics are now included below. However, researching all {len(bingo_stats.overall_uniques.unique_authors)} individual authors
is quite an undertaking, and there is still a reasonable amount of information missing, especially regarding Nationality.
By the time next year's stats roll around I hope to have it reasonably complete.
5. Short stories were excluded from most of the stats below. They *were* included in the total story count.

# And Now: The Stats
    
## Overall Stats

### Squares and Cards

- There were {bingo_stats.total_card_count} cards submitted, {len(bingo_stats.incomplete_cards)} of which were incomplete.
The minimum number of filled squares was {25 - bingo_stats.max_incomplete_squares}. {bingo_stats.incomplete_squares_per_card[1]} were *this close*, with 24 filled squares.
{bingo_stats.incomplete_squares.total()} squares were left blank, leaving {bingo_stats.total_card_count*25 - bingo_stats.incomplete_cards.total()} filled squares.
- There were {bingo_stats.total_story_count} total stories, with {len(bingo_stats.overall_uniques.unique_books)} unique stories read,
by {len(bingo_stats.overall_uniques.unique_authors)} unique authors ({bingo_stats.overall_uniques.unique_authors.total()} total).
{get_used_once(bingo_stats.overall_uniques.unique_books)} books and {get_used_once(bingo_stats.overall_uniques.unique_authors)} authors were used only once. 
- The top squares left blank were: {format_bottom_square_counts(bingo_stats)}. On the other hand, {format_favorite_square(bingo_stats, card_data.square_names.values())}.
- The squares most often substituted were: {format_most_subbed_squares(bingo_stats.subbed_out_squares)}.
{format_least_subbed_square(bingo_stats.subbed_out_squares, card_data.square_names.values())}.
This means that {summary_stats.most_avoided[0]} was the least favorite overall, skipped or substituted a total of {summary_stats.most_avoided[1]} times, and
{summary_stats.least_avoided[0]} was the favorite, skipped or substituted only {summary_stats.least_avoided[1]} times.
- There were an average of {summary_stats.mean_uniques:.1f} unique books per card.
- {summary_stats.all_hm_count} cards claimed an all-hard-mode card, while {summary_stats.almost_hm_count} cards were short by one square.
{summary_stats.no_hm_count} cards claimed no hard-mode squares at all. The average number of hard-mode squares per card was {summary_stats.avg_hm_per_card:.1f}.
There were a total of {bingo_stats.hard_mode_by_square.total()} hard-mode squares claimed.

{format_square_table(bingo_stats, card_data.square_names.values())}

### Books

The ten most-read books were:

{format_top_book_counts(bingo_stats.overall_uniques.unique_books)}

The books used for the most squares were:

{format_most_square_books(bingo_stats.unique_squares_by_book)}

{format_book(summary_stats.max_square_ratio_book)} was the book read at least 10 times with the highest ratio of squares to times read:
read {bingo_stats.overall_uniques.unique_books[summary_stats.max_square_ratio_book]} times for {bingo_stats.unique_squares_by_book[summary_stats.max_square_ratio_book]} squares.

One of those interesting stats phenomena: even though most cards only include a few unique books, most of the books read are unique.
There were an average of {summary_stats.avg_reads_per_book:.1f} reads per book.

### Authors

The ten most-read authors were:

{format_top_author_counts(bingo_stats.overall_uniques.unique_authors)}

The authors used for the most squares were:

{format_most_square_authors(bingo_stats.unique_squares_by_author)}

{summary_stats.max_square_ratio_author} was the author read at least 10 times with the highest ratio of squares to times read:
read {bingo_stats.overall_uniques.unique_authors[summary_stats.max_square_ratio_author]} times for {bingo_stats.unique_squares_by_author[summary_stats.max_square_ratio_author]} squares.

The authors with the most unique books read were:

{format_unique_author_books(bingo_stats.books_per_author)}

As with books, most authors were read only once.
There were an average of {summary_stats.avg_reads_per_author:.1f} reads per author.

The following tables represent a best-effort attempt at a statistical breakdown of author demographics.
The "Overall %" column represents the _total_ number of times a demographic appeared in Bingo data,
i.e. Brandon Sanderson counts {bingo_stats.overall_uniques.unique_authors[Author("Brandon Sanderson")]} times for each of his demographic groups.
The "Unique %" column represents the unique number of times a demographic appeared in Bingo data,
i.e. Brandon Sanderson counts only once, no matter how many squares or cards he appears on.

Demographics representing less than 1% of the unique authors are not included in these tables. 

{format_author_statistics(bingo_stats.overall_author_stats, bingo_stats.unique_author_stats)}

### Bingos

#### Normal Mode
{format_bingos(bingo_stats.normal_bingo_type_stats, bingo_stats.incomplete_cards.keys())}

#### Hard Mode
{format_bingos(bingo_stats.hardmode_bingo_type_stats, [card_id for card_id, hm_count in bingo_stats.hard_mode_by_card.items() if hm_count != BINGO_SIZE**2])}

## Variety

The FarraGini index, [introduced in 2017](https://www.reddit.com/r/Fantasy/comments/89esvx/2017_fantasy_bingo_statistics/) (see Part III),
attempts to measure the variety of books and authors read for each square.
Each entity's "income" for a square is the number of times it was used for that square,
so the index is analogous to its namesake, the [Gini index](https://en.wikipedia.org/wiki/Gini_coefficient):

Values close to 0 suggest a square was well-varied; 0 means no book was repeated for a square.
Values close to 100 suggest the same books were used repeatedly for a square; 100 means only one book was used for a square.

{format_farragini(bingo_stats, card_data.square_names.values())}

## Wall of Shame

Quoting the [very first bingo stats post](https://www.reddit.com/r/Fantasy/comments/62sp9h/2016_fantasy_bingo_statistics/),

> You are all terrible spellers.

A "misspelling" for the purposes of these statistics is any book (title/author combination)
that does not match the version used as the canonical version during cleaning.
There were a total of {bingo_stats.bad_spellings_by_card.total()} misspellings.
(Note that this does not include short stories.)

{format_dedupe_counts(bingo_stats)}

What makes a book hard to "spell" correctly?

- Length
- Lots of articles or prepositions
- Non-ASCII characters (diacritics, etc.)
- Lots of authors
- Numbers
- Somewhat obviously, books that were published under multiple titles

Predictably, there's a lot of crossover between books with the most variations and the most-read books overall.

## Substitutions

{format_subbed_stats(bingo_stats)}
"""


def format_square_links(card_data: CardData) -> str:
    lines = ["|   |   |   |   |   |", "|---|---|---|---|---|"]
    line = "|"
    for square_num, square_name in enumerate(card_data.square_names.values()):
        line += f"[{square_name}]({card_data.square_names_to_files[square_name]})|"
        if square_num % 5 == 4:
            lines.append(line)
            line = "|"

    return "\n".join(lines)


def generate_square_markdown(
    bingo_stats: BingoStatistics,
    card_data: CardData,
    square_num: int,
    square_name: SquareName,
    year: int,
) -> str:
    return f"""---
layout: base
---
# {year} r/Fantasy Bingo Stats, Square {square_num}: {square_name}

This page includes summary statistics for a single square of the bingo card.
Summary statistics for the whole card can be found [here](../{year}).
Statistics for other squares can be found at the following links:

{format_square_links(card_data)}

{format_square_stats(square_name, bingo_stats)}
"""


def generate_index_markdown(
    bingo_stats: BingoStatistics,
    card_data: CardData,
    summary_stats: SummaryStats,
    plots: Plots,
    year: int,
) -> str:
    return f"""---
layout: base
---
# {year} r/Fantasy Bingo Stats

This page contains summary statistics for the whole card. Individual square statistics can be found at the following links:

{format_square_links(card_data)}

## Square and Card Statistics

- There were {bingo_stats.total_card_count} cards submitted, {len(bingo_stats.incomplete_cards)} of which were incomplete.
The minimum number of filled squares was {25 - bingo_stats.max_incomplete_squares}. {bingo_stats.incomplete_squares_per_card[1]} were *this close*, with 24 filled squares.
{bingo_stats.incomplete_squares.total()} squares were left blank, leaving {bingo_stats.total_card_count*25 - bingo_stats.incomplete_cards.total()} filled squares.
- There were {bingo_stats.total_story_count} total stories, with {len(bingo_stats.overall_uniques.unique_books)} unique stories read,
by {len(bingo_stats.overall_uniques.unique_authors)} unique authors ({bingo_stats.overall_uniques.unique_authors.total()} total).
{get_used_once(bingo_stats.overall_uniques.unique_books)} books and {get_used_once(bingo_stats.overall_uniques.unique_authors)} authors were used only once. 
- The top squares left blank were: {format_bottom_square_counts(bingo_stats)}. On the other hand, {format_favorite_square(bingo_stats, card_data.square_names.values())}.
- The squares most often substituted were: {format_most_subbed_squares(bingo_stats.subbed_out_squares)}.
{format_least_subbed_square(bingo_stats.subbed_out_squares, card_data.square_names.values())}.
This means that {summary_stats.most_avoided[0]} was the least favorite overall, skipped or substituted a total of {summary_stats.most_avoided[1]} times, and
{summary_stats.least_avoided[0]} was the favorite, skipped or substituted only {summary_stats.least_avoided[1]} times.
- There were an average of {summary_stats.mean_uniques:.1f} unique books per card.
- {summary_stats.all_hm_count} cards claimed an all-hard-mode card, while {summary_stats.almost_hm_count} cards were short by one square.
{summary_stats.no_hm_count} cards claimed no hard-mode squares at all. The average number of hard-mode squares per card was {summary_stats.avg_hm_per_card:.1f}.
There were a total of {bingo_stats.hard_mode_by_square.total()} hard-mode squares claimed.

{format_square_table(bingo_stats, card_data.square_names.values())}

{plots.yearly_plots.incompletes.to_html()}
{plots.yearly_plots.hard_mode.to_html()}

### Year-over-Year

To see how these numbers have changed over the course of bingo, here are some plots.

{plots.yoy_plots.participants.to_html()}
{plots.yoy_plots.squares_per_card.to_html()}
{plots.yoy_plots.cards_per_person.to_html()}
{plots.yoy_plots.hm_per_nonhm_card.to_html()}
{plots.yoy_plots.hard_mode.to_html()}
{plots.yoy_plots.hero_mode.to_html()}
{plots.yoy_plots.uniqueness.to_html()}

## Book Statistics

The ten most-read books were:

{format_top_book_counts(bingo_stats.overall_uniques.unique_books)}

The books used for the most squares were:

{format_most_square_books(bingo_stats.unique_squares_by_book)}

The books used the most times per square were:

{format_most_reads_per_square_books(bingo_stats.overall_uniques.unique_books, bingo_stats.unique_squares_by_book)}

{format_book(summary_stats.max_square_ratio_book)} was the book read at least 10 times with the highest ratio of squares to times read:
read {bingo_stats.overall_uniques.unique_books[summary_stats.max_square_ratio_book]} times for {bingo_stats.unique_squares_by_book[summary_stats.max_square_ratio_book]} squares.

{plots.yearly_plots.book_reads.to_html()}
{plots.yearly_plots.uniques.to_html()}

One of those interesting stats phenomena: even though most cards only include a few unique books, most of the books read are unique.
There were an average of {summary_stats.avg_reads_per_book:.1f} reads per book.

## Author Statistics

The ten most-read authors were:

{format_top_author_counts(bingo_stats.overall_uniques.unique_authors)}

The authors used for the most squares were:

{format_most_square_authors(bingo_stats.unique_squares_by_author)}

{summary_stats.max_square_ratio_author} was the author read at least 10 times with the highest ratio of squares to times read:
read {bingo_stats.overall_uniques.unique_authors[summary_stats.max_square_ratio_author]} times for {bingo_stats.unique_squares_by_author[summary_stats.max_square_ratio_author]} squares.

The authors with the most unique books read were:

{format_unique_author_books(bingo_stats.books_per_author)}

{plots.yearly_plots.author_reads.to_html()}

As with books, most authors were read only once.
There were an average of {summary_stats.avg_reads_per_author:.1f} reads per author.

The following tables represent a best-effort attempt at a statistical breakdown of author demographics.
The "Overall %" column represents the _total_ number of times a demographic appeared in Bingo data,
i.e. Brandon Sanderson counts {bingo_stats.overall_uniques.unique_authors[Author("Brandon Sanderson")]} times for each of his demographic groups.
The "Unique %" column represents the unique number of times a demographic appeared in Bingo data,
i.e. Brandon Sanderson counts only once, no matter how many squares or cards he appears on.

Demographics representing less than 1% of the unique authors are not included in these tables. 

{format_author_statistics(bingo_stats.overall_author_stats, bingo_stats.unique_author_stats)}

## Bingo-type Statistics

### Normal Mode
{format_bingos(bingo_stats.normal_bingo_type_stats, bingo_stats.incomplete_cards.keys())}

{plots.yearly_plots.bingos.to_html()}

### Hard Mode
{format_bingos(bingo_stats.hardmode_bingo_type_stats, [card_id for card_id, hm_count in bingo_stats.hard_mode_by_card.items() if hm_count != BINGO_SIZE**2])}

{plots.yearly_plots.hm_bingos.to_html()}

## Book Variety (Per Square)

The FarraGini index, [introduced in 2017](https://www.reddit.com/r/Fantasy/comments/89esvx/2017_fantasy_bingo_statistics/) (see Part III),
attempts to measure the variety of books and authors read for each square.
Each entity's "income" for a square is the number of times it was used for that square,
so the index is analogous to its namesake, the [Gini index](https://en.wikipedia.org/wiki/Gini_coefficient):

Values close to 0 suggest a square was well-varied; 0 means no book was repeated for a square.
Values close to 100 suggest the same books were used repeatedly for a square; 100 means only one book was used for a square.

{format_farragini(bingo_stats, card_data.square_names.values())}

> [!CAUTION]
> TODO
> INSERT COMMENTARY HERE

## Wall of Shame

Quoting the [very first bingo stats post](https://www.reddit.com/r/Fantasy/comments/62sp9h/2016_fantasy_bingo_statistics/),

> You are all terrible spellers.

A "misspelling" for the purposes of these statistics is any book (title/author combination)
that does not match the version used as the canonical version during cleaning.
There were a total of {bingo_stats.bad_spellings_by_card.total()} misspellings.
(Note that this does not include short stories.)

{format_dedupe_counts(bingo_stats)}

What makes a book hard to "spell" correctly?

- Length
- Lots of articles or prepositions
- Non-ASCII characters (diacritics, etc.)
- Lots of authors
- Numbers
- Somewhat obviously, books that were published under multiple titles

Predictably, there's a lot of crossover between books with the most variations and the most-read books overall.

### Year-over-Year

{plots.yoy_plots.misspellings.to_html()}

Is it true that "every year we typo further from God"? Proportionally, we collectively seem to be improving,
though absolute numbers are still increasing. There may not be enough data to draw strong conclusions yet, though.

## Substitutions

{format_subbed_stats(bingo_stats)}
"""


def create_markdown(
    bingo_stats: BingoStatistics,
    card_data: CardData,
    post_draft_path: Path,
    plots: Plots,
    year: int,
) -> None:
    """Create a Markdown draft of stats"""

    most_avoided_square, most_avoided_count = bingo_stats.avoided_squares.most_common(1)[0]
    fav_index = 0
    least_avoided_square = SquareName("")
    least_avoided_count = None
    while least_avoided_square not in card_data.square_names.values():
        # Loops around and progresses backwards
        fav_index -= 1
        least_avoided_square, least_avoided_count = bingo_stats.avoided_squares.most_common()[
            fav_index
        ]
    if least_avoided_count is None:
        raise ValueError("No least-avoided square found")

    max_square_ratio_book = None
    max_ratio = 0.0
    for book, square_count in bingo_stats.unique_squares_by_book.items():
        total_count = bingo_stats.overall_uniques.unique_books[book]
        if total_count >= 10:
            count_ratio = square_count / total_count
            if count_ratio > max_ratio:
                max_ratio = count_ratio
                max_square_ratio_book = book

    if max_square_ratio_book is None:
        raise ValueError("No book found for max unique squares to total times read ratio")

    max_square_ratio_author = None
    max_ratio = 0.0
    for author, square_count in bingo_stats.unique_squares_by_author.items():
        total_count = bingo_stats.overall_uniques.unique_authors[author]
        if total_count >= 10:
            count_ratio = square_count / total_count
            if count_ratio > max_ratio:
                max_ratio = count_ratio
                max_square_ratio_author = author

    if max_square_ratio_author is None:
        raise ValueError("No author found for max unique squares to total times read ratio")

    hard_mode_by_card_counts = Counter(bingo_stats.hard_mode_by_card.values())

    summary_stats = SummaryStats(
        most_avoided=(most_avoided_square, most_avoided_count),
        least_avoided=(least_avoided_square, least_avoided_count),
        mean_uniques=float(np.mean(list(bingo_stats.card_uniques.values()))),
        all_hm_count=hard_mode_by_card_counts[25],
        almost_hm_count=hard_mode_by_card_counts[24],
        no_hm_count=hard_mode_by_card_counts[0],
        avg_hm_per_card=float(np.mean(list(bingo_stats.hard_mode_by_card.values()))),
        avg_reads_per_book=float(np.mean(list(bingo_stats.overall_uniques.unique_books.values()))),
        avg_reads_per_author=float(
            np.mean(list(bingo_stats.overall_uniques.unique_authors.values()))
        ),
        max_square_ratio_book=max_square_ratio_book,
        max_square_ratio_author=max_square_ratio_author,
    )

    post_markdown = generate_reddit_post(bingo_stats, card_data, summary_stats, year)

    LOGGER.info(f"Markdown output:\n\n{post_markdown}")
    with post_draft_path.open("w", encoding="utf8") as post_draft_file:
        post_draft_file.write(post_markdown)

    pages_root = REPO_ROOT / "docs" / str(year)
    index_markdown = generate_index_markdown(bingo_stats, card_data, summary_stats, plots, year)
    with (pages_root / "index.md").open("w", encoding="utf8") as index_file:
        index_file.write(index_markdown)

    for square_num, square_name in enumerate(card_data.square_names.values()):
        square_markdown = generate_square_markdown(
            bingo_stats, card_data, square_num + 1, square_name, year
        )
        filename = card_data.square_names_to_files[square_name]
        with (pages_root / f"{filename}.md").open("w", encoding="utf8") as square_file:
            square_file.write(square_markdown)
        filename = card_data.square_names_to_files[square_name]
        with (pages_root / f"{filename}.md").open("w", encoding="utf8") as square_file:
            square_file.write(square_markdown)
