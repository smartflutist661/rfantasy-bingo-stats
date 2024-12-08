"""
Created on Apr 14, 2023

@author: fred
"""
import json

from process_data.data.filepaths import DUPE_RECORD_FILEPATH
from process_data.data_operations.author_title_book_operations import (
    book_to_title_author,
    books_to_title_authors,
)
from process_data.types.recorded_states import RecordedStates

if __name__ == "__main__":
    with DUPE_RECORD_FILEPATH.open("r", encoding="utf8") as dupe_file:
        known_states = RecordedStates.from_data(json.load(dupe_file))

    for book, book_dupes in known_states.book_dupes.items():
        _, author = book_to_title_author(book, known_states.book_separator)
        author_dupes = {
            author for _, author in books_to_title_authors(book_dupes, known_states.book_separator)
        }
        known_states.author_dupes[author] |= author_dupes

    with open("test.json", "w") as test_file:
        json.dump(known_states.to_data(), test_file)
