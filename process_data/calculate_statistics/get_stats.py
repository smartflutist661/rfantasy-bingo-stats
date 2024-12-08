"""
Created on Apr 7, 2023

@author: fred
"""
from collections import Counter

import numpy as np

from ..data.current import (
    CUSTOM_SEPARATOR,
    OUTPUT_MD_FILEPATH,
    SQUARE_NAMES,
)
from ..data_operations.author_title_book_operations import book_to_title_author
from ..types.bingo_statistics import BingoStatistics
from ..types.defined_types import (
    Author,
    Book,
    SquareName,
)
from .gini_function import calculate_gini_index


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
    last_count = -1
    place_count = 0
    cur_ties = []
    for book, count in unique_books.most_common():
        if last_count == count:
            cur_ties.append(format_book(book))
        else:
            if len(cur_ties) == 1:
                book_count_strs.append("- " + cur_ties[0] + f", read {last_count} times")
            elif len(cur_ties) > 1:
                book_count_strs.append(
                    "- TIE: " + " and ".join(cur_ties) + f", each read {last_count} times"
                )

            place_count += 1
            if place_count > top_n:
                break

            cur_ties = []
            cur_ties.append(format_book(book))

        last_count = count
    return "\n".join(book_count_strs)


def format_bottom_square_counts(bingo_stats: BingoStatistics, bottom_n: int = 3) -> str:
    """Format most-incomplete squares"""
    incomplete_square_strs = []
    last_count = -1
    place_count = 0
    cur_ties = []
    for incomplete_square, count in bingo_stats.incomplete_squares.most_common():
        if last_count == count:
            cur_ties.append(format_square(incomplete_square))
        else:
            if len(cur_ties) > 1:
                incomplete_square_strs.append(
                    " and ".join(cur_ties) + f", blank on {last_count} cards each"
                )
            elif len(cur_ties) == 1:
                incomplete_square_strs.append("".join(cur_ties) + f", blank on {last_count} cards")
            cur_ties = []
            place_count += 1
            if place_count > bottom_n:
                break

            cur_ties.append(format_square(incomplete_square))

        last_count = count
    return "; ".join(incomplete_square_strs)


def format_favorite_square(bingo_stats: BingoStatistics) -> str:
    """Format square completed most often"""
    print(bingo_stats.incomplete_squares)
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
    last_count = -1
    place_count = 0
    cur_ties = []
    for subbed_square, count in subbed_squares.most_common():
        if last_count == count:
            cur_ties.append(format_square(subbed_square))
        else:
            if len(cur_ties) > 1:
                subbed_square_strs.append(
                    " and ".join(cur_ties) + f", substituted on {last_count} cards each"
                )
            elif len(cur_ties) == 1:
                subbed_square_strs.append(
                    "".join(cur_ties) + f", substituted on {last_count} cards"
                )
            cur_ties = []

            place_count += 1
            if place_count > top_n:
                break

            cur_ties.append(format_square(subbed_square))

        last_count = count

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
    last_count = -1
    place_count = 0
    cur_ties = []
    for author, count in unique_authors.most_common():
        if last_count == count:
            cur_ties.append(author)
        else:
            if len(cur_ties) == 1:
                author_count_strs.append("- " + cur_ties[0] + f", read {last_count} times")
            elif len(cur_ties) > 1:
                author_count_strs.append(
                    "- TIE: " + " and ".join(cur_ties) + f", each read {last_count} times"
                )

            place_count += 1
            if place_count > top_n:
                break

            cur_ties = []
            cur_ties.append(author)

        last_count = count
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

**TOTAL**: {len(bingo_stats.square_uniques[square_name].unique_authors)} unique authors read.
"""


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


def format_square_table(bingo_stats: BingoStatistics) -> str:
    """Format a table of FarraGini indices"""
    table_strs: list[tuple[str, str, str]] = [
        ("SQUARE", "% COMPLETE", "% HARD MODE"),
        ("---------", ":---------:", ":---------:"),
    ]
    total_cards = bingo_stats.total_card_count
    for square_name in SQUARE_NAMES.values():
        table_strs.append(
            (
                square_name,
                f"{100 - bingo_stats.incomplete_squares[square_name]/total_cards*100:.1f}",
                f"{bingo_stats.hard_mode_by_square[square_name]/total_cards*100:.1f}",
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


def format_dedupe_counts(bingo_stats: BingoStatistics) -> str:
    """Format the counts of book variations"""
    book_vars = []
    cur_ties: list[str] = []
    last_count = -1
    place_count = 0
    for book, count in bingo_stats.bad_spellings_by_book.most_common():
        if last_count == count:
            cur_ties.append(format_book(book))
        else:
            if len(cur_ties) == 1:
                book_vars.append("- " + cur_ties[0] + f", with {last_count} variations")
            elif len(cur_ties) > 1:
                book_vars.append(
                    "- TIE: " + " and ".join(cur_ties) + f", with {last_count} variations each"
                )

            place_count += 1
            if place_count > 10:
                break

            cur_ties = []
            cur_ties.append(format_book(book))

        last_count = count

    book_str = "\n".join(book_vars)

    return f"""The books with the most variation in title or author spellings were:

