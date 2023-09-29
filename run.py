# Write your code to expect a terminal of 80 characters wide and 24 rows high
import curses as c
import random
import emoji

from curses import wrapper
from time import sleep
from pprint import pprint

ROWS = 75
COLS = 250
ESC = 27
ENTER = 10
# Bear & Goldilocks spawn coordinates
BEAR_X = random.randrange(200, 240)
BEAR_Y = random.randrange(5, 65)
GOLDILOCKS_X = 40
# TODO Okay sooooo goldilocks will be on screen form game start, spawning near player to promote map exploration.
# SHe will be hidden by a window that contains wall blocks. after picking up quest and searching for g-locks, #
# player will wander near enough to the hiding spot and see the window disappear, with the pad refreshing instantly.
# Goldilocks will be visible and the player can approach
GOLDILOCKS_Y = 24


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
    map = [
        random.choices([0, 1], [1 - fill_percent, fill_percent], k=width)
        for x in range(height)
    ]  # fills map grid with 1's and 0's, using fill_percent to determine number of 1's

    # Set map border to 1's
    map[0] = [1] * width
    map[height - 1] = [1] * width
    for ind in range(1, height - 1):
        map[ind][0] = 1
        map[ind][width - 1] = 1

    return map


def draw_map(screen, map: list[list[int]], colors: dict):
    """
    Draws the map "map" on the screen "screen", using color pairs
    found in the colors list
    Args:
      screen (window): The window on which the map is drawn
      map (list): Map 2D list
      colors (dict): The dict of color pairs to be used in the drawing
    """

    for row in range(len(map)):
        for col in range(len(map[row])):
            if map[row][col] == 3:
                screen.addch(row, col, "•", list(colors.values())[map[row][col]])
            else:
                screen.addch(row, col, " ", list(colors.values())[map[row][col]])
    # add bear and bear adjacent tile to
    screen.addstr(BEAR_Y, BEAR_X, "🐻")


def smooth_map(map: list[list[int]]):
    """
    Uses cellular automota algorithm to smooth the map and make it more "cave-like"
    Args:
      map (list): Map 2D list
    Returns:
      new_map (list): Map 2D list
    """
    new_map = [[1] * len(map[0]) for row in range(len(map))]
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
        map (list): Map 2D list
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
            if (
                neighbour_row != row or neighbour_col != col
            ):  # Don't check the current tile, only neighbouring tiles
                # Only check neighbours of interior tiles
                if (
                    neighbour_col >= 0
                    and neighbour_col < len(map[0])
                    and neighbour_row >= 0
                    and neighbour_row < len(map)
                ):
                    if map[neighbour_row][neighbour_col] == type:
                        count += 1
                else:
                    count += 1
    return count


def spawn_bear(map, x_limit):
    """
    Spawns a bear for the player to interact with
    Args:
        map (list): Map 2D list
        x_limit (int): X coord limit for spawn location
    Returns:
        Returns:
        map (2D list): The 2D list containing the map
    """
    map[BEAR_Y][BEAR_X] = 2
    # Bear emoji width is 2 units, set adjacent cells to 4 to prevent player/bear
    #  overlap
    map[BEAR_Y][BEAR_X + 1] = 4
    map[BEAR_Y][BEAR_X - 1] = 4

    return map


def spawn_goldilocks(map: list[list[int]]):
    """
    Spawns goldilocks and porridge by adding them to the map list
    Args:
        map (2D list): The 2D list containing the map
    Returns:
        map (2D list): The 2D list containing the map
    """
    # Goldilocks adjacent cells (player can't move onto cell = 5)
    for y in range(22, 26):
        for x in range(39, 42):
            map[y][x] = 5

    # goldilocks & porridge placeholder
    map[25][40] = 2
    map[23][40] = 2

    return map


def inventory():
    global inv_win
    inv_win = c.newwin(1, 40, 23, 0)
    inv_win.nodelay(True)
    inv_win.addstr("Inventory:")
    inv_win.refresh
    inv_win.getch()
    inv = {"rock": 0, "porridge": 0}
    return inv


def update_inventory(item: str, inv: dict):
    new_inventory = inv[item] + 1  # .get(item,-1) + 1
    inv.update({item: new_inventory})
    inv_win.addstr(0, 10, f"{item}: {new_inventory}")
    inv_win.refresh()
    return inv


def coords(x: int, y: int):
    coords_win = c.newwin(1, 19, 23, 41)
    coords_win.addstr(0, 1, f"x:{x}, y:{y}")
    coords_win.refresh()


