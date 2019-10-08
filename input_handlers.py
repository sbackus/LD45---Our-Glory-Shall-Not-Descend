import tcod as libtcod

from game_states import GameStates


def get_key_from_event(key_event):
    return key_event.sym if key_event else None


def with_alt(key_event):
    if key_event and key_event.mod and (key_event.mod & libtcod.event.KMOD_ALT):
        return True
    return False


def handle_keys(key_event, game_state):
    if game_state == GameStates.PLAYERS_TURN:
        return handle_player_turn_keys(key_event)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key_event)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_inventory_keys(key_event)
    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(key_event)
    elif game_state == GameStates.LEVEL_UP:
        return handle_level_up_menu(key_event)
    elif game_state == GameStates.CHARACTER_SCREEN:
        return handle_character_screen(key_event)
    return {}


def handle_targeting_keys(key_event):
    if key_event.sym == libtcod.event.K_ESCAPE:
        return {'exit': True}

    return {}

KEY_A = libtcod.event.K_a
KEY_B = libtcod.event.K_b
KEY_C = libtcod.event.K_c

LEFT_KEYS = (libtcod.event.K_LEFT, libtcod.event.K_KP_4, libtcod.event.K_h)
RIGHT_KEYS = (libtcod.event.K_RIGHT, libtcod.event.K_KP_6, libtcod.event.K_l)
UP_KEYS = (libtcod.event.K_UP, libtcod.event.K_KP_8, libtcod.event.K_k)
DOWN_KEYS = (libtcod.event.K_DOWN, libtcod.event.K_KP_2, libtcod.event.K_j)

UP_LEFT_KEYS = (libtcod.event.K_KP_7, libtcod.event.K_y)
UP_RIGHT_KEYS = (libtcod.event.K_KP_9, libtcod.event.K_u)
DOWN_LEFT_KEYS = (libtcod.event.K_KP_1, libtcod.event.K_b)
DOWN_RIGHT_KEYS = (libtcod.event.K_KP_3, libtcod.event.K_n)

ENTER_KEYS = (libtcod.event.K_KP_ENTER, libtcod.event.K_RETURN, libtcod.event.K_RETURN2)

WAIT_KEYS = (libtcod.event.K_z, libtcod.event.K_SPACE, libtcod.event.K_KP_SPACE)

RESTART_KEYS = (libtcod.event.K_c, libtcod.event.K_r)


def handle_player_turn_keys(key_event):
    key = get_key_from_event(key_event)
    if not key:
        return {}

    # TODO refactor me into a big map of key sets -> actions?

    # Meta-key events should be checked first
    if with_alt(key_event) and key in ENTER_KEYS:
        return {'fullscreen': True}

    elif key in UP_KEYS:
        return {'move': (0, -1)}
    elif key in DOWN_KEYS:
        return {'move': (0, 1)}
    elif key in LEFT_KEYS:
        return {'move': (-1, 0)}
    elif key in RIGHT_KEYS:
        return {'move': (1, 0)}
    elif key in UP_LEFT_KEYS:
        return {'move': (-1, -1)}
    elif key in UP_RIGHT_KEYS:
        return {'move': (1, -1)}
    elif key in DOWN_LEFT_KEYS:
        return {'move': (-1, 1)}
    elif key in DOWN_RIGHT_KEYS:
        return {'move': (1, 1)}
    elif key in WAIT_KEYS:
        return {'wait': True}

    elif key == libtcod.event.K_p:
        return {'possession': True}

    if key == libtcod.event.K_g:
        return {'pickup': True}

    elif key == libtcod.event.K_i:
        return {'show_inventory': True}

    elif key == libtcod.event.K_d:
        return {'drop_inventory': True}

    elif key in ENTER_KEYS:
        return {'take_stairs': True}

    elif key == libtcod.event.K_c:
        return {'show_character_screen': True}

    elif key == libtcod.event.K_s:
        return {'start_test_mode': True}

    elif key == libtcod.event.K_ESCAPE:
        # Exit the game
        return {'exit': True}

    # No key was pressed
    return {}


def handle_player_dead_keys(key_event):
    key = get_key_from_event(key_event)
    if not key:
        return {}

    # Meta-key events should be checked first
    elif key in ENTER_KEYS and with_alt(key_event):
        return {'fullscreen': True}

    elif key == libtcod.event.K_i:
        return {'show_inventory': True}

    elif key == libtcod.event.K_ESCAPE:
        # Exit the menu
        return {'exit': True}

    elif key in RESTART_KEYS:
        return {'restart': True}

    return {}


def handle_inventory_keys(key_event):
    key = get_key_from_event(key_event)
    if not key:
        return {}

    # Get index relative to A-Z
    index = key - KEY_A

    # Meta-key events should be checked first
    if with_alt(key_event) and key in ENTER_KEYS:
        return {'fullscreen': True}

    # Is this a letter between A and Z?
    elif index >= 0 and index <= 25:
        return {'inventory_index': index}

    elif key == libtcod.event.K_ESCAPE:
        return {'exit': True}

    return {}


def handle_main_menu(key_event):
    key = get_key_from_event(key_event)
    if not key:
        return {}

    # Meta-key events should be checked first
    elif with_alt(key_event) and key in ENTER_KEYS:
        return {'fullscreen': True}

    elif key == KEY_A:
        return {'new_game': True}
    elif key == KEY_B:
        return {'load_game': True}
    elif key in (KEY_C, libtcod.event.K_ESCAPE):
        return {'exit': True}

    return {}


def handle_level_up_menu(key_event):
    key = get_key_from_event(key_event)
    if not key:
        return {}

    if key == KEY_A:
        return {'level_up': 'hp'}
    elif key == KEY_B:
        return {'level_up': 'str'}
    elif key == KEY_C:
        return {'level_up': 'def'}

    return {}


def handle_character_screen(key_event):
    key = get_key_from_event(key_event)
    if not key:
        return {}

    if key == libtcod.event.K_ESCAPE:
        return {'exit': True}

    return {}
