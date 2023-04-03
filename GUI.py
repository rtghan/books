from tkinter import *
from tkinter import ttk
from urllib.request import urlopen
from PIL import Image, ImageTk

import book_selection as rb
import similar_books_graph as bg
import data_gen


class BookSetup:
    """A class that handles the setup and first inputs of the application: getting the genres the client is interested
    in, and when they would like to begin finding books.

    Instance Attributes:
    - genre_widgets:
        A dictionary mapping each genre to a Checkbutton widget, as well as a corresponding variable, to make for easy
        data retrieval.
    - init_widgets:
        A list of widgets that are only used in the initial setup, and can be removed afterwards.
    - root:
        The instance of Tk upon which this BookSetup is placed
    """
    genre_widgets: dict[str, tuple[Checkbutton, BooleanVar]]
    init_widgets: list[Widget]

    def __init__(self, root: Tk) -> None:
        self.root = root
        root.title('Books On Books On Books')

        # define the main frame, 3px padding on left and right, 12px on top and bottom
        mainframe = ttk.Frame(root, padding='3 3 12 12')
        mainframe.grid(column=0, row=0, sticky=N)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # create the genre input widgets, and save the dictionary that can be used to access any input values
        self.genre_widgets = self.genre_input(mainframe)
        # the button that will be used to start the computations
        self.init_widgets = [ttk.Button(mainframe, text='Start Finding Books!', command=self.run_booknetwork)]
        # position the button
        self.init_widgets[0].grid(column=3, row=2, sticky=W)

        # pad every widget within the frame so everything is not squished
        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def genre_input(self, frame: Frame) -> dict[str, tuple[Checkbutton, BooleanVar]]:
        """This function generates the input widgets for getting the genres the client is interested in.
        """
        # possible genres to choose from
        genres = ['Comics and Graphic Novels', 'Fantasy and Paranormal', 'Mystery, Thriller, and Crime', 'Romance',
                  'Young Adult']

        widgets = {}

        for i in range(0, len(genres)):
            # generate the widget and variable for each genre
            genre_variable = BooleanVar(value=False)
            genre_checkbox = ttk.Checkbutton(frame, text=genres[i], variable=genre_variable,
                                             onvalue=True, offvalue=False)
            # store them in the dictionary
            widgets[genres[i]] = (genre_checkbox, genre_variable)

            # position the widget
            widgets[genres[i]][0].grid(column=0, row=i, sticky=W)

        return widgets

    def run_booknetwork(self) -> None:
        """This function is called once the user clicks the "Start Finding Books" button, and creates a RunBookNetwork
         instance to be used to recommend books to the user.
         """
        # map the keys returned from genre_input to the genres used in RunBookNetwork
        genres = {'Comics and Graphic Novels': 'comics_graphic', 'Fantasy and Paranormal': 'fantasy_paranormal',
                  'Mystery, Thriller, and Crime': 'mystery_thriller_crime', 'Romance': 'romance',
                  'Young Adult': 'young_adult'}

        chosen_genres = [genres[genre] for genre in self.genre_widgets if self.genre_widgets[genre][1].get()]
        print(f'The chosen genres are: {chosen_genres}')

        # account for the user misclicking, and entering invalid input (no choice)
        if len(chosen_genres) == 0:
            return

        # clear the initial setup widgets
        for genre in self.genre_widgets:
            self.genre_widgets[genre][0].destroy()
        for init_widget in self.init_widgets:
            init_widget.destroy()

        run_book_network = rb.RunBookNetwork(chosen_genres)
        BookGUI(self.root, run_book_network)