def show_inventory(inv: dict):
    """
    Displays window with current inventory and allows user to scroll through inventory
    Args:
        inv (dict): The current player inventory
    """
    inv_disp_win = c.newwin(18, 60, 3, 10)
    inv_disp_win.border()
    inv_disp_win.addstr(2, 25, "INVENTORY")

    # Print items in inv dict
    for index, item in enumerate(inv):
        if inv[item] > 0:
            inv_disp_win.addstr(5 + index * 2, 7, f"{item}: {inv[item]}")
    inv_disp_win.refresh()

    inv_disp_win.getch()


def pause_menu(screen):
    """
    Creates Pause menu window above main game, with various game options
    """
    pause_win = c.newwin(18, 60, 3, 10)
    pause_win.border(0, 0, 0, 0, 0, 0, 0, 0)
    pause_win.addstr(2, 24, "GAME PAUSED")

    pause_win.refresh()
    pause_win.keypad(True)
    pause_win.nodelay(True)
    options = ["Resume", "Help", "Exit"]
    highlight = 0
    key = 0

    while True:
        key = pause_win.getch()
        if key == ESC:
            break
        # highlight options
        if key == c.KEY_DOWN or key == ord("s"):
            highlight = (highlight + 1) % 3

        if key == c.KEY_UP or key == ord("w"):
            highlight = (highlight - 1) % 3

        if key == ord(" ") or key == ENTER:
            match highlight:
                case 0:  # Resume
                    break
                case 1:  # Help
                    pause_win.clear()
                    pause_win.noutrefresh()
                    help_menu(screen)
                    break
                case 2:  # Exit
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
                # Add strings roughly in the center of the window
                pause_win.addstr(6 + 3 * index, int(30 - len(option) / 2), f"{option}")
        pause_win.refresh()


