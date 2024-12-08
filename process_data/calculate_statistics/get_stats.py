"""
Created on Apr 7, 2023

@author: fred
"""
from collections import Counter

import pandas

from ..data.current import (
    OUTPUT_MD_FILEPATH,
    SQUARE_NAMES,
)
from ..data_operations.author_title_book_operations import (
    get_all_title_author_combos,
    get_unique_title_author_counts,
)
from ..types.bingo_statistics import (
    BingoStatistics,
    UniqueStatistics,
)
from ..types.defined_types import (
    Author,
    SquareName,
    TitleAuthor,
)
from .get_bingo_cards import get_bingo_cards


def get_summary_statistics(bingo_data: pandas.DataFrame) -> BingoStatistics:
    """Do preliminary math and prepare to save to file"""
    all_title_authors = get_all_title_author_combos(bingo_data)
    unique_title_author_counts = get_unique_title_author_counts(all_title_authors)

    unique_author_counts = Counter(author for _, author in all_title_authors)

    (
        bingo_cards,
        subbed_squares,
        incomplete_cards,
        incomplete_squares,
        square_uniques,
        unique_square_usage,
    ) = get_bingo_cards(bingo_data)

    assert incomplete_cards.total() == incomplete_squares.total()

    subbed_out_squares = Counter(subbed_out for subbed_out, _ in subbed_squares.keys())

    unique_square_usage_count: Counter[TitleAuthor] = Counter()
    for title_author, squares in unique_square_usage.items():
        unique_square_usage_count[title_author] = len(squares)

    return BingoStatistics(
        total_card_count=len(bingo_cards),
        incomplete_cards=incomplete_cards,
        incomplete_squares=incomplete_squares,
        max_incomplete_squares=max(
            incomplete for incomplete in incomplete_cards.values() if incomplete != 25
        ),
        incomplete_squares_per_card=Counter(incomplete_cards.values()),
        total_story_count=len(all_title_authors),
        subbed_squares=subbed_squares,
        subbed_out_squares=subbed_out_squares,
        avoided_squares=incomplete_squares + subbed_out_squares,
        overall_uniques=UniqueStatistics(
            unique_title_authors=unique_title_author_counts,
            unique_authors=unique_author_counts,
        ),
        square_uniques=square_uniques,
    )


def format_title_author(title_author: TitleAuthor) -> str:
    """Format a title/author pair into a string"""
    return f"**{title_author[0]}**, by {title_author[1]}"


def format_square(square_name: SquareName) -> str:
    """Format a square name"""
    return f"**{square_name}**"


def format_top_book_counts(unique_title_authors: Counter[TitleAuthor], top_n: int = 10) -> str:
    """Format counts of top N unique reads"""
    book_count_strs = []
    for title_author, count in unique_title_authors.most_common(top_n):
        book_count_strs.append(f"* {format_title_author(title_author)}, read {count} times")
    return "\n".join(book_count_strs)


def format_bottom_square_counts(bingo_stats: BingoStatistics, bottom_n: int = 3) -> str:
    """Format most-incomplete squares"""
    incomplete_square_strs = []
    for incomplete_square, blank_count in bingo_stats.incomplete_squares.most_common(bottom_n):
        incomplete_square_strs.append(
            f"{format_square(incomplete_square)}, blank on {blank_count} cards"
        )
    return "; ".join(incomplete_square_strs)


def format_favorite_square(bingo_stats: BingoStatistics) -> str:
    """Format square completed most often"""
    fewest_incomplete = min(
        incomplete
        for square, incomplete in bingo_stats.incomplete_squares.items()
        if square in SQUARE_NAMES.values()
    )
    most_filled_squares = []
    for square_name, incomplete_count in bingo_stats.incomplete_squares.items():
        if incomplete_count == fewest_incomplete and square_name in SQUARE_NAMES.values():
            most_filled_squares.append(square_name)

    multiple_favorites = len(most_filled_squares) > 1
    if multiple_favorites:
        fave_str = (
            ", ".join(format_square(square_name) for square_name in most_filled_squares[:-1])
            + f", and {format_square(most_filled_squares[-1])}"
        )
    else:
        fave_str = format_square(most_filled_squares[0])

    return (
        f"{fave_str} {'were' * multiple_favorites}{'was' * (not multiple_favorites)} "
        + f"only left blank {fewest_incomplete} "
        + f"time{'s'*(fewest_incomplete > 1)}{' each' * multiple_favorites}"
    )


def format_most_subbed_squares(bingo_stats: BingoStatistics, top_n: int = 3) -> str:
    """Format the sqaure subbed most often"""
    subbed_square_strs = []
    for subbed_square, subbed_count in bingo_stats.subbed_out_squares.most_common(top_n):
        subbed_square_strs.append(
            f"{format_square(subbed_square)}, substituted on {subbed_count} cards"
        )
    return "; ".join(subbed_square_strs)


