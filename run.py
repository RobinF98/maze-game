# Write your code to expect a terminal of 80 characters wide and 24 rows high
import curses as c
import random
# import sys
from curses import wrapper
from time import sleep
from pprint import pprint

ROWS = 24
COLS = 80
ESC = 27
ENTER = 10

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


def draw_map(screen, map: list[list[int]], colors:dict):
  """
  Draws the map "map" on the screen "screen", using color pairs found in the colors list
  Args:
    screen (window): The window on which the map is drawn
    map (list): Map 2D list
    colors (dict): The dict of color pairs to be used in the drawing
  """
  # color_map = {0:}
  for row in range(len(map)):
    for col in range(len(map[row])):
      screen.addch(row, col, " ", list(colors.values())[map[row][col]])

def smooth_map(map: list[list[int]]):
  """
  Uses cellular automota algorithm to smooth the map and make it more "cave-like"
  Args:
    map (list): Map 2D list
  Returns:
    new_map (list): Map 2D list
  """
  new_map = [[1]*len(map[0]) for row in range(len(map))]
  for row in range(len(map)):
    for col in range(len(map[0])):
      wall_neighbours = count_neighbours(map, row, col, 1)
      if wall_neighbours >= 4:
        new_map[row][col] = 1
      elif wall_neighbours < 4:
        new_map[row][col] = 0
        
  return new_map

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
          if map[neighbour_row][neighbour_col] == type:
            count += 1
        else:
          count += 1
  return count

def spawn_bear(map, x_limit):
  """
  Spawns a bear for the player to interact with
  Args:
      map (_list_): Map 2D list
      x_limit (_int_): X coord limit for spawn location
  """
  # y coord offset from horizontal map boundaries
  random_y = random.randint(3,ROWS - 3)

  # loop through subsection of map within rightmost wall and x_limit and along random_y
  # for coord in range(158 , 159 - x_limit, -1):
  #   if map[10][coord] == 0:
  #     map[10][coord] = 2
  #     break
  map[20][len(map[0]) - 10] = 2

  #shortcut ---- DELETE THIS THISNRIHSWIOHASOFIHSqwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwdwqdqwdqwdqwdqwdqwdqwdqdwqd
  for i in range(1,len(map[20])):
    map[15][i] = 0
  #asdddddwqeeeddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd

  return map

def inventory():
  inv_win = c.newwin(1,60,24,0)
  inv_win.nodelay(True)
  inv_win.addstr("Inventory:")
  inv_win.refresh
  inv_win.getch()

def pause_menu(screen):
  """
  Creates Pause menu window above main game, with various game options
  """
  pause_win = c.newwin(18,60,3,10)
  pause_win.border(0,0,0,0,0,0,0,0)
  pause_win.addstr(2, 24,"GAME PAUSED")

  pause_win.refresh()
  pause_win.keypad(True)
  pause_win.nodelay(True)
  options = ["Resume", "Help","Exit"]
  highlight = 0
  while True:
    key = pause_win.getch()
    if key == ESC: 
      break
    # highlight options
    if key == c.KEY_DOWN:
      highlight = (highlight + 1)%4

    if key == c.KEY_UP:
      highlight = (highlight - 1) % 3  
    
    if key == ord(" ") or key == ENTER:
      match highlight:
        case 0: # Resume
          break
        case 1: # Help
          pause_win.clear()
          pause_win.noutrefresh()
          help_menu(screen, pause_win) # TODO: ADD HELP SCREEN
          break
        case 2: # Exit
          del pause_win
          c.endwin()
          print("Thanks for playing!")
          break
    
    # Print and highlight selected option
    for index, option in enumerate(options):
      if index == highlight:
        pause_win.attron(c.A_REVERSE)
        pause_win.addstr(6 + 3 * index, int(30 - len(option) / 2), f"{option}")
        pause_win.attroff(c.A_REVERSE)
      else:
        # Add strings in rough center of window
        pause_win.addstr(6 + 3 * index, int(30 - len(option) / 2), f"{option}")
    pause_win.refresh()