class BookGUI:
    """The class running the main GUI interactions between the client and the
    RunBookNetwork instance.

    Instance Attributes:
    - rbn:
        The instance of RunBookNetwork that will be used in this GUI to recommend books to the client
    - selection_type:
        A variable representing the selection method that should be used to recommend a book to the user, should the
        user desire to do so
    - displayed_books:
        A dictionary mapping book IDs to a list of the labels current displaying that book on the interface
    - mainframe:
        The frame upon which all the widgets are rendered.
    - preferences:
        The 3 variables that contain the client's selection of whether they like the book or not
    - client_liked:
        A list of the names of the books that the client liked
    - client_disliked:
        A list of the names of the books that the client disliked
    - book_labels:
        A list of the Label objects representing the books the client rated already
    """
    rbn: rb.RunBookNetwork
    selection_type: StringVar
    displayed_books: list[tuple[bg.BookID, list[Widget]]]
    mainframe: Frame
    preferences: list[StringVar]
    client_liked: list[str]
    client_disliked: list[str]
    book_labels: list[Label]

    def __init__(self, root: Tk, rbn: rb.RunBookNetwork) -> None:
        self.rbn = rbn
        self.displayed_books = []
        self.preferences = []
        self.client_disliked = []
        self.client_liked = []
        self.book_labels = []

        # define the main frame, 3px padding on left and right, 12px on top and bottom
        self.mainframe = ttk.Frame(root, padding='3 3 12 12')
        self.mainframe.grid(column=0, row=0, sticky=N)

        # split the frame into 6 columns of equal weight (width)
        for i in range(0, 5):
            root.columnconfigure(i, weight=1)

        # set the first row of the frame as double the weight of other rows (the height)
        root.rowconfigure(0, weight=2)
        for i in range(1, 20):
            root.rowconfigure(i, weight=1)
        # images go in this row, so we want to make it extra tall (-> make weight=3)
        root.rowconfigure(5, weight=3)

        # create the main labels:
        liked_lbl = ttk.Label(self.mainframe, text='Liked Books:')
        liked_lbl.grid(column=4, row=0, padx=50)
        liked_lbl['foreground'] = 'green'
        disliked_lbl = ttk.Label(self.mainframe, text='Disliked Books:')
        disliked_lbl.grid(column=0, row=0, padx=50)
        disliked_lbl['foreground'] = 'red'
        select_lbl = ttk.Label(self.mainframe, text='Select a Method of Recommending Books:')
        select_lbl.grid(column=2, row=0)

        # create the input for the book selection method (random, popularity, rating) using radio button widgets
        self.selection_type = StringVar(value="no_choice")

        # save the input widgets to a dictionary
        radio_buttons = {}
        selection_types = ['Random', 'Rating', 'Popularity']
        i = 1
        # create one radio button per selection type
        for selection in selection_types:
            radio_buttons[selection.lower()] = ttk.Radiobutton(self.mainframe, text=selection,
                                                               variable=self.selection_type, value=selection.lower())
            radio_buttons[selection.lower()].grid(column=i, row=1)
            i += 1

        # finally, create the button that can be used to start recommending books
        recommend_btn = ttk.Button(self.mainframe, text='Recommend!', command=self.recommend)
        recommend_btn.grid(column=2, row=2, pady=3)

    def clear_books(self) -> None:
        """Clears the books which are displayed by the "recommend" function.
        """
        for widgets in self.displayed_books:
            for widget in widgets[1]:
                widget.destroy()
        self.preferences = []
        self.displayed_books = []

    def render_books(self) -> None:
        """Displays the books the client has already rated like/dislike
        """
        for label in self.book_labels:
            label.destroy()

        # render liked books
        for i in range(0, len(self.client_liked)):
            liked = ttk.Label(self.mainframe, text=self.client_liked[i])
            liked.grid(column=4, row=1 + i, padx=3, pady=5)
            liked['wraplength'] = 150
            liked['foreground'] = 'green'
            self.book_labels.append(liked)
        # render disliked
        for i in range(0, len(self.client_disliked)):
            disliked = ttk.Label(self.mainframe, text=self.client_disliked[i])
            disliked.grid(column=0, row=1 + i, padx=3, pady=5)
            disliked['wraplength'] = 150
            disliked['foreground'] = 'red'
            self.book_labels.append(disliked)

    def update_network(self) -> None:
        """Handles the updating of the network in accordance with the books disliked by the client.
        """
        # get which books were liked/disliked from self.preferences and self.displayed_books
        liked = []
        disliked = []
        for i in range(0, 3):
            if self.preferences[i].get() == 'Like':
                liked.append(self.displayed_books[i][0])
            elif self.preferences[i].get() == 'Dislike':
                disliked.append(self.displayed_books[i][0])

        dissimilar_users = self.rbn.book_network.prune(disliked)
        print(f'Dissimilar Users: {dissimilar_users}')

        liked_names = [self.rbn.all_books[b_id]['title'] for b_id in liked]
        disliked_names = [self.rbn.all_books[b_id]['title'] for b_id in disliked]
        print(f'Disliked Books: {disliked_names}')
        print(f"Disliked Books' IDs: {disliked}")
        print(f'Liked Books: {liked_names}')
        print(f"Liked Books' IDs: {liked}")

        self.client_liked.extend(liked_names)
        self.client_disliked.extend(disliked_names)
        self.clear_books()
        self.render_books()

    def recommend(self) -> None:
        """Handles the recommending of the books, by using the RunBookNetwork instance in concert with GUI methods.
        """
        print('Recommending books...')
        # in the event of the user clicking the button before selection a recommending method
        if self.selection_type.get() == 'no_choice':
            return None

        # use the RunBookNetwork instance to return recommended books based on the selection type
        else:
            # first clear the previously displayed items
            self.clear_books()

            # use the RunBookNetwork instance to get the recommended books based on whichever ranking metric
            book_ids = self.rbn.get_recommended_books(self.selection_type.get())

            # collect the metadata of the returned books for use in displaying
            books = {}
            for b_id in book_ids:
                book_data = self.rbn.all_books[b_id]
                # get the book's rating and popularity as according to the book graph
                bg_rating = float(self.rbn.book_network.books[b_id].rating)
                bg_popularity = len(self.rbn.book_network.books[b_id].connected)

                books[b_id] = (book_data['title'], bg_rating, book_data['image_url'], bg_popularity)

            # display the books
            i = 1
            for b_id in books:
                book = books[b_id]

                title = ttk.Label(self.mainframe, text=book[0])
                title.grid(column=i, row=3, padx=3, pady=3)
                rating = ttk.Label(self.mainframe, text=f'Rating: {round(book[1], 1)}')
                rating.grid(column=i, row=4, padx=3, pady=3)
                popularity = ttk.Label(self.mainframe, text=f'Popularity: {book[3]}')
                popularity.grid(column=i, row=6, padx=3, pady=3)

                # get the image data from the url with urllib
                with urlopen(book[2]) as img_f:
                    img = img_f.read()
                # display the cover
                cover_img = ImageTk.PhotoImage(data=img)
                cover = ttk.Label(self.mainframe, image=cover_img)
                cover.image = cover_img
                cover.grid(column=i, row=5)

                # update the currently displayed books
                self.displayed_books.append((b_id,[title, rating, cover, popularity]))

                # create the two Like/Dislike radio buttons per book
                choice = StringVar(value='no_choice')
                preferences = ['Like', 'Dislike']
                c = 7
                for preference in preferences:
                    like_dislike = ttk.Radiobutton(self.mainframe, text=preference, variable=choice, value=preference)
                    like_dislike.grid(column=i, row=c, padx=3, pady=3)
                    self.displayed_books[i - 1][1].append(like_dislike)
                    c += 1
                # update self.preferences
                self.preferences.append(choice)
                i += 1

            # finally, add a button that will update the network in accordance with the user's preferences
            update_preferences = ttk.Button(self.mainframe, text='Update Preferences!', command=self.update_network)
            update_preferences.grid(column=2, row=10, padx=3, pady=3)
            # so that it also gets deleted in self.clear_books() calls:
            self.displayed_books[2][1].append(update_preferences)


root = Tk()
BookSetup(root)
root.mainloop()
