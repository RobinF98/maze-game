# Write your code to expect a terminal of 80 characters wide and 24 rows high
import curses as c
import random
import sys
from curses import wrapper
from time import sleep


def main(stdscr):
    """
    Initializes curses window and settings, and runs all functions.
    """
    stdscr = c.initscr()  # Initialize curses main window
    c.noecho()  # Prevents keystrokes being echoed on screen
    c.cbreak()  # Allows keystrokes to be read instantly without needing to hit return
    c.curs_set(False)  # Hides flashing cursor
    stdscr.keypad(True)  # Allows screen to read keystrokes
    stdscr.clear()
    stdscr.refresh()

    stdscr.getch()  # Gets user keystroke - waits for this befroe exiting


wrapper(main)
