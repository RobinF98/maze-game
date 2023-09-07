# Write your code to expect a terminal of 80 characters wide and 24 rows high
import curses as c
import random
import sys
from curses import wrapper
from time import sleep
from pprint import pprint

ROWS = 24
COLS = 80

def build_map(height, width, fill_percent):
  """
  Returns a 2d array height x width with 1's on the border and a random weighted
  fill of 1's for wall and 0's for open space
  Args:
  height (int): Map height
  width (int): Map width
  fill_percent (float): Percentage of map area that is 1's (or wall)

  Returns:
  map (list): Map 2D list
  """
  map = [random.choices([0, 1], [1 - fill_percent, fill_percent], k=width)
       for x in range(height)]  # fills map grid with 1's and 0's, using fill_percent to determine number of 1's

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
    map (list): Map 2D list
    colors (list): The list of color pairs to be used in the drawing
  """
  # color_map = {0:}
  for row in range(len(map)):
    for col in range(len(map[row])):
      screen.addch(row, col, " ", colors[map[row][col]])


def smooth_map(map):
  """
  Uses cellular automota algorithm to smooth the map and make it more "cave-like"
  Args:
    map (list): Map 2D list
  """
  new_map = [[1]*len(map[0]) for row in range(len(map))]
  for row in range(len(map)):
    for col in range(len(map[0])):
      wall_neighbours = count_neighbours(map, row, col, 1)
      if wall_neighbours >= 4:
        new_map[row][col] = 1
      elif wall_neighbours < 4:
        # print(f"neighbours = {wall_neighbours}")
        new_map[row][col] = 0
      # print(f"row: {row}, col: {col}, neighbours: {wall_neighbours}")
  #     new_map[row][col] = wall_neighbours
  #   # pprint(new_map)
  #   print(new_map[row])

  # print()
  # pprint(new_map)
  # print()
  # pprint(map)
  return new_map


# TEST

test_map = [[1, 2, 3, 1, 1, 1],
            [4, 1, 5, 1, 1, 1],
            [6, 7, 8, 1, 1, 1],
            [1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1]]


# TEST
def count_neighbours(map, row, col, type):
  """
  Counts number of tiles neighbouring map[row][col] of type "type" (wall or space)
  Args:
    map (_list_): Map 2D list
    row (int): Tile row index
    col (int): Tile column index
type (int): 1 or 0, wall or space

  Returns:
    count (int): Count of neighbouring tiles of type "type"
  """
  count = 0
  # range functions ends at end value - 1
  for neighbour_row in range(row - 1, row + 2):
    for neighbour_col in range(col - 1, col + 2):
      if neighbour_row != row or neighbour_col != col:  # Don't check the current tile, only neighbouring tiles
        # Only check neighbours of interior tiles
        if neighbour_col >= 0 and neighbour_col < len(map[0]) and neighbour_row >= 0 and neighbour_row < len(map):
          # print(map[neighbour_row][neighbour_col])
          if map[neighbour_row][neighbour_col] == type:
            count += 1
  return count


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

  map = build_map(ROWS-1, COLS, float(sys.argv[1]))
  
  for ind in range(2):
    map = smooth_map(map)
  draw_map(stdscr, map, colors)

  stdscr.getch()  # Gets user keystroke - waits for this before exiting


wrapper(main)


### testing###
# map = build_map(10, 10, float(sys.argv[1]))
# pprint(map)
# print()
# pprint(smooth_map(map))
# print(f"count i s: {count_neighbours(test_map,1,4,1)}")