def format_least_subbed_square(bingo_stats: BingoStatistics) -> str:
    """Format the string for the least-subbed bingo square"""
    fewest_subbed = min(bingo_stats.subbed_out_squares.values())
    fewest_subbed_squares = []
    for square_name, subbed_count in bingo_stats.subbed_out_squares.items():
        if subbed_count == fewest_subbed and square_name in SQUARE_NAMES.values():
            fewest_subbed_squares.append(square_name)

    multiple_low_subs = len(fewest_subbed_squares) > 1
    if multiple_low_subs:
        low_sub_string = (
            ", ".join(format_square(square_name) for square_name in fewest_subbed_squares[:-1])
            + f", and {format_square(fewest_subbed_squares[-1])}"
        )
    else:
        low_sub_string = format_square(fewest_subbed_squares[0])

    return (
        f"{low_sub_string} {'were' * multiple_low_subs}{'was' * (not multiple_low_subs)} "
        + f"only left blank {fewest_subbed} time{'s'*(fewest_subbed > 1)}{' each' * multiple_low_subs}"
    )


def format_top_author_counts(unique_authors: Counter[Author], top_n: int = 10) -> str:
    """Format counts of top N unique authors"""
    author_count_strs = []
    for author, count in unique_authors.most_common(top_n):
        author_count_strs.append(f"* {author}, read {count} times")
    return "\n".join(author_count_strs)


def format_square_stats(
    square_num: int,
    square_name: SquareName,
    bingo_stats: BingoStatistics,
) -> str:
    """Format stats for a single square"""
    return f"""### {square_num}. {square_name}

#### Most Read Books

{format_top_book_counts(bingo_stats.square_uniques[square_name].unique_title_authors, 5)}

#### Most Read Authors

{format_top_author_counts(bingo_stats.square_uniques[square_name].unique_authors, 5)}
"""


def format_all_squares(bingo_stats: BingoStatistics) -> str:
    """Format stats for every square"""
    square_strs = []
    for square_num, square_name in enumerate(SQUARE_NAMES.values()):
        square_strs.append(format_square_stats(square_num + 1, square_name, bingo_stats))
    return "\n".join(square_strs)


def create_markdown(bingo_stats: BingoStatistics) -> None:
    """Create a Markdown draft of stats"""

    most_avoided_square, most_avoided_count = bingo_stats.avoided_squares.most_common(1)[0]

    markdown_lines = f"""# Preliminary Notes

Most of this post, and all of these statistics, were generated by a script I wrote, [available on GitHub](https://github.com/smartflutist661/rfantasy-bingo-stats).
Anyone is welcome to contribute there. The raw data is also available.

Format has been shamelessly copied from u/FarragutCircle's previous bingo stats:

  * [2020](https://www.reddit.com/r/Fantasy/comments/npvigf/2020_rfantasy_bingo_statistics/)
  * [2019](https://www.reddit.com/r/Fantasy/comments/gjq0ym/2019_rfantasy_bingo_statistics/)
  * [2018](https://www.reddit.com/r/Fantasy/comments/bbm35a/2018_rfantasy_bingo_statistics/)
  * [2017](https://www.reddit.com/r/Fantasy/comments/89esvx/2017_fantasy_bingo_statistics/)
  * [2016](https://www.reddit.com/r/Fantasy/comments/62sp9h/2016_fantasy_bingo_statistics/)

Likewise, the following notes are shamelessly adapted.

1. Stories were not examined for fitness. If you used **All That's Left in the World** for **No Ifs, Ands, or Buts**, it was included in the statistics for that square.
In addition, if you did something like, say, put **Spinning Silver** as a short story, I made no effort to figure out where it actually belonged.
2. Series were collapsed to their first book. Graphic novels, light novels, manga, and webserials were collapsed from issues to the overall series.

# And Now: The Stats
    
## Overall Stats

* There were {bingo_stats.total_card_count} cards submitted, {len(bingo_stats.incomplete_cards)} of which were incomplete.
The minimum number of filled squares was {25 - bingo_stats.max_incomplete_squares}. {bingo_stats.incomplete_squares_per_card[1]} were *this close*, with 24 filled squares.
{bingo_stats.incomplete_squares.total()} squares were left blank, leaving {bingo_stats.total_card_count*25 - bingo_stats.incomplete_cards.total()} filled squares.
* There were {bingo_stats.total_story_count} total stories, with {len(bingo_stats.overall_uniques.unique_title_authors)} unique stories read,
by {len(bingo_stats.overall_uniques.unique_authors)} unique authors.
* The top three squares left blank were: {format_bottom_square_counts(bingo_stats)}. On the other hand, {format_favorite_square(bingo_stats)}.
* The three squares most often substituted were: {format_most_subbed_squares(bingo_stats)}. {format_least_subbed_square(bingo_stats)}.

This means that {most_avoided_square} was the least favorite overall, skipped or substituted a total of {most_avoided_count} times.

The ten most-read books were:

{format_top_book_counts(bingo_stats.overall_uniques.unique_title_authors)}

The ten most-read authors were:

{format_top_author_counts(bingo_stats.overall_uniques.unique_authors)}

Now for the squares:

{format_all_squares(bingo_stats)}

"""

    print()
    print(markdown_lines)

    with OUTPUT_MD_FILEPATH.open("w", encoding="utf8") as md_file:
        md_file.write(markdown_lines)
