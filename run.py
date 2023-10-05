import curses as c
import random
import time

ROWS = 75
COLS = 250
ESC = 27
ENTER = 10

# Bear & Goldilocks spawn coordinates
BEAR_X = random.randrange(200, 240)
BEAR_Y = random.randrange(5, 65)
GOLDILOCKS_X = 50
GOLDILOCKS_Y = 30
PORRIDGE_X = 50
PORRIDGE_Y = 28

PLAYER_ICON = "☺"


def build_map(height, width, fill_percent):
    """
    Returns a 2d array height x width with 1's on the border and a random
    weighted fill of 1's for wall and 0's for open space
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
    ]  # fills map grid with 1's and 0's, fill_percent determines number of 1's

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
    found in the colors list. Adds in bear, goldilocks, and porridge avatars
    Args:
      screen (window): The window on which the map is drawn
      map (list): Map 2D list
      colors (dict): The dict of color pairs to be used in the drawing
    """

    for row in range(len(map)):
        for col in range(len(map[row])):
            if map[row][col] == 3:
                screen.addch(row, col, "•",
                             list(colors.values())[map[row][col]])
            else:
                screen.addch(row, col, " ",
                             list(colors.values())[map[row][col]])

    # add avatars and adjacent tiles to map
    screen.addstr(BEAR_Y, BEAR_X, "🐻")
    screen.addstr(GOLDILOCKS_Y, GOLDILOCKS_X, "👧")
    screen.addstr(PORRIDGE_Y, PORRIDGE_X, "🥣")


def smooth_map(map: list[list[int]]):
    """
    Uses cellular automota algorithm to smooth the map and make it
    more "cave-like"
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
      Counts number of tiles neighbouring map[row][col]
      of type "type" (wall or space)
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
    # Bear emoji width is 2 units, set adjacent cells to 4 to prevent
    # player/bear overlap
    map[BEAR_Y][BEAR_X + 1] = 4
    map[BEAR_Y][BEAR_X - 1] = 4

    return map


def spawn_goldilocks(map: list[list[int]]):
    """
    Sets Golidlocks and Porridge area of map to open space
    Args:
        map (2D list): The 2D list containing the map
    Returns:
        map (2D list): The 2D list containing the map
    """
    # reserve open space for goldilocks
    for y in range(GOLDILOCKS_Y - 2, GOLDILOCKS_Y + 1):
        for x in range(GOLDILOCKS_X, GOLDILOCKS_X + 2):
            map[y][x] = 0

    return map


def inventory():
    """
        Initialises new window below main pad to display player
        inventory
    Returns:
        inv (dict): Dict containing items with key: inventory item,
                    and value: item quantity
    """
    global inv_win
    inv_win = c.newwin(1, 40, 23, 0)
    inv_win.nodelay(True)
    inv_win.addstr("Inventory:")
    inv_win.refresh()
    inv_win.getch()
    inv = {"Rock": 0, "Porridge": 0}
    return inv


def update_inventory(item: str, inv: dict):
    """
        Adds qty 1 to item in inventory
    Args:
        item (str): The item being updated
        inv (dict): Inventory dictionary containing item and qty

    Returns:
        _type_: _description_
    """
    new_inventory = inv[item] + 1
    inv.update({item: new_inventory})
    for index, item in enumerate(inv):
        if inv[item] > 0:
            inv_win.addstr(0, 11 + index * 10, f"{item}: {inv[item]}")
    inv_win.refresh()
    return inv


def coords(x: int, y: int):
    """
        Generates and updates coordinate window to keep track of
        player position
    Args:
        x (int): Player X coordinate
        y (int): Player Y coordinate
    """
    coords_win = c.newwin(1, 19, 23, 41)
    coords_win.addstr(0, 1, f"x:{x}, y:{y}")
    coords_win.refresh()


def show_inventory(inv: dict):
    """
    Displays window with current inventory on top of main pad
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


