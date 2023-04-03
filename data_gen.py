"""CSC111 Course Project:  Books On Books On Books

===============================

This module contains a collection of Python functions for cleaning and processing book review data and book metadata,
and for generating a graph that represents relationships between books based on user ratings.

Copyright and Usage Information
===============================

This file is Copyright (c) 2023 Ethan Chan, Ernest Yuen, Alyssa Lu, and Kelsie Fung.
"""
from typing import Any
import json
import similar_books_graph as bg

AllBooksDict = dict[bg.BookID, dict[str, Any]]


def get_users(review_file: str, save_to_file: bool = False, file_save_name: str = '') -> bg.UsersReadDict | None:
    """Given a review dataset, generate a mapping of user ID to all the books they have read. Each book ID itself maps
    to a rating that the user gave it. This function essentially cleans the original "review" datasets downloaded.
    """
    users = {}
    with open(review_file) as f:

        # the reviews file contains multiple jsons, so we need to go through each one in the file
        for review in f:
            review_dict = json.loads(review)
            user_id = review_dict['user_id']

            # if the user is not already in the dictionary, create the mapping from the user to a dict mapping the book
            # ID to the rating
            if user_id not in users:
                users[user_id] = {review_dict['book_id']: review_dict['rating']}
            else:  # otherwise the dictionary already exists, so we can mutate it
                users[user_id][review_dict['book_id']] = review_dict['rating']

    # write to a file if we want to save it for later use
    if save_to_file:
        with open(file_save_name, 'w') as output_f:
            json_str = json.dumps(users, indent=4)
            output_f.write(json_str)
    else:
        return users


def clean_books(books_data_file: str, save_to_file: bool = False, file_save_name: str = '') -> AllBooksDict:
    """Given a filename of one of the goodreads book datasets (separated by genre), clean it by selecting only
    the relevant data, and then returning it/saving it for later use.
    """
    books = {}

    with open(books_data_file) as f:
        for book in f:
            book_dict = json.loads(book)
            book_id = book_dict['book_id']

            # choose the information relevant to us, and store it
            selected_keys = ['average_rating', 'description', 'image_url', 'title']
            selected_data = {}
            for selected_key in selected_keys:
                selected_data[selected_key] = book_dict[selected_key]

            books[book_id] = selected_data

    # write to a file if we want to save it for later use
    if save_to_file:
        with open(file_save_name, 'w') as output_f:
            json_str = json.dumps(books, indent=4)
            output_f.write(json_str)
    else:
        return books


def get_cleaned_data(filename: str) -> bg.UsersReadDict | AllBooksDict:
    """Given a valid filename representing cleaned users_read data or all_books data, then read that file, and return
    a corresponding dictionary object.
    """
    with open(filename) as f:
        dictionary = json.load(f)
        return dictionary


def get_genres(genres: list[str]) -> tuple[bg.UsersReadDict, AllBooksDict]:
    """Given a list of genres, retrieve both the users_read dictionary and all_books dictionary data corresponding
    to each genre, then return a tuple containing those two types of dictionaries, but merged for all genres
    """
    users_read_multiple = []
    all_books_multiple = []
    for genre in genres:
        users_read_multiple.append(get_cleaned_data(f'users_read/{genre}.json'))
        all_books_multiple.append(get_cleaned_data(f'books/books_{genre}.json'))
    # merge the dictionaries
    users_read = {}
    all_books = {}

    for i in range(0, len(users_read_multiple)):
        # merge all the users_read datasets together
        for u_id in users_read_multiple[i]:
            if u_id not in users_read:  # we can set the read books dict directly
                users_read[u_id] = users_read_multiple[i][u_id]
            else:  # we must mutate the read books dict, as it already has information we don't want to overwrite
                users_read[u_id].update(users_read_multiple[i][u_id])

        # the consequences of the books datasets overwriting is not important, because even if a book appears twice, in
        # two different genres, it still has the same metadata
        all_books.update(all_books_multiple[i])

    print('Retrieved all books and users...')
    return (users_read, all_books)


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)

    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['similar_books_graph', 'typing', 'json'],
        'allowed-io': ['get_users', 'clean_books', 'get_cleaned_data', 'get_genres'],
        'max-line-length': 120,
        'disable': ['E9992', 'E9997']
    })
