"""
Created on Apr 7, 2023

@author: fred
"""
from collections import Counter

import pandas

from ..data.current import (
    CUSTOM_SEPARATOR,
    OUTPUT_MD_FILEPATH,
    SQUARE_NAMES,
)
from ..data_operations.author_title_book_operations import (
    book_to_title_author,
    get_all_title_author_combos,
    get_unique_book_counts,
)
from ..types.bingo_statistics import (
    BingoStatistics,
    UniqueStatistics,
)
from ..types.defined_types import (
    Author,
    Book,
    SquareName,
)
from .get_bingo_cards import get_bingo_cards
from .gini_function import calculate_gini_index


def get_summary_statistics(bingo_data: pandas.DataFrame) -> BingoStatistics:
    """Do preliminary math and prepare to save to file"""
    all_title_authors = get_all_title_author_combos(bingo_data)
    unique_book_counts = get_unique_book_counts(all_title_authors, CUSTOM_SEPARATOR)

    unique_author_counts = Counter(author for _, author in all_title_authors)

    (
        bingo_cards,
        subbed_squares,
        incomplete_cards,
        incomplete_squares,
        square_uniques,
        unique_square_usage_by_book,
        unique_square_usage_by_author,
    ) = get_bingo_cards(bingo_data)

    assert incomplete_cards.total() == incomplete_squares.total()

    subbed_out_squares = Counter(subbed_out for subbed_out, _ in subbed_squares.keys())
    for square_name in SQUARE_NAMES.values():
        subbed_out_squares[square_name] += 0

    unique_square_usage_count_by_book: Counter[Book] = Counter()
    for book, squares in unique_square_usage_by_book.items():
        unique_square_usage_count_by_book[book] = len(squares)

    unique_square_usage_count_by_author: Counter[Author] = Counter()
    for author, squares in unique_square_usage_by_author.items():
        unique_square_usage_count_by_author[author] = len(squares)

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
            unique_books=unique_book_counts,
            unique_authors=unique_author_counts,
        ),
        square_uniques=square_uniques,
        unique_squares_by_book=unique_square_usage_count_by_book,
        unique_squares_by_author=unique_square_usage_count_by_author,
    )


def format_book(book: Book) -> str:
    """Format a title/author pair into a string"""
    title_author = book_to_title_author(book, CUSTOM_SEPARATOR)
    return f"**{title_author[0]}** by {title_author[1]}"


def format_square(square_name: SquareName) -> str:
    """Format a square name"""
    return f"**{square_name}**"


def format_top_book_counts(unique_books: Counter[Book], top_n: int = 10) -> str:
    """Format counts of top N unique reads"""
    book_count_strs = []
    for book, count in unique_books.most_common(top_n):
        book_count_strs.append(f"* {format_book(book)}, read {count} times")
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
        + f"time{'s'*(fewest_incomplete != 1)}{' each' * multiple_favorites}"
    )


def format_most_subbed_squares(subbed_squares: Counter[SquareName], top_n: int = 3) -> str:
    """Format the sqaure subbed most often"""
    subbed_square_strs = []
    for subbed_square, subbed_count in subbed_squares.most_common(top_n):
        subbed_square_strs.append(
            f"{format_square(subbed_square)}, substituted on {subbed_count} cards"
        )
    return "; ".join(subbed_square_strs)


