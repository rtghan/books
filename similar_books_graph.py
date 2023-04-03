"""CSC111 Course Project:  Books On Books On Books

===============================

This module contains a collection of Python classes and functions to represent a network of books and users.

Copyright and Usage Information
===============================

This file is Copyright (c) 2023 Ethan Chan, Ernest Yuen, Alyssa Lu, and Kelsie Fung.
"""
from __future__ import annotations
from typing import Callable
import random

# what we define as a good rating
GOOD_RATING = 3.5

# type aliases for clearer type annotations
UserID = str
BookID = str
UsersReadDict = dict[UserID, dict[BookID, float | int]]


class Node:
    """A node that represents a user or book in the network.

    Instance Attributes
    - is_user:
        Whether self is represents a user (giving a review), or a book
    - obj_id:
        The book/user id
    - connected:
        A dictionary containing all the nodes connected to self, mapping from their id to the actual Node object
    - rating:
        A book-only statistic that records the average rating of all the users connected to it

    Representation Invariants:
    - self.is_user == all(node.is_user is False for node in self.connected)
    """
    is_user: bool
    obj_id: UserID | BookID
    connected: dict[str, Node]
    rating: float

    def __init__(self, is_user: bool, obj_id: UserID | BookID) -> None:
        """Initialise a singular node that is either a book/user, with given id
        """
        self.is_user = is_user
        self.obj_id = obj_id
        self.connected = {}
        self.rating = 0

    def __str__(self) -> str:
        return self.obj_id

    def connect(self, neighbour_node: Node) -> None:
        """Connects a node to this node
        """
        self.connected[neighbour_node.obj_id] = neighbour_node
        neighbour_node.connected[self.obj_id] = self