{book_str}"""


def format_most_square_books(unique_squares_by_book: Counter[Book]) -> str:
    """Format the books used for the most different squares"""
    book_strs = []
    cur_ties: list[str] = []
    last_count = -1
    place_count = 0
    for book, count in unique_squares_by_book.most_common():
        if last_count == count:
            cur_ties.append(format_book(book))
        else:
            if len(cur_ties) == 1:
                book_strs.append("- " + cur_ties[0] + f", used for {last_count} squares")
            elif len(cur_ties) > 1:
                book_strs.append(
                    "- TIE: " + " and ".join(cur_ties) + f", each used for {last_count} squares"
                )

            place_count += 1
            if place_count > 3:
                break

            cur_ties = []
            cur_ties.append(format_book(book))

        last_count = count

    return "\n".join(book_strs)


def format_most_square_authors(unique_squares_by_author: Counter[Author]) -> str:
    """Format the authors used for the most different squares"""
    book_strs = []
    cur_ties: list[str] = []
    last_count = -1
    place_count = 0
    for author, count in unique_squares_by_author.most_common():
        if last_count == count:
            cur_ties.append(author)
        else:
            if len(cur_ties) == 1:
                book_strs.append("- " + cur_ties[0] + f", used for {last_count} squares")
            elif len(cur_ties) > 1:
                book_strs.append(
                    "- TIE: " + " and ".join(cur_ties) + f", each used for {last_count} squares"
                )

            place_count += 1
            if place_count > 3:
                break

            cur_ties = []
            cur_ties.append(author)

        last_count = count

    return "\n".join(book_strs)


def format_unique_author_books(books_per_author: Counter[Author]) -> str:
    """Format the counts of author varieties"""
    book_strs = []
    cur_ties: list[str] = []
    last_count = -1
    place_count = 0
    for author, count in books_per_author.most_common():
        if last_count == count:
            cur_ties.append(author)
        else:
            if len(cur_ties) == 1:
                book_strs.append("- " + cur_ties[0] + f", with {last_count} unique books read")
            elif len(cur_ties) > 1:
                book_strs.append(
                    "- TIE: "
                    + " and ".join(cur_ties)
                    + f", each with {last_count} unique books read"
                )

            place_count += 1
            if place_count > 10:
                break

            cur_ties = []
            cur_ties.append(author)

        last_count = count

    return "\n".join(book_strs)


def create_markdown(bingo_stats: BingoStatistics) -> None:
    """Create a Markdown draft of stats"""

    most_avoided_square, most_avoided_count = bingo_stats.avoided_squares.most_common(1)[0]

    max_ratio = 0.0
    for book, square_count in bingo_stats.unique_squares_by_book.items():
        total_count = bingo_stats.overall_uniques.unique_books[book]
        if total_count >= 10:
            count_ratio = square_count / total_count
            if count_ratio > max_ratio:
                max_ratio = count_ratio
                max_square_ratio_book = book

    max_ratio = 0.0
    for author, square_count in bingo_stats.unique_squares_by_author.items():
        total_count = bingo_stats.overall_uniques.unique_authors[author]
        if total_count >= 10:
            count_ratio = square_count / total_count
            if count_ratio > max_ratio:
                max_ratio = count_ratio
                max_square_ratio_author = author

    mean_uniques = np.mean(list(bingo_stats.card_uniques.values()))

    hard_mode_by_card_counts = Counter(bingo_stats.hard_mode_by_card.values())

    avg_hm = np.mean(list(bingo_stats.hard_mode_by_card.values()))

    avg_reads_per_book = np.mean(list(bingo_stats.overall_uniques.unique_books.values()))
    avg_reads_per_author = np.mean(list(bingo_stats.overall_uniques.unique_authors.values()))

    markdown_lines = f"""# Preliminary Notes

