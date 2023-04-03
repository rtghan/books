"""CSC111 Course Project:  Books On Books On Books

===============================

This module contains a collection of Python functions for cleaning and processing book review data and book metadata,
and for generating a graph that represents relationships between books based on user ratings.

Copyright and Usage Information
===============================

This file is Copyright (c) 2023 Ethan Chan, Ernest Yuen, Alyssa Lu, and Kelsie Fung.
"""
import similar_books_graph as bg
from typing import Any
import json

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
    users_read = users_read_multiple.pop()
    all_books = all_books_multiple.pop()

    for i in range(0, len(users_read_multiple)):
        users_read.update(users_read_multiple[i])
        all_books.update(all_books_multiple[i])
    print('Retrieved all books and users...')
    return (users_read, all_books)

# def convert_set(users_books: dict[bg.UserID, list[bg.BookID]]) -> dict[bg.UserID, set[bg.BookID]]:
#     """Given a mapping between user IDs and the books they have read, return an equivalent mapping, but from
#     ID to set instead."""
#     users_books_set = {}
#
#     for uid in users_books:
#         users_books_set[uid] = set(users_books[uid])
#
#     return users_books_set