def pause_menu():
    """ Creates Pause menu window above main game, with game options """
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
        if key == c.KEY_DOWN or key == ord("s") or key == ord("S"):
            highlight = (highlight + 1) % 3

        if key == c.KEY_UP or key == ord("w") or key == ord("W"):
            highlight = (highlight - 1) % 3

        if key == ord(" ") or key == ENTER:
            match highlight:
                case 0:  # Resume
                    break
                case 1:  # Help
                    pause_win.clear()
                    pause_win.noutrefresh()
                    help_menu()
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
                pause_win.addstr(6 + 3 * index, int(30 - len(option) / 2),
                                 f"{option}")

                pause_win.attroff(c.A_REVERSE)
            else:
                # Add strings roughly in the center of the window
                pause_win.addstr(6 + 3 * index, int(30 - len(option) / 2),
                                 f"{option}")

        pause_win.refresh()


def help_menu():
    """ Displays Help Menu information window """

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
        pause_menu()


def bear_dialogue():
    """
        Generates window and dialogue with Baby Bear.
    Returns:
        Bool (True): Returns true to set quest variable to true for
        quest initialization
    """
    bear_win = c.newwin(10, 79, 13, 0)
    bear_win.border()
    dialogue = [
        "BOooo HOOooo : 🐻",
        "❤ : Hey hey, what's the matter?",
        "Goldilocks stole my porridge, and I'm so hungwy : 🐻",
        "Press E to console",
        "Baby Bear is unconsolable",
    ]

    # print dialogue line by line on each key press
    for index, str in enumerate(dialogue):
        if index == 3:
            break
        if index == 1:
            bear_win.addstr(2 + index, 2, f"{dialogue[index]}")
        else:
            bear_win.addstr(2 + index, 76 - len(dialogue[index]),
                            f"{dialogue[index]}")
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


def bear_dialogue_win():
    """
        Generates window and dialogue with Baby Bear to give him porridge.
    Returns:
        Bool (True): Returns true to set quest_complete variable to true
    """
    bear_win = c.newwin(10, 79, 13, 0)
    bear_win.border()
    dialogue = [
        "❤ : Hello 🐻, guess what I got you",
        "OMG! I have no idea! What did you get? : 🐻",
        "Press E to give 🥣",
        "Oh, thanks. I'm don't really like porridge anymore : 🐻",
        "Press E to leave 🐻",
        "Ungrateful"
    ]

    # Print dialogue line by line on each key press
    key = 0
    for index, str in enumerate(dialogue):

        if index == 4:
            break

        if index % 2 == 0:
            bear_win.addstr(2 + index, 2, f"{dialogue[index]}")
            key = bear_win.getch()

            if index == 2:
                while True:
                    if key == ord("e") or key == ord("E"):
                        break
                    else:
                        key = bear_win.getch()

        else:
            bear_win.addstr(2 + index, 76 - len(dialogue[index]),
                            f"{dialogue[index]}")
            key = bear_win.getch()

        bear_win.refresh()

    bear_win.addstr(6, 2, f"{dialogue[4]}")

    while True:
        if key == ord("e") or key == ord("E"):
            bear_win.clear()
            bear_win.border()
            bear_win.addstr(2, 2, f"{dialogue[5]}")
            bear_win.refresh()
            bear_win.getch()
            break
        else:
            key = bear_win.getch()


def goldilocks_dialogue():
    """
        Generates window and dialogue with Goldilocks, and runs fight
        function to fight with Goldilocks

    Returns:
        Bool: Bool indicating win or loss in fight_goldilocks()
    """
    gold_win = c.newwin(10, 79, 13, 0)
    gold_win.border()
    dialogue = [
        "STAY AWAY FROM MY PORRIDGE !!! : 👧",
        "❤ : HEY! You scared me",
        "I DON'T CARE. LEAVE ME AND MY PORRIDGE ALONE! : 👧",
        "❤ : That porridge belongs to 🐻, not you!",
        "OH YEAH?? WHAT ARE YOU GOING TO DO ABOUT IT? : 👧",
        "Press E to fight"
    ]

    # print dialogue line by line on each key press
    for index, str in enumerate(dialogue):
        if index % 2 == 0:
            gold_win.addstr(2 + index, 76 - len(dialogue[index]),
                            f"{dialogue[index]}")
        else:
            gold_win.addstr(2 + index, 2, f"{dialogue[index]}")
        gold_win.refresh()
        key = gold_win.getch()

    while True:
        key = gold_win.getch()
        if key == ord("e") or key == ord("E"):
            gold_win.clear()
            return fight_goldilocks()
            break
        else:
            pass


class Projectile():
    """ Class for spawning and updating projectiles for minigame """

    def __init__(self, y, x, speed):
        self.y = y
        self.x = x
        self.speed = speed
        self.active = True

    def update_position(self):
        self.y += self.speed
        return self.y

    def deactivate(self):
        self.active = False