def format_least_subbed_square(subbed_squares: Counter[SquareName]) -> str:
    """Format the string for the least-subbed bingo square"""
    fewest_subbed = min(subbed_squares.values())
    fewest_subbed_squares = []
    for square_name, subbed_count in subbed_squares.items():
        if subbed_count == fewest_subbed and square_name in SQUARE_NAMES.values():
            fewest_subbed_squares.append(square_name)

    multiple_low_subs = len(fewest_subbed_squares) > 1
    if multiple_low_subs:
        low_sub_string = (
            ", ".join(format_square(square_name) for square_name in fewest_subbed_squares[:-1])
            + f"{',' * (len(fewest_subbed_squares) > 2)} and {format_square(fewest_subbed_squares[-1])}"
        )
    else:
        low_sub_string = format_square(fewest_subbed_squares[0])

    if fewest_subbed == 0:
        return f"{low_sub_string} {'were' * multiple_low_subs}{'was' * (not multiple_low_subs)} never subsituted"
    return (
        f"{low_sub_string} {'were' * multiple_low_subs}{'was' * (not multiple_low_subs)} "
        + f"only left blank {fewest_subbed} time{'s'*(fewest_subbed != 1)}{' each' * multiple_low_subs}"
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

{format_top_book_counts(bingo_stats.square_uniques[square_name].unique_books, 5)}

**TOTAL**: {bingo_stats.square_uniques[square_name].unique_books.total()} books read, with {len(bingo_stats.square_uniques[square_name].unique_books)} unique titles.
Skipped {bingo_stats.incomplete_squares[square_name]} times. Substituted {bingo_stats.subbed_out_squares[square_name]} times.

#### Most Read Authors

{format_top_author_counts(bingo_stats.square_uniques[square_name].unique_authors, 5)}

**TOTAL**: {len(bingo_stats.square_uniques[square_name].unique_authors)} unique authors read."""


def format_all_squares(bingo_stats: BingoStatistics) -> str:
    """Format stats for every square"""
    square_strs = []
    for square_num, square_name in enumerate(SQUARE_NAMES.values()):
        square_strs.append(format_square_stats(square_num + 1, square_name, bingo_stats))
    return "\n".join(square_strs)


def format_farragini(bingo_stats: BingoStatistics) -> str:
    """Format a table of FarraGini indices"""
    table_strs: list[tuple[str, str, str]] = [
        ("SQUARE", "BOOK", "AUTHOR"),
        ("---------", ":---------:", ":---------:"),
    ]
    for square_name in SQUARE_NAMES.values():
        table_strs.append(
            (
                square_name,
                f"{calculate_gini_index(tuple(bingo_stats.square_uniques[square_name].unique_books.values()))*100:.1f}",
                f"{calculate_gini_index(tuple(bingo_stats.square_uniques[square_name].unique_authors.values()))*100:.1f}",
            )
        )
    return "\n".join("|" + "|".join(row) + "|" for row in table_strs)


def format_subbed_stats(bingo_stats: BingoStatistics) -> str:
    """Format stats on squares that were subbed for others"""

    subbed_in_squares = Counter(subbed_in for _, subbed_in in bingo_stats.subbed_squares.keys())

    subbed_in_books: Counter[Book] = Counter()
    subbed_in_authors: Counter[Author] = Counter()
    for square_name in subbed_in_squares:
        books = bingo_stats.square_uniques[square_name].unique_books
        authors = bingo_stats.square_uniques[square_name].unique_authors
        subbed_in_books += books
        subbed_in_authors += authors

    return f"""Out of {bingo_stats.total_card_count} cards, {bingo_stats.subbed_out_squares.total()} used the Substitution rule.

### Books

{format_top_book_counts(subbed_in_books, 3)}

### Authors

{format_top_author_counts(subbed_in_authors, 3)}

### Squares

{format_most_subbed_squares(subbed_in_squares, 3)}."""


def create_markdown(bingo_stats: BingoStatistics) -> None:
    """Create a Markdown draft of stats"""

    most_avoided_square, most_avoided_count = bingo_stats.avoided_squares.most_common(1)[0]

    (
        book_with_most_squares,
        book_with_most_squares_count,
    ) = bingo_stats.unique_squares_by_book.most_common(1)[0]

    max_ratio = 0.0
    for book, square_count in bingo_stats.unique_squares_by_book.items():
        total_count = bingo_stats.overall_uniques.unique_books[book]
        if total_count >= 10:
            count_ratio = square_count / total_count
            if count_ratio > max_ratio:
                max_ratio = count_ratio
                max_square_ratio_book = book

    (
        author_with_most_squares,
        author_with_most_squares_count,
    ) = bingo_stats.unique_squares_by_author.most_common(1)[0]

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
* There were {bingo_stats.total_story_count} total stories, with {len(bingo_stats.overall_uniques.unique_books)} unique stories read,
by {len(bingo_stats.overall_uniques.unique_authors)} unique authors.
* The top three squares left blank were: {format_bottom_square_counts(bingo_stats)}. On the other hand, {format_favorite_square(bingo_stats)}.
* The three squares most often substituted were: {format_most_subbed_squares(bingo_stats.subbed_out_squares)}. {format_least_subbed_square(bingo_stats.subbed_out_squares)}.

This means that {most_avoided_square} was the least favorite overall, skipped or substituted a total of {most_avoided_count} times.

The ten most-read books were:

{format_top_book_counts(bingo_stats.overall_uniques.unique_books)}

{format_book(book_with_most_squares)} was used for the most individual squares, {book_with_most_squares_count}.

{format_book(max_square_ratio_book)} was the book read at least 10 times with the highest ratio of squares to times read:
read {bingo_stats.overall_uniques.unique_books[max_square_ratio_book]} times for {bingo_stats.unique_squares_by_book[max_square_ratio_book]} squares. 

The ten most-read authors were:

{format_top_author_counts(bingo_stats.overall_uniques.unique_authors)}

{author_with_most_squares} was used for the most individual squares, {author_with_most_squares_count}.

## Square Stats

{format_all_squares(bingo_stats)}

## Substitutions

{format_subbed_stats(bingo_stats)}

## Variety

{format_farragini(bingo_stats)}
"""

    print()
    print(markdown_lines)

    with OUTPUT_MD_FILEPATH.open("w", encoding="utf8") as md_file:
        md_file.write(markdown_lines)