def help_menu(screen):
    """
    Displays Help Menu information window
    """
    help_win = c.newwin(18, 60, 3, 10)
    help_win.border()

    help_win.addstr(2, 28, "HELP")
    help_list = [
        " ",
        "• Walk around using the arrow keys or wasd",
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
    if key != -1:
        # del help_win
        # pause_win.refresh()
        pause_menu(screen)


def bear_dialogue():
    bear_win = c.newwin(10, 79, 13, 0)
    bear_win.border()
    dialogue = [
        "Baby Bear: BOooo HOOooo :(",
        "You: Hey hey, what's the matter? ö",
        "Baby Bear: Goldilocks stole my porridge, and I'm so hungwy :(",
        "Press E to console",
        "Baby Bear is unconsolable",
    ]

    # print dialogue line by line on each key press
    for index, str in enumerate(dialogue):
        if index == 3:
            break
        bear_win.addstr(2 + index, 2, f"{dialogue[index]}")
        bear_win.refresh()
        key = bear_win.getch()

    bear_win.addstr(6, 2, f"{dialogue[3]}")

    while True:
        key = bear_win.getch()
        if key == ord("e") or key == ord("E"):
            bear_win.clear()
            bear_win.border()
            bear_win.addstr(2, 2, f"{dialogue[4]}")
            bear_win.refresh()
            bear_win.getch()
            break
        else:
            pass

    return True


def update_quest(quest: bool):
    """
    Updates and displays current quest in quest window

    Args:
        quest (bool): Bool indicating whether a quest is in progress
    """
    quest_win = c.newwin(23, 19, 0, 61)
    quest_win.border()

    quest_win.addstr(2, 7, "QUESTS")

    if quest:
        quest_win.addstr(4, 1, "• Get the")
        quest_win.addstr(5, 1, "  porridge from")
        quest_win.addstr(6, 1, "  Goldilocks")
    else:
        pass
    quest_win.refresh()


def spawn_rock(map: list[list[int]]):
    """
    Spawns rocks in locations around the map
    Args:
        map (list): 2D list containing the map
    """
    # Count neighbour tiles
    for row in range(len(map)):
        for col in range(len(map[0])):
            if map[row][col] == 0:
                wall_neighbours = count_neighbours(map, row, col, 1)
                # for spawning rocks in nooks and crannies
                if wall_neighbours >= 5 and wall_neighbours <= 6:
                    # rock rarity
                    if random.random() < 0.05:
                        map[row][col] = 3
    return map


def main(stdscr):
    """
    Initializes curses window and settings, and runs all functions.
    """
    stdscr = c.initscr()  # Initialize curses module, returns window
    c.noecho()  # Prevents keystrokes being echoed on screen
    c.cbreak()  # Allows keystrokes to be read instantly without needing to hit return
    if hasattr(c, "curs_set"):
        try:
            c.curs_set(0)  # Hide the cursor
        except:
            pass
    stdscr.keypad(True)  # Allows screen to read keystrokes
    stdscr.nodelay(True)  # getch will return -1, not ERR, if no key is pressed
    # color pairs
    c.init_pair(1, c.COLOR_WHITE, c.COLOR_BLACK)
    c.init_pair(2, c.COLOR_BLACK, c.COLOR_WHITE)
    c.init_pair(3, c.COLOR_WHITE, c.COLOR_BLUE)
    colors = {
        "w_black": c.color_pair(1),
        "black_w": c.color_pair(2),
        "w_black_goldilocks": c.color_pair(1),
        "w_black_rock": c.color_pair(1),
        "w_black_bear": c.color_pair(1),
    }

    map = build_map(ROWS, COLS, 0.35)

    # set player spawn point to empty space
    for row in range(22, 27):
        for col in range(38, 43):
            map[row][col] = 0

    # set bear spawn point to empty space
    for row in range(BEAR_Y - 1, BEAR_Y + 3):
        for col in range(BEAR_X - 1, BEAR_X + 3):
            map[row][col] = 0

    pad = c.newpad(ROWS + 1, COLS + 1)

    # Smooth the random map into something more cave shaped
    for ind in range(7):
        map = smooth_map(map)

    map = spawn_bear(map, 10)
    map = spawn_rock(map)
    map = spawn_goldilocks(map)
    # Initial screen position
    x, y = 0, 12
    # Tile that player moves to
    next_tile = 0

    # Draw the map to the pad
    draw_map(pad, map, colors)

    # Set the inventory dictionary
    global inventory
    inventory = inventory()
    quest = False
    # Generate quest window
    update_quest(quest)
    # will be set to 4 after goldilocks is spawned to prevent player/goldilocks
    # overlap:
    goldilocks = 1
    while True:
        # main movement
        key = stdscr.getch()
        if key != -1:
            if key == ESC:
                pause_menu(stdscr)
            # Exits game if endwin has been called (from pause_menu)
            if key == ord("q") or c.isendwin():  # TODO: Remove "q" from this bit
                break
            else:
                # Refresh quest window after pause to remove pause window overlap
                update_quest(quest)

            # Check if player is near bear:
            if x + 40 in range(BEAR_X - 2, BEAR_X + 3) and y + 12 in range(
                BEAR_Y - 1, BEAR_Y + 2
            ):
                if not quest:
                    # Interact with bear and add to quest list
                    quest = bear_dialogue()
                    update_quest(quest)

            if key == c.KEY_LEFT or key == ord("a"):
                # Set previous player position to open space
                pad.addstr(y + 12, x + 40, " ")
                # Detect if tile is wall/bear/goldilocks/bear adjacent
                # (bear emoji character has a width of 2, so need to check 2 tiles)
                next_tile = map[y + 12][x + 40 - 1]
                if next_tile not in [1, 2, 4, goldilocks]:
                    # Detect if next tile is a rock
                    if next_tile == 3:
                        inventory = update_inventory("rock", inventory)
                    x -= 1

            if key == c.KEY_RIGHT or key == ord("d"):
                pad.addstr(y + 12, x + 40, " ")
                next_tile = map[y + 12][x + 40 + 1]
                if next_tile not in [1, 2, 4, goldilocks]:
                    if next_tile == 3:
                        inventory = update_inventory("rock", inventory)
                    x += 1

            if key == c.KEY_UP or key == ord("w"):
                pad.addstr(y + 12, x + 40, " ")
                next_tile = map[y + 12 - 1][x + 40]
                if next_tile not in [1, 2, 4, goldilocks]:
                    if next_tile == 3:
                        inventory = update_inventory("rock", inventory)
                    y -= 1

            if key == c.KEY_DOWN or key == ord("s"):
                pad.addstr(y + 12, x + 40, " ")
                next_tile = map[y + 12 + 1][x + 40]
                if next_tile not in [1, 2, 4, goldilocks]:
                    if next_tile == 3:
                        inventory = update_inventory("rock", inventory)
                    y += 1
            if key == ord("i") or key == ord("I"):
                # Show inventory
                show_inventory(inventory)
                # run update quest to ensure quest window displays properly after
                # show_inventory call
                update_quest(quest)
            # Update player position
            pad.addch(y + 12, x + 40, "❤")
            coords(x + 40, y + 12)
            pad.refresh(y, x, 0, 0, 22, 60)
            # pad.refresh(y, x, 0, 0, 40, 155)


wrapper(main)
