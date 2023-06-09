"""CSC111 Course Project:  Books On Books On Books

===============================

This module contains a Python class that enables the user interface to run a simulation of the BookNetwork.

Copyright and Usage Information
===============================

This file is Copyright (c) 2023 Ethan Chan, Ernest Yuen, Alyssa Lu, and Kelsie Fung.
"""

import similar_books_graph as bg
import data_gen


class RunBookNetwork:
    """A runner class that operates the BookNetwork class from inputs given by the GUI.

    Instance Attributes:
    - all_books:
        A dictionary containing all the books within the intial parameters the user selected, mapping from book ID to
        the book's attributes, including title, average rating, a short description, and a link to an image of the book.
    - book_network:
        An instance of the BookNetwork class, initialised with books (and users) pertaining to a given set of genres
    - users_read:
        A mapping of each user to the books they have read, and their respective ratings, used to initialise the
        BookNetwork instance
    """
    all_books: data_gen.AllBooksDict
    book_network: bg.BookNetwork
    users_read: bg.UsersReadDict

    def __init__(self, genres: list[str]) -> None:
        """Initialise a RunBookNetwork, which then initialises a BookNetwork with books from the given genres.
        Additionally, store the all_books and users_read dict objects relevant to the BookNetwork.

        Preconditions:
            - all(genre in ['comics_graphic', 'fantasy_paranormal', 'mystery_thriller_crime',
                  'romance', 'young_adult'] for genre in genres)
        """
        self.users_read, self.all_books = data_gen.get_genres(genres)

        user_list = list(self.users_read.keys())

        self.book_network = bg.BookNetwork(user_list, self.users_read)

    def rating_metric(self, book: bg.Node) -> float:
        """This is a function that may be passed to the get_books_by_statistic() method , that calculates the rating of
        each book while trying to take into account the number of ratings as well, since simply returning the
        average_rating would favor books with low numbers of ratings who have a few high values (e.g. a book with only
        one rating of 5 vs. 4.5 average over 80 ratings).

        The way the number of ratings is taken into account is through the Bayesian average, which essentially factors
        in outside knowledge (i.e. some pre-existing rating/average for the book) to balance the number of ratings.
        The formula is, where w represents the weight, and m the numeric value of the already-known statistic:
                bayesian_average = (w * m + sum of all n ratings) / (w + n)

        The already-known statistic here will be the average rating (on GoodReads) retrieved from the datasets of books.
        """
        w = 3
        m = float(self.all_books[book.obj_id]['average_rating'])
        n = len(book.connected)

        # still, we want books to have at least 10 ratings
        if n < 10:
            return 0

        return (w * m + n * book.rating) / (w + n)

    def get_recommended_books(self, method: str) -> list[bg.BookID]:
        """Get the recommended books from the book network given a certain method (random, popularity, or rating)

        Preconditions:
        - method.lower() in ['rating', 'popularity', 'random']
        """
        if method == 'rating':
            return self.book_network.get_books_by_statistic(self.rating_metric)
        elif method == 'popularity':
            return self.book_network.get_books_by_statistic(lambda book: len(book.connected))
        else:
            return self.book_network.get_books_by_random()
