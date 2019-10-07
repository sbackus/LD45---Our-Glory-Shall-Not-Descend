import tcod as libtcod

from game_states import GameStates

def get_key_char(key):
    try:
        char = chr(key)
    except ValueError:
        return ""
    return char


def handle_keys(key, game_state):
    if game_state == GameStates.PLAYERS_TURN:
        return handle_player_turn_keys(key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_inventory_keys(key)
    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(key)
    elif game_state == GameStates.LEVEL_UP:
        return handle_level_up_menu(key)
    elif game_state == GameStates.CHARACTER_SCREEN:
        return handle_character_screen(key)
    return {}


def handle_targeting_keys(key):
    if key == libtcod.event.K_ESCAPE:
        return {'exit': True}

    return {}


ENTER_KEYS = (libtcod.event.K_KP_ENTER, libtcod.event.K_RETURN, libtcod.event.K_RETURN2)


def handle_player_turn_keys(key):
    if not key:
        return {}

    key_char = get_key_char(key)

    if key == libtcod.event.K_UP or key_char == 'k':
        return {'move': (0, -1)}
    elif key == libtcod.event.K_DOWN or key_char == 'j':
        return {'move': (0, 1)}
    elif key == libtcod.event.K_LEFT or key_char == 'h':
        return {'move': (-1, 0)}
    elif key == libtcod.event.K_RIGHT or key_char == 'l':
        return {'move': (1, 0)}
    elif key_char == 'y':
        return {'move': (-1, -1)}
    elif key_char == 'u':
        return {'move': (1, -1)}
    elif key_char == 'b':
        return {'move': (-1, 1)}
    elif key_char == 'n':
        return {'move': (1, 1)}
    elif key_char == 'z' or key_char == ' ':
        return {'wait': True}

    elif key_char == 'p':
        return {'possession': True}

    if key_char == 'g':
        return {'pickup': True}

    elif key_char == 'i':
        return {'show_inventory': True}

    elif key_char == 'd':
        return {'drop_inventory': True}

    elif key in ENTER_KEYS:
        return {'take_stairs': True}

    elif key_char == 'c':
        return {'show_character_screen': True}

    elif key_char == 's':
        return {'start_test_mode': True}

    if key in ENTER_KEYS and libtcod.event.KMOD_ALT:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}

    elif key == libtcod.event.K_ESCAPE:
        # Exit the game
        return {'exit': True}

    # No key was pressed
    return {}


def handle_player_dead_keys(key):
    if not key:
        return {}

    key_char = get_key_char(key)

    if key_char == 'i':
        return {'show_inventory': True}

    if key in ENTER_KEYS and libtcod.event.KMOD_ALT:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}
    elif key == libtcod.event.K_ESCAPE:
        # Exit the menu
        return {'exit': True}
    elif key_char == 'c' or key_char == 'r':
        return {'restart': True}

    return {}

def handle_inventory_keys(key):
    index = key - ord('a')

    if index >= 0:
        return {'inventory_index': index}

    if key in ENTER_KEYS and libtcod.event.KMOD_ALT:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}
    elif key == libtcod.event.K_ESCAPE:
        # Exit the menu
        return {'exit': True}

    return {}

def handle_main_menu(key):
    if not key:
        return {}

    key_char = get_key_char(key)

    if key_char == 'a':
        return {'new_game': True}
    elif key_char == 'b':
        return {'load_game': True}
    elif key_char == 'c' or  key == libtcod.event.K_ESCAPE:
        return {'exit': True}

    return {}

def handle_level_up_menu(key):
    if not key:
        return {}

    key_char = get_key_char(key)

    if key_char == 'a':
        return {'level_up': 'hp'}
    elif key_char == 'b':
        return {'level_up': 'str'}
    elif key_char == 'c':
        return {'level_up': 'def'}

    return {}

def handle_character_screen(key):
    if key == libtcod.event.K_ESCAPE:
        return {'exit': True}

    return {}
