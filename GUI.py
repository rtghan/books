from tkinter import *
from tkinter import ttk

import book_selection as rt
import similar_books_graph as bg
import data_gen


def run():
    """creates a RunBookNetwork instance"""
    runtime = rt.RunBookNetwork(['comics_graphic, fantasy_paranormal'])
    print('hi')


root = Tk()
root.title('Books On Books On Books')

mainframe = ttk.Frame(root, padding='3 3 12 12')
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

ttk.Button(mainframe, text='Genres: Comics & Graphic Novels, Fantasy & Paranormal'
           , command=run).grid(column=3, row=3, sticky=W)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

root.mainloop()
