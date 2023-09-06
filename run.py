# Write your code to expect a terminal of 80 characters wide and 24 rows high
import curses as c
import random
import sys
from curses import wrapper
from time import sleep

def build_map(height, width, fill_percent):
  """
  Returns a 2d array height x width with 1's on the border and a random weighted
  fill of 1's for wall and 0's for open space
  Args:
      height (int): Map height
      width (int): Map width
      fill_percent (float): Percentage of map area that is 1's (or wall)

  Returns:
      _type_: _description_
  """
  map = [random.choices([0, 1], [1 - fill_percent, fill_percent], k=width)
          for x in range(height)] # fills map grid with 1's and 0's, using fill_percent to determine number of 1's
  
  # Set map border to 1's
  map[0] = [1] * width
  map[height - 1] = [1] * width
  for ind in range(1, height - 1):
      map[ind][0] = 1
      map[ind][width - 1] = 1
  
  return map

def draw_map(screen, map, colors):
  """
  Draws the map "map" on the screen "screen", using color pairs found in the colors list
  Args:
      screen (window): The window on which the map is drawn
      map (list): the 2d list that is drawn
      colors (list): The list of color pairs to be used in the drawing
  """
  # color_map = {0:}
  for row in range(len(map)):
      for col in range(len(map[row])):
          screen.addch(row, col, " ", colors[map[row][col]])

def main(stdscr):
    """
    Initializes curses window and settings, and runs all functions.
    """
    stdscr = c.initscr()  # Initialize curses module, returns window
    c.noecho()  # Prevents keystrokes being echoed on screen
    c.cbreak()  # Allows keystrokes to be read instantly without needing to hit return
    c.curs_set(False)  # Hides flashing cursor
    stdscr.keypad(True)  # Allows screen to read keystrokes
    stdscr.clear()
    stdscr.refresh()

    # color pairs
    c.init_pair(1, c.COLOR_RED, c.COLOR_BLACK)
    c.init_pair(2, c.COLOR_RED, c.COLOR_WHITE)
    colors = [c.color_pair(1), c.color_pair(2)]

    map = build_map(c.LINES-1, c.COLS, float(sys.argv[1]))
    draw_map(stdscr, map, colors)
    
    stdscr.getch()  # Gets user keystroke - waits for this befroe exiting


wrapper(main)