Most of this post, and all of these statistics, were generated by a script I wrote, [available on GitHub](https://github.com/smartflutist661/rfantasy-bingo-stats).
Anyone is welcome to contribute there. You can find the raw data, corrected data, and some more extensive summary statistics at that link, as well.
See [last year's post](https://www.reddit.com/r/Fantasy/comments/12gyb45/cleaning_2022_and_future_bingo_data/) for some technical details.

Format has been shamelessly copied from previous bingo stats posts:

  - [2022](https://www.reddit.com/r/Fantasy/comments/12xs3c1/2022_rfantasy_bingo_statistics/)
  - [2021](https://www.reddit.com/r/Fantasy/comments/ude8f4/2021_rfantasy_bingo_stats/)
  - [2020](https://www.reddit.com/r/Fantasy/comments/npvigf/2020_rfantasy_bingo_statistics/)
  - [2019](https://www.reddit.com/r/Fantasy/comments/gjq0ym/2019_rfantasy_bingo_statistics/)
  - [2018](https://www.reddit.com/r/Fantasy/comments/bbm35a/2018_rfantasy_bingo_statistics/)
  - [2017](https://www.reddit.com/r/Fantasy/comments/89esvx/2017_fantasy_bingo_statistics/)
  - [2016](https://www.reddit.com/r/Fantasy/comments/62sp9h/2016_fantasy_bingo_statistics/)

Likewise, the following notes are shamelessly adapted.

1. Stories were not examined for fitness. If you used **1984** for **Novella**, it was included in the statistics for that square.
In addition, if you did something like, say, put **The Lost Metal** as a short story, I made no effort to figure out where it actually belonged.
2. Series were collapsed to their first book. Graphic novels, light novels, manga, and webserials were collapsed from issues to the overall series.
3. Books by multiple authors were counted once for each author. E.g.: **In the Heart of Darkness** by Eric Flint and David Drake counts as a read for both Eric Flint and David Drake.
*However*, books by a writing team with a single-author pseudonym, e.g. M.A. Carrick, were counted once for the pseudonym, and not for the authors behind the pseudonym.
4. Author demographic statistics are not included below, for two reasons: it quickly gets messy and culturally-specific,
and I didn't want to stalk all {len(bingo_stats.overall_uniques.unique_authors)} individual authors. Machinery for these calculations are included in the script, however,
so if anyone would like to supply demographic information, it is easy to include.
5. Short stories were excluded from most of the stats below. They *were* included in the total story count.

# And Now: The Stats
    
## Overall Stats

### Squares and Cards

- There were {bingo_stats.total_card_count} cards submitted, {len(bingo_stats.incomplete_cards)} of which were incomplete.
The minimum number of filled squares was {25 - bingo_stats.max_incomplete_squares}. {bingo_stats.incomplete_squares_per_card[1]} were *this close*, with 24 filled squares.
{bingo_stats.incomplete_squares.total()} squares were left blank, leaving {bingo_stats.total_card_count*25 - bingo_stats.incomplete_cards.total()} filled squares.
- There were {bingo_stats.total_story_count} total stories, with {len(bingo_stats.overall_uniques.unique_books)} unique stories read,
by {len(bingo_stats.overall_uniques.unique_authors)} unique authors.
- The top three squares left blank were: {format_bottom_square_counts(bingo_stats)}. On the other hand, {format_favorite_square(bingo_stats)}.
- The three squares most often substituted were: {format_most_subbed_squares(bingo_stats.subbed_out_squares)}. {format_least_subbed_square(bingo_stats.subbed_out_squares)}.
This means that {most_avoided_square} was the least favorite overall, skipped or substituted a total of {most_avoided_count} times.
- There were an average of {mean_uniques:.1f} unique books per card.
- {hard_mode_by_card_counts[25]} cards claimed an all-hard-mode card, while {hard_mode_by_card_counts[24]} cards were short by one square.
{hard_mode_by_card_counts[0]} cards claimed no hard-mode squares at all. The average number of hard-mode squares per card was {avg_hm:.1f}.

{format_square_table(bingo_stats)}

<INSERT PLOTS HERE>

### Books

The ten most-read books were:

{format_top_book_counts(bingo_stats.overall_uniques.unique_books)}

The books used for the most squares were:

{format_most_square_books(bingo_stats.unique_squares_by_book)}

{format_book(max_square_ratio_book)} was the book read at least 10 times with the highest ratio of squares to times read:
read {bingo_stats.overall_uniques.unique_books[max_square_ratio_book]} times for {bingo_stats.unique_squares_by_book[max_square_ratio_book]} squares.

<INSERT PLOT HERE>

There were an average of {avg_reads_per_book} reads per book.

### Authors

The ten most-read authors were:

{format_top_author_counts(bingo_stats.overall_uniques.unique_authors)}

The authors used for the most squares were:

{format_most_square_authors(bingo_stats.unique_squares_by_author)}

{max_square_ratio_author} was the author read at least 10 times with the highest ratio of squares to times read:
read {bingo_stats.overall_uniques.unique_authors[max_square_ratio_author]} times for {bingo_stats.unique_squares_by_author[max_square_ratio_author]} squares.

The authors with the most unique books read were:

{format_unique_author_books(bingo_stats.books_per_author)}

<INSERT_PLOT_HERE>

There were an average of {avg_reads_per_author} reads per author.

## Stats for Individual Squares

{format_all_squares(bingo_stats)}
## Substitutions

{format_subbed_stats(bingo_stats)}

## Variety

Values close to 0 suggest a square was well-varied; 0 means no book was repeated for a square.
Values close to 100 suggest the same books were used repeatedly for a square; 100 means only one book was used for a square.

{format_farragini(bingo_stats)}

## Wall of Shame

{format_dedupe_counts(bingo_stats)}
"""

    print()
    print(markdown_lines)

    with OUTPUT_MD_FILEPATH.open("w", encoding="utf8") as md_file:
        md_file.write(markdown_lines)
