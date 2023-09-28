# Write your code to expect a terminal of 80 characters wide and 24 rows high
import curses as c
import random
import emoji

from curses import wrapper
from time import sleep
from pprint import pprint

ROWS = 24
COLS = 80
ESC = 27
ENTER = 10
BEAR_X = 41
BEAR_Y = 20


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
        map (_list_): Map 2D list
        x_limit (_int_): X coord limit for spawn location
    """
    # y coord offset from horizontal map boundaries
    random_y = random.randint(3, ROWS - 3)

    # loop through subsection of map within rightmost wall and x_limit and along random_y
    # for coord in range(158 , 159 - x_limit, -1):
    #   if map[10][coord] == 0:
    #     map[10][coord] = 2
    #     break
    map[BEAR_Y][BEAR_X] = 2
    # Bear emoji width is 2, set to 4 to allow for collision detection in main
    map[BEAR_Y][BEAR_X + 1] = 4
    map[BEAR_Y][BEAR_X - 1] = 4

    # shortcut ---- DELETE THIS THISNRIHSWIOHASOFIHSqwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwdwqdqwdqwdqwdqwdqwdqwdqdwqd
    for i in range(1, len(map[20]) - 1):
        map[15][i] = 0
    # asdddddwqeeeddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd

    return map


def inventory():
    global inv_win
    inv_win = c.newwin(1, 60, 23, 0)
    inv_win.nodelay(True)
    inv_win.addstr("Inventory:")
    inv_win.refresh
    inv_win.getch()
    inv = {"rock": 0, "porridge": 0}
    return inv


def update_inventory(item: str, inv: dict):
    new_inventory = inv[item] + 1  # .get(item,-1) + 1
    inv.update({item: new_inventory})
    inv_win.addstr(0, 30, f"{item}: {new_inventory}")
    inv_win.refresh()
    return inv


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
            highlight = (highlight + 1) % 4

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
    counter = 0
    # TODO: fix inf loop inconsolable, clear screen after each Inconsolable, exit dialogue after 3 inconsolable's, prevent re running dialogue after exit (with call to quest() or a bool or something)

    key = bear_win.getch()

    bear_win.addstr(6, 2, f"{dialogue[3]}")
    if key == ord("e") or key == ord("E"):
        bear_win.clear()
        bear_win.addstr(2, 2, f"{dialogue[4]}")
        bear_win.getch()
        counter += 1

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
        "w_blue": c.color_pair(3),
        "w_black_rock": c.color_pair(1),
        "w_black_bear": c.color_pair(1),
    }

    map = build_map(c.LINES * 2, (c.COLS - 1) * 2, 0.35)

    # set player spawn point to empty space
    for row in range(23, 26):
        for col in range(39, 42):
            map[row][col] = 0

    # set bear spawn point to empty space
    for row in range(BEAR_Y - 1, BEAR_Y + 3):
        for col in range(BEAR_X - 1, BEAR_X + 3):
            map[row][col] = 0

    pad = c.newpad(c.LINES * 2, c.COLS * 2)

    # Smooth the random map into something more cave shaped
    for ind in range(7):
        map = smooth_map(map)

    map = spawn_bear(map, 10)
    map = spawn_rock(map)
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
    update_quest(quest)
    while True:
        # main movement
        key = stdscr.getch()
        if key == ESC:
            pause_menu(stdscr)

        if key == ord("q") or c.isendwin():  # TODO: Remove "q" from this bit
            break

        # Check if player is near bear:
        if x + 40 in range(BEAR_X - 2, BEAR_X + 2) and y + 12 in range(
            BEAR_Y - 1, BEAR_Y + 2
        ):
            if not quest:
                # Interact with bear and add to quest list
                quest = bear_dialogue()
                update_quest(quest)

        if key == c.KEY_LEFT or key == ord("a"):
            # Set previous player position to open space
            pad.addstr(y + 12, x + 40, " ")
            # Detect if map tile is wall or bear or bear adjacent
            # (bear emoji character has a width of 2, so need to check 2 tiles)
            next_tile = map[y + 12][x + 40 - 1]
            if next_tile not in [1, 2, 4]:
                # Detect if next tile is a rock
                if next_tile == 3:
                    inventory = update_inventory(
                        "rock", inventory
                    )  # TODO: Add update inventory function that checks if arg is in inventory items list and increments count
                x -= 1

        if key == c.KEY_RIGHT or key == ord("d"):
            pad.addstr(y + 12, x + 40, " ")
            next_tile = map[y + 12][x + 40 + 1]
            if next_tile not in [1, 2, 4]:
                if next_tile == 3:
                    inventory = update_inventory("rock", inventory)
                x += 1

        if key == c.KEY_UP or key == ord("w"):
            pad.addstr(y + 12, x + 40, " ")
            next_tile = map[y + 12 - 1][x + 40]
            if next_tile not in [1, 2, 4]:
                if next_tile == 3:
                    inventory = update_inventory("rock", inventory)
                y -= 1

        if key == c.KEY_DOWN or key == ord("s"):
            pad.addstr(y + 12, x + 40, " ")
            next_tile = map[y + 12 + 1][x + 40]
            if next_tile not in [1, 2, 4]:
                if next_tile == 3:
                    inventory = update_inventory("rock", inventory)
                y += 1

        # Update player position
        pad.addstr(y + 12, x + 40, "❤")
        pad.refresh(y, x, 0, 0, 22, 60)
        # pad.refresh(y, x, 0, 0, 40, 155)


wrapper(main)
