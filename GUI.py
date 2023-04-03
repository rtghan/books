from tkinter import *
from tkinter import ttk

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
    """
    rbn: rb.RunBookNetwork
    selection_type: StringVar

    def __init__(self, root: Tk, rbn: rb.RunBookNetwork) -> None:
        self.rbn = rbn

        # # get a bigger window
        # root.geometry('1200x750')

        # define the main frame, 3px padding on left and right, 12px on top and bottom
        mainframe = ttk.Frame(root, padding='3 3 12 12')
        mainframe.grid(column=0, row=0, sticky=N)

        # split the frame into 6 columns of equal weight (width)
        for i in range(0, 5):
            root.columnconfigure(i, weight=1)

        # set the first row of the frame as double the weight of other rows (the height)
        root.rowconfigure(0, weight=2)
        for i in range(1, 5):
            root.rowconfigure(i, weight=1)

        # create the main labels:
        liked_lbl = ttk.Label(mainframe, text='Liked Books:')
        liked_lbl.grid(column=4, row=0, padx=50)
        disliked_lbl = ttk.Label(mainframe, text='Disliked Books:')
        disliked_lbl.grid(column=0, row=0, padx=50)
        select_lbl = ttk.Label(mainframe, text='Select a Method of Recommending Books:')
        select_lbl.grid(column=2, row=0)

        # create the input for the book selection method (random, popularity, rating) using radio button widgets
        self.selection_type = StringVar(value="no_choice")

        # save the input widgets to a dictionary
        radio_buttons = {}
        selection_types = ['Random', 'Rating', 'Popularity']
        i = 1
        # create one radio button per selection type
        for selection in selection_types:
            radio_buttons[selection.lower()] = ttk.Radiobutton(mainframe, text=selection,
                                                               variable=self.selection_type, value=selection.lower())
            radio_buttons[selection.lower()].grid(column=i, row=1)
            i += 1

        # finally, create the button that can be used to start recommending books
        recommend_btn = ttk.Button(mainframe, text='Recommend!', command=self.recommend)
        recommend_btn.grid(column=2, row=2, pady=3)

    def recommend(self) -> None:
        print('do stuff')
root = Tk()
BookSetup(root)
root.mainloop()