def fight_goldilocks():
    """
        Generates window and logic for bullet dodge style minigame
    Returns:
        (bool): Bool to define win or loss
    """
    width = 60

    fight_win = c.newwin(18, width, 3, 10)
    fight_win.keypad(True)
    fight_win.border()

    win = False
    defeat = False

    # GOLDILOCKS INITIAL POSITION
    goldilocks_x = 1
    goldilocks_y = 1
    goldilocks_health = 3
    goldilocks_hearts = "GOLDILOCKS: ❤ ❤ ❤"
    fight_win.addstr(0, 21, f"{goldilocks_hearts}")

    # PLAYER INITIAL POSITION
    player_x = 30
    player_y = 16
    fight_win.addstr(17, 25, "PLAYER: ❤")

    fight_win.nodelay(True)

    fps = 10  # frames per second for goldilocks and projectile movement
    goldilocks_direction = -1  # initial direction for goldilocks movement
    player_cooldown = 0  # Cooldown for player projectile, to prevent rapidfire
    projectiles = []
    key = 0

    # Main movement:
    goldilocks_cooldown = 0  # Number of iteretions since last projectile
    # fired, to not overwhelm player with projectiles
    time_of_last = time.time()  # Time of last goldilocks movement iteration

    while not win and not defeat:

        # Only move Goldilocks and projectiles every 1/fps seconds
        if time.time() - time_of_last > 1 / fps:

            # Goldilocks Movement
            fight_win.addstr(goldilocks_y, goldilocks_x, "  ")

            # Left / right boundaries
            if goldilocks_x == 57 or goldilocks_x == 1:
                goldilocks_direction *= -1
            goldilocks_x += goldilocks_direction
            fight_win.addstr(goldilocks_y, goldilocks_x, "👧")

            # Fire projectile semi-randomly
            if ((random.randrange(100) > 70 and goldilocks_cooldown > 5) or
                    goldilocks_x == player_x):

                projectiles.append(Projectile(goldilocks_y + 1,
                                   goldilocks_x, 1))
                goldilocks_cooldown = 0

            # Projectile movement
            for projectile in projectiles:
                fight_win.addstr(projectile.y, projectile.x, " ")

                # prevent projectiles updating outside of the fight window
                if projectile.y > 15 or projectile.y < 2:
                    projectile.deactivate()
                    projectiles.remove(projectile)

                else:
                    projectile.update_position()

                    # Different projectiles for goldilocks and player
                    if projectile.speed == 1:
                        # Goldilocks projectile
                        fight_win.addstr(projectile.y, projectile.x, "|")
                    else:
                        # Player projectile
                        fight_win.addstr(projectile.y, projectile.x, "•")

                # Goldilocks hit detection:
                if (projectile.y == goldilocks_y and
                   projectile.x == goldilocks_x):

                    goldilocks_health -= 1

                    if goldilocks_health == 2:
                        goldilocks_hearts = "GOLDILOCKS: ❤ ❤  "

                    if goldilocks_health == 1:
                        goldilocks_hearts = "GOLDILOCKS: ❤    "

                    if goldilocks_health == 0:
                        goldilocks_hearts = "GOLDILOCKS:      "
                        win = True

                    fight_win.addstr(0, 21, f"{goldilocks_hearts}")

                # Player hit detection:
                if projectile.y == player_y and projectile.x == player_x:
                    fight_win.addstr(17, 25, "PLAYER:  ")
                    defeat = True

            goldilocks_cooldown += 1  # Prevent rapid fire
            player_cooldown += 1  # Prevent rapid fire
            time_of_last = time.time()

        key = fight_win.getch()

        # Player movement

        # move left
        if key == c.KEY_LEFT or key == ord("a") or key == ord("A"):
            if player_x != 2:
                fight_win.addstr(player_y, player_x, " ")
                player_x -= 1

        # move right
        if key == c.KEY_RIGHT or key == ord("d") or key == ord("D"):
            if player_x != 58:
                fight_win.addstr(player_y, player_x, " ")
                player_x += 1

        # fire projectile
        if key == ord(" ") and player_cooldown > 5:

            # Spawn player projectile (note negative speed)
            projectiles.append(Projectile(player_y - 1, player_x, -1))
            player_cooldown = 0

        fight_win.addstr(player_y, player_x, f"{PLAYER_ICON}")

        fight_win.refresh()

        if win or key == ord("m"):  #ASDDDDDDDDDDDDDDDDDDDDDDDDDDDDWERWIJOIJWERIJWDJOJOROJOJJIJOJOJIJOJUIJOJOJIJOJOJIJOJIJOJIJIOJOJIJOJIJOJIJSDF
            fight_win.nodelay(False)
            c.flash()
            time.sleep(0.2)
            c.flash()
            win_win = fight_win.derwin(7, 32, 5, 14)
            win_win.border()
            win_win.addstr(3, 5, "GOLDILOCKS 👧 DEFEATED")
            win_win.addstr(5, 5, "Press E to keep moving")
            key = win_win.getch()
            while True:
                if key == ord("e") or key == ord("E"):
                    break
                key = win_win.getch()

            return True  # Continue game
            break

        if defeat or key == ord("p"):  #ASDDDDDDDDDDDDDDDDDDDDDDDDDDDDWERWIJOIJWERIJWDJOJOROJOJJIJOJOJIJOJUIJOJOJIJOJOJIJOJIJOJIJIOJOJIJOJIJOJIJSDF
            fight_win.nodelay(False)
            c.flash()
            time.sleep(0.2)
            c.flash()
            defeat_win = fight_win.derwin(7, 32, 5, 14)
            defeat_win.border()
            defeat_win.addstr(3, 12, "YOU DIED")
            defeat_win.addstr(5, 8, "Press E to leave")
            key = defeat_win.getch()
            while True:
                if key == ord("e") or key == ord("E"):
                    break
                key = defeat_win.getch()

            return False  # Game over
            break