class BookNetwork:
    """A graph of user/book nodes that should hold users of "similar taste" to the client, and the books that they
    enjoy.

    Instance Attributes:
    - users:
        A mapping of a UserID value to its corresponding Node (User) object, for each user in the graph
    - books:
        A mapping of a BookID value to its corresponding Node (Book) Object, for each book in the graph
    - users_read:
        A mapping of each user to the books they have read, and their respective ratings
    - used:
        A set of the IDs of the books that have already been given to the user. We would not like to repeat the books
        we show the user, as that would make the development of the network much slower.

    Representation Invariants:
    - all(i == i.obj_id for i in self.users)
    - all(j == j.obj_id for j in self.books)
    """
    users: dict[BookID, Node]
    books: dict[BookID, Node]
    users_read: dict[UserID, dict[BookID, float | int]]
    used: set[BookID]

    def __init__(self, similar: list[UserID], users_read: UsersReadDict) -> None:
        """Initialise a BookNetwork made of the users listed in similar, or if similar is empty, initialise a
        BookNetwork containing every user in the 'reviews' dataset.

        Preconditions:
            - all(user in users_read for user in self.similar)
        """
        self.users = {}
        self.books = {}
        self.users_read = users_read
        self.used = set()

        # for each user in the list of similar users, we generate their Node
        for u_id in similar:
            user_node = Node(True, u_id)
            self.users[u_id] = user_node

            # then generate the neighbours and connect them
            for book_id in self.users_read[u_id]:

                # it is possible that the book already exists in the Graph, so if it does, we would just like to
                # connect to it instead of remaking the Node object (and erasing its previous connections)
                if book_id in self.books:
                    user_node.connect(self.books[book_id])

                    # update the rating as well
                    book = self.books[book_id]
                    user_rating = self.users_read[u_id][book_id]
                    n = len(book.connected)

                    # average before this node = (r_1 + r_2 + ... r_n-1) / (n-1), so multiplying by (n-1)/n =
                    # (r_1 + r_2 + ... + r_n-1) / n.
                    book.rating *= ((n - 1) / n)
                    # Add (r_n / n) to get the new average rating: (r_1 + r_2 + ... + r_n-1 + r_n) / n
                    book.rating += (user_rating / n)

                else:  # otherwise just make a new Node object, and connect it
                    book_node = Node(False, book_id)
                    self.books[book_id] = book_node
                    user_node.connect(book_node)
                    # set the rating of the book node to the rating this user has given it
                    book_node.rating = self.users_read[u_id][book_id]

    def __str__(self) -> str:
        return f'Books: {self.books}\nUsers: {self.users}'

    def get_books_by_statistic(self, metric: Callable, n: int = 3) -> list[BookID]:
        """Select the books in BookNetwork that return the highest metrics based on some statistic (popularity, or
        rating), and return a list of them (to the client for them to evaluate, so our book network may evolve to
        better reflect their tastes).
            Popularity Based:
            The most popular books are the ones with the most connections, though they may not have the best ratings.

            Rating Based:
            Since the rating is based on the users in the graph, and not the book's true rating on GoodReads, we hope
            that it will reflect 'a rating by users of similar taste'.
        """
        # get a list of all the book Node objects
        book_lst = list(self.books.values())

        # if the call wants all or more of the (unrecommended) books that are left in the network, simply
        # return all the available books
        if n >= len(book_lst) - len(self.used):
            return [book.obj_id for book in book_lst]

        # sort the books by the metric
        book_lst.sort(key=metric, reverse=True)

        # get the n highest ranking books (that have not already been recommended)
        recommended = []
        idx = 0
        count = 0

        # only want to return n books
        while count < n:
            b_id = book_lst[idx].obj_id
            # can recommend the book if it hasn't been already
            if b_id not in self.used:
                recommended.append(b_id)
                self.used.add(b_id)
                count += 1
            # keep going through indexes
            idx += 1

        return recommended

    def get_books_by_random(self, n: int = 3) -> list[BookID]:
        """Select n random books, and return a list of them (to the client for them to evaluate).
        """
        book_id_lst = list(self.books.keys())

        # if the call wants all or more of the (unrecommended) books that are left in the network, simply
        # return all the available books
        if n >= len(book_id_lst) - len(self.used):
            return book_id_lst

        # otherwise, randomly pick n books
        recommended = []
        i = 0
        while i < n:
            choice = random.randint(0, len(book_id_lst))
            # account for duplicates and already used books
            if book_id_lst[choice] not in self.used:
                recommended.append(book_id_lst[choice])
                self.used.add(book_id_lst[choice])
                i += 1

        return recommended

    def prune(self, exclude_lst: list[BookID]) -> list[UserID]:
        """Given a list of books to exclude (client doesn't like), mutate the network to remove those users.
        This should make the statistics computed by the network (rating, popularity) more in line with the tastes of
        the user. This function also returns the list of "dissimilar" users.
        """
        dissimilar = []

        users = list(self.users.keys())
        # go through each user to remove only ones with "dissimilar taste"
        for u_id in users:
            # go through each book that the client doesn't like
            for exclude_id in exclude_lst:
                # check if that book exists in the client's read/reviewed books, and if they liked it
                if exclude_id in self.users_read[u_id] and self.users_read[u_id][exclude_id] >= GOOD_RATING:
                    # remove the user from the network if so
                    dissimilar.append(u_id)
                    self.disconnect(self.users[u_id])
                    break

        return dissimilar

    def disconnect(self, node: Node) -> None:
        """Given a node within this network, disconnect it by removing it from the dictionary of books/users, as well
        as removing it from the '.connected' attribute of each of its neighbours.
        """
        # removing a user node means updating the rating of the neighbouring book nodes
        if node.is_user:
            u_id = node.obj_id
            # we must remove its connections to its books
            for book_id in node.connected:
                # get the connections of the book
                book = node.connected[book_id]

                # update rating
                n = len(book.connected)
                user_rating = self.users_read[u_id][book_id]
                # we should only update the average if there is more than 1 user, as if there is only 1 user, then
                # we will be removing the only user who rates the book
                if n > 1:
                    # similar computation as in adding connections
                    book.rating *= (n / (n - 1))
                    book.rating -= (user_rating / (n - 1))

                # remove its connection to this node
                del book.connected[u_id]

            # remove the user from the graph
            del self.users[u_id]

        # removing a book
        else:
            b_id = node.obj_id
            # remove all connections to connected users
            for u_id in node.connected:
                # get the connections of the user
                user = node.connected[u_id]
                # remove the book from the connections
                del user.connected[b_id]

                # if the user has no more connections, remove it from the graph
                if len(user.connected) == 0:
                    del self.users[u_id]

            # remove the book from the graph
            del self.books[b_id]


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)

    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['__future__', 'typing', 'random'],
        'max-line-length': 120,
        'disable': ['E9992', 'E9997']
    })