def help_menu(screen):
  """
  Displays Help Menu information window
  """
  help_win = c.newwin(18,60,3,10)
  help_win.border()
  
  help_win.addstr(2, 28,"HELP")
  help_list = [
              " ",
              "• Walk around using the arrow keys",
              "• Interact using 'E'",
              "• Access inventory using 'I'",
              "• Explore the map, if you get stuck", 
              "  or reach a dead end, try reloading the game",
              "• Press any key to go back",
               ]
  for index, str in enumerate(help_list):
    help_win.addstr(3 + 2 * index, 9, f"{str}")
  help_win.refresh()
  key = help_win.getch()
  if key  != -1:
    # del help_win
    # pause_win.refresh()
    pause_menu(screen)

def bear_dialogue():
  bear_win = c.newwin(10,80,13,0)
  bear_win.border()
  dialogue = [
    "Baby Bear: BOooo HOOooo :(",
    "You: Hey hey, what's the matter? ö",
    "Baby Bear: Goldilocks stole my porridge, and I'm so hungwy :(",
    "Press E to console",
    "Baby Bear is unconsolable" 
  ]

  # print dialogue line by line on each key press
  for index, str in enumerate(dialogue):
    if index == 2:
      break
    bear_win.addstr(2 + index, 2, f"{dialogue[index]}")
    bear_win.refresh()
    key = bear_win.getch()

  # TODO: fix inf loop inconsolable, clear screen after each Inconsolable, exit dialogue after 3 inconsolable's, prevent re running dialogue after exit (with call to quest() or a bool or something)
  while True:
    key = bear_win.getch()
    counter = 0
    bear_win.addstr(6, 2, f"{dialogue[3]}")
    if key == ord("e"):
      bear_win.clear()
      bear_win.addstr(2, 2, f"{dialogue[4]}")
      bear_win.getch()
      counter += 1
    if counter == 3:
      break

  

def main(stdscr):
  """
  Initializes curses window and settings, and runs all functions.
  """
  stdscr = c.initscr()  # Initialize curses module, returns window
  c.noecho()  # Prevents keystrokes being echoed on screen
  c.cbreak()  # Allows keystrokes to be read instantly without needing to hit return
  # c.curs_set(0)  # Hides flashing cursor
  c.leaveok(True)
  stdscr.keypad(True)  # Allows screen to read keystrokes
  stdscr.nodelay(True)
  # color pairs
  c.init_pair(1, c.COLOR_WHITE, c.COLOR_BLACK)
  c.init_pair(2, c.COLOR_BLACK, c.COLOR_WHITE)
  c.init_pair(3, c.COLOR_WHITE, c.COLOR_BLUE)
  c.init_pair(4, c.COLOR_WHITE, c.COLOR_RED)
  colors = {
            "w_black": c.color_pair(1),
            "black_w": c.color_pair(2),
            "w_blue": c.color_pair(3),
            "w_red": c.color_pair(4)
            }

  map = build_map(c.LINES * 2, (c.COLS - 1) * 2, 0.35)
  
  # set player spawn point to empty space
  for row in range(23,26):
    for col in range(39,42):  
      map[row][col] = 0
  
  pad = c.newpad(c.LINES * 2, c.COLS * 2)
  
  # Smooth the random map into something cave shaped
  for ind in range(7):
    map = smooth_map(map)

  map = spawn_bear(map, 10)
  # Initial screen position
  x, y = 0, 12
  
  draw_map(pad, map, colors)
  inventory()
  while True:
    # main movement
    key = stdscr.getch()
    if key == ESC:
      pause_menu(stdscr)
    
    if key == ord("q") or c.isendwin(): # TODO: Remove "q" from this bit
      break

    # Check if player is near bear:
    if x + 40 - 1 == len(map[10]) - 10:
      bear_dialogue()

    if key == c.KEY_LEFT:
      # Set previous player position to open space
      pad.addstr(y + 12, x + 40, " ")
      # Detect if map tile is wall
      if map[y+12][x+40-1] != 1:
        x -= 1
    if key == c.KEY_RIGHT:
      pad.addstr(y + 12, x + 40, " ")
      if map[y+12][x+40+1] != 1:
        x += 1
    if key == c.KEY_UP:
      pad.addstr(y+12, x + 40, " ")
      if map[y+12-1][x+40] != 1:
        y -= 1
    if key == c.KEY_DOWN:
      pad.addstr(y+12, x + 40, " ")
      if map[y+12+1][x+40] != 1:
        y += 1

    # Update player position    
    pad.addstr(y + 12,x + 40, "@")
    pad.refresh(y, x, 0,0 ,23, 80)
    # pad.refresh(y, x, 0, 0, 40, 155)

wrapper(main)