def update_quest(quest: bool, quest_complete: bool):
    """
    Updates and displays current quest in quest window

    Args:
        quest (bool): Bool indicating whether a quest has started
        quest_complete (bool): Bool indicating quest completed
    """
    quest_win = c.newwin(23, 19, 0, 61)
    quest_win.border()

    quest_win.addstr(2, 7, "QUESTS")

    if quest:
        quest_win.addstr(4, 1, "• Get the")
        quest_win.addstr(5, 1, "  porridge from")
        quest_win.addstr(6, 1, "  Goldilocks")

    elif quest_complete:
        quest_win.addstr(4, 1, "• All")
        quest_win.addstr(5, 1, "  quests")
        quest_win.addstr(6, 1, "  complete")

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
    c.cbreak()  # Read keystrokes instantly without needing to hit return

    # Try to hide cursor if terminal allows. Try minimize cursor if that fails.
    # Do nothing if that fails
    if hasattr(c, "curs_set"):
        try:
            c.curs_set(0)  # Hide the cursor
        except:
            try:
                c.curs_set(1)
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
        "w_black_bear_adj": c.color_pair(1),
        "w_black_goldilocks_adj": c.color_pair(1)
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

    # set goldilocks spawn point to empty space
    for row in range(GOLDILOCKS_Y - 1, GOLDILOCKS_Y + 3):
        for col in range(GOLDILOCKS_X - 1, GOLDILOCKS_X + 3):
            map[row][col] = 0

    pad = c.newpad(ROWS + 1, COLS + 1)

    # Smooth the random map into something more cave shaped
    for ind in range(7):
        map = smooth_map(map)

    # Add bear and rocks to map
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

    # quest and quest complete status
    quest = False
    quest_complete = False

    # Generate quest window
    update_quest(quest, quest_complete)

    show_goldilocks = False
    show_porridge = False

    goldilocks_spawned = False  # True if Goldilocks has spawned

    while True:
        # main movement
        key = stdscr.getch()
        if key != -1:
            if key == ESC:
                pause_menu()
            # Exits game if endwin has been called (from pause_menu)
            if key == ord("q") or c.isendwin():  # TODO: Remove "q" from this bit mmmmmmmmmmmmmmmm
                break
            else:
                # Refresh quest window after pause to remove window overlap
                update_quest(quest, quest_complete)

            # Move Left
            if key == c.KEY_LEFT or key == ord("a") or key == ord("A"):
                # Set previous player position to open space
                pad.addstr(y + 12, x + 40, " ")
                # Detect if tile is wall/bear/goldilocks/bear adjacent
                # (bear emoji character width == 2, so need to check 2 tiles)
                next_tile = map[y + 12][x + 40 - 1]
                if next_tile not in [1, 2, 4]:
                    # Detect if next tile is a rock
                    if next_tile == 3:
                        inventory = update_inventory("Rock", inventory)
                    x -= 1

            # Move Right
            if key == c.KEY_RIGHT or key == ord("d") or key == ord("D"):
                pad.addstr(y + 12, x + 40, " ")
                next_tile = map[y + 12][x + 40 + 1]
                if next_tile not in [1, 2, 4]:
                    if next_tile == 3:
                        inventory = update_inventory("Rock", inventory)
                    x += 1

            # Move Up
            if key == c.KEY_UP or key == ord("w") or key == ord("W"):
                pad.addstr(y + 12, x + 40, " ")
                next_tile = map[y + 12 - 1][x + 40]
                if next_tile not in [1, 2, 4]:
                    if next_tile == 3:
                        inventory = update_inventory("Rock", inventory)
                    y -= 1

            # Move Down
            if key == c.KEY_DOWN or key == ord("s") or key == ord("S"):
                pad.addstr(y + 12, x + 40, " ")
                next_tile = map[y + 12 + 1][x + 40]
                if next_tile not in [1, 2, 4]:
                    if next_tile == 3:
                        inventory = update_inventory("Rock", inventory)
                    y += 1

            # Show inventory
            if key == ord("i") or key == ord("I"):
                show_inventory(inventory)
                # run update quest to ensure quest window displays
                # properly after show_inventory() call
                update_quest(quest, quest_complete)

            # Hide goldilocks (until quest is active)
            if not show_goldilocks:
                pad.addstr(GOLDILOCKS_Y, GOLDILOCKS_X, "  ", c.color_pair(1))

            if not show_porridge:
                pad.addstr(PORRIDGE_Y, PORRIDGE_X, "  ", c.color_pair(1))

            # Spawn goldilocks on quest initiation
            if key == ord("g") or (quest and not goldilocks_spawned):  # ADFSUDFSDUHFIOSDHFI REMOVE G CHECK AASDASHDASIDJAOIDFJAROIGJA45

                pad.clear()
                spawn_goldilocks(map)
                draw_map(pad, map, colors)

                # Show Goldilocks, and Porridge
                show_goldilocks = True
                show_porridge = True

                goldilocks_spawned = True

            # Update player position
            pad.addstr(y + 12, x + 40, f"{PLAYER_ICON}")

            coords(x + 40, y + 12)
            pad.refresh(y, x, 0, 0, 22, 60)

            # Check if player is near bear:
            if (x + 40 in range(BEAR_X - 2, BEAR_X + 3) and
                    y + 12 in range(BEAR_Y - 1, BEAR_Y + 2)):
                if not quest:
                    # Interact with bear and add to quest list

                    quest = bear_dialogue()  # set quest to True
                    update_quest(quest, quest_complete)  # Set quest window

                elif inventory["Porridge"] > 0:
                    bear_dialogue_win()
                    inventory["Porridge"] = 0
                    quest = False
                    quest_complete = True
                    update_quest(quest, quest_complete)

            # Check if player is near Goldilocks
            if quest and show_goldilocks:
                if (x + 40 in range(GOLDILOCKS_X - 1, GOLDILOCKS_X + 3) and
                        y + 12 in range(PORRIDGE_Y - 1, GOLDILOCKS_Y + 2)):
                    show_goldilocks = False
                    result = goldilocks_dialogue()
                    if not result:  # Game over if player loses to goldilocks
                        print("GAME OVER")
                        break

            # Check if player is on porridge:
            if x + 40 == PORRIDGE_X and y + 12 == PORRIDGE_Y and show_porridge:
                # Add porridge to inventory
                inventory = update_inventory("Porridge", inventory)
                # Hide porridge
                show_porridge = False

            if key == ord("l"):
                bear_dialogue_win()
                # dialogue = True
                # fight_goldilocks()
            # pad.refresh(y, x, 0, 0, 40, 155)
            if key == ord("k"):
                # bear_dialogue_win()
                # dialogue = True
                fight_goldilocks()
            # pad.refresh(y, x, 0, 0, 40, 155)
            if key == ord("t"):
                quest = True
                show_goldilocks = True


c.wrapper(main)
