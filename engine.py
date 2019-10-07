import tcod as libtcod
import tcod.event

from components.ai import SlowMonster
from components.equipment import EquipmentSlots, Equipment
from components.inventory import Inventory
from components.equippable import Equippable
from components.fighter import Fighter
from death_functions import kill_monster, kill_player
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_messages import Message
from game_states import GameStates
from input_handlers import handle_keys, handle_main_menu
from loader_functions.data_loaders import save_game, load_game
from loader_functions.initialize_new_game import Constants, get_game_variables
from menus import main_menu, message_box
from render_functions import RenderOrder, clear_all, render_all

from os import path
import sys

# Get the current location of the bundled App (a la PyInstaller)
app_dir = getattr(sys, '_MEIPASS', path.abspath(path.dirname(__file__)))


def app_path(*local_path_segments):
    # Account for varying slash marks across filesystems & OSes
    return path.join(app_dir, *local_path_segments)


def main():

    arial_font_path = app_path('assets', 'images', 'arial10x10.png')

    libtcod.console_set_custom_font(arial_font_path, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

    libtcod.console_init_root(Constants.screen_width, Constants.screen_height, Constants.window_title, False, libtcod.RENDERER_SDL2, vsync=False)

    con = libtcod.console.Console(Constants.screen_width, Constants.screen_height)
    panel = libtcod.console.Console(Constants.screen_width, Constants.panel_height)

    player = None
    entities = []
    game_map = None
    message_log = None
    game_state = None

    show_main_menu = True
    show_load_error_message = False

    bg_path = app_path('assets', 'images', 'menu_fire_background.png')
    main_menu_background_image = libtcod.image_load(bg_path)

    while True:
        key = 0
        for event in libtcod.event.get():
            print(f"Got Event: {event.type}")
            if event.type in ("QUIT"):
                print("QUIT event: Exiting")
                raise SystemExit()
            if event.type == "KEYDOWN":
                if event.sym == libtcod.event.K_ESCAPE:
                    print(f"{event.type} K_ESCAPE: Exiting")
                    raise SystemExit()
                else:
                    key = event.sym

        if show_main_menu:
            main_menu(con, main_menu_background_image, Constants.screen_width,
                      Constants.screen_height)

            if show_load_error_message:
                message_box(con, 'No save game to load', 50, Constants.screen_width, Constants.screen_height)

            libtcod.console_flush()

            action = handle_main_menu(key)

            new_game = action.get('new_game')
            load_saved_game = action.get('load_game')
            exit_game = action.get('exit')

            if show_load_error_message and (new_game or load_saved_game or exit_game):
                show_load_error_message = False
            elif new_game:
                player, entities, game_map, message_log, game_state = get_game_variables(Constants)
                game_state = GameStates.PLAYERS_TURN

                show_main_menu = False
            elif load_saved_game:
                try:
                    player, entities, game_map, message_log, game_state = load_game()
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error_message = True
            elif exit_game:
                break

        else:
            con.clear()
            play_game(player, entities, game_map, message_log, game_state, con, panel, Constants)

            show_main_menu = True

def play_game(player, entities, game_map, message_log, game_state, con, panel, constants):
    fov_recompute = True
    fov_map = initialize_fov(game_map)

    previous_game_state = game_state

    targeting_item = None

    message_log.add_message(Message(f'You are ghost.  You have nothing.', libtcod.white))
    message_log.add_message(Message(f'Use the arrow keys to move', libtcod.white))
    message_log.add_message(Message(f'Press \'p\' to possess a creature and gain it\'s abilities', libtcod.white))

    mouse_event = None
    while True:
        key = 0
        left_click = None
        right_click = None
        exit_game = False

        for event in libtcod.event.get():
            print(f"Got Event: {event.type}")
            if event.type in ("QUIT"):
                print("QUIT event: Exiting")
                raise SystemExit()
            if event.type == "KEYDOWN":
                if event.sym == libtcod.event.K_ESCAPE:
                    print(f"{event.type} K_ESCAPE: Exiting")
                    exit_game = True
                else:
                    key = event.sym
            if event.type == "MOUSEMOTION":
                mouse_event = event
                if event.state & libtcod.event.BUTTON_LMASK:
                    left_click = mouse_event
                if event.state & libtcod.event.BUTTON_RMASK:
                    right_click = mouse_event

        if exit_game:
            break

        fov_radius = player.fighter.fov() if player.fighter else Constants.min_fov_radius
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius, Constants.fov_light_walls, Constants.fov_algorithm)

        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, Constants.screen_width,
                   Constants.screen_height, Constants.bar_width, Constants.panel_height, Constants.panel_y, mouse_event, Constants.colors, game_state)

        fov_recompute = False

        libtcod.console_flush()

        clear_all(con, entities)
        action = handle_keys(key, game_state)

        move = action.get('move')
        wait = action.get('wait')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        inventory_index = action.get('inventory_index')
        take_stairs = action.get('take_stairs')
        level_up = action.get('level_up')
        show_character_screen = action.get('show_character_screen')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')
        possession = action.get('possession')
        start_test_mode = action.get('start_test_mode')
        restart = action.get('restart')

        player_turn_results = []

        if False: # start_test_mode:
            fighter_component = Fighter(hp=30, defense=2, power=8, body='god mode', xp=100, will_power = 4)
            player.fighter = fighter_component
            player.fighter.owner = player
            player.inventory = Inventory(26)
            player.equipment = Equipment()
            player.inventory.owner = player
            player.equipment.owner = player
            equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=1)
            item = Entity(player.x, player.y, '/', libtcod.red, 'Small Dagger', equippable=equippable_component)
            entities.append(item)

        if restart:
            player, entities, game_map, message_log, game_state = get_game_variables(Constants)
            game_state = GameStates.PLAYERS_TURN
            fov_map = initialize_fov(game_map)
            fov_recompute = True
            con.clear()

        if possession:
            if not player.fighter:
                for entity in entities:
                    if entity.fighter and entity.x == player.x and entity.y == player.y:
                        if player.level.current_level >= entity.fighter.will_power:
                            message_log.add_message(Message(f'You take control of the {entity.name} body', libtcod.blue))
                            player.fighter = entity.fighter
                            player.inventory = entity.inventory
                            player.equipment = entity.equipment
                            player.possessed_entity = entity
                            player.fighter.owner = player
                            player.char = entity.char
                            player.render_order = entity.render_order
                            entities.remove(entity)
                        else:
                            message_log.add_message(Message(f'{entity.name} is too powerful for you to possess', libtcod.blue))


            else:
                message_log.add_message(Message(f'You cast your spirit out of your body, leaving a shambling husk behind...', libtcod.blue))
                ai_component = SlowMonster()
                zombie_name = f'Zombie {player.possessed_entity.name}'
                zombie_char = player.possessed_entity.char
                zombie = Entity(player.x, player.y, zombie_char, libtcod.desaturated_green, zombie_name, blocks=True, render_order=RenderOrder.ACTOR, fighter=player.fighter, ai=ai_component, inventory = player.inventory, equipment = player.equipment)
                zombie.fighter.xp = 5
                zombie.fighter.owner = zombie
                entities.append(zombie)

                player.fighter = None
                player.inventory = None
                player.equipment = None
                player.char = ' '
                player.render_order = RenderOrder.GHOST

        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy
            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                if target and player.fighter:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)
                    fov_recompute = True
                game_state = GameStates.ENEMY_TURN

        elif wait:
            game_state = GameStates.ENEMY_TURN

        elif pickup and game_state == GameStates.PLAYERS_TURN:
            if player.inventory:
                for entity in entities:
                    if entity.item and entity.x == player.x and entity.y == player.y:
                        pickup_results = player.inventory.add_item(entity)
                        player_turn_results.extend(pickup_results)

                        break
                else:
                    message_log.add_message(Message('There is nothing here to pick up!', libtcod.yellow))
            elif player.fighter:
                message_log.add_message(Message('This creature cannot carry items.', libtcod.yellow))
            else:
                message_log.add_message(Message("You can't pick up items without a body of some kind...", libtcod.yellow))


        if show_inventory:
            if player.inventory:
                previous_game_state = game_state
                game_state = GameStates.SHOW_INVENTORY
            elif player.fighter:
                message_log.add_message(Message('This creature cannot carry items.', libtcod.yellow))
            else:
                message_log.add_message(Message('You lack a body to carry items...', libtcod.yellow))

        if drop_inventory:
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        if inventory_index is not None and player.inventory and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(
                player.inventory.items):
            item = player.inventory.items[inventory_index]
            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        if take_stairs and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if entity.stairs and entity.x == player.x and entity.y == player.y:
                    entities = game_map.next_floor(player, message_log, constants)
                    fov_map = initialize_fov(game_map)
                    fov_recompute = True
                    libtcod.console_clear(con)

                    break
            else:
                message_log.add_message(Message('There are no stairs here.', libtcod.yellow))

        if level_up:
            if player.fighter:
                if level_up == 'hp':
                    player.fighter.base_max_hp += 20
                    player.fighter.hp += 20
                elif level_up == 'str':
                    player.fighter.base_power += 1
                elif level_up == 'def':
                    player.fighter.base_defense += 1

            game_state = previous_game_state

        if show_character_screen:
            previous_game_state = game_state
            game_state = GameStates.CHARACTER_SCREEN

        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inventory.use(targeting_item, entities=entities, fov_map=fov_map,
                                                        target_x=target_x, target_y=target_y)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})

        if exit:
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.CHARACTER_SCREEN):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            else:
                save_game(player, entities, game_map, message_log, game_state)
                return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            equip = player_turn_result.get('equip')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')
            xp = player_turn_result.get('xp')

            if message:
                message_log.add_message(message)

            if targeting_cancelled:
                game_state = previous_game_state
                message_log.add_message(Message('Targeting cancelled'))

            if xp:
                leveled_up = player.level.add_xp(xp)
                fighter_leveled_up = player.fighter.level.add_xp(xp)
                message_log.add_message(Message('You gain {0} experience points.'.format(xp)))

                if leveled_up:
                    message_log.add_message(Message(
                        'You grow stronger! You reached level {0}'.format(
                            player.level.current_level) + '!', libtcod.yellow))
                    message_log.add_message(Message('you can now possess larger creatures'))

                if fighter_leveled_up:
                    previous_game_state = game_state
                    game_state = GameStates.LEVEL_UP

            if dead_entity:
                if dead_entity.fighter == player.fighter:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

            if item_added:
                entities.remove(item_added)

                game_state = GameStates.ENEMY_TURN

            if item_consumed:
                game_state = GameStates.ENEMY_TURN

            if item_dropped:
                entities.append(item_dropped)

                game_state = GameStates.ENEMY_TURN

            if equip:
                equip_results = player.equipment.toggle_equip(equip)

                for equip_result in equip_results:
                    equipped = equip_result.get('equipped')
                    dequipped = equip_result.get('dequipped')

                    if equipped:
                        message_log.add_message(Message('You equipped the {0}'.format(equipped.name)))

                    if dequipped:
                        message_log.add_message(Message('You dequipped the {0}'.format(dequipped.name)))

                game_state = GameStates.ENEMY_TURN

            if targeting:
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING

                targeting_item = targeting

                message_log.add_message(targeting_item.item.targeting_message)


        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')

                        if message:
                            message_log.add_message(message)

                        if dead_entity:
                            if dead_entity.fighter == player.fighter:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break

            else:
                game_state = GameStates.PLAYERS_TURN

if __name__ == '__main__':
    main()
