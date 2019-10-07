import tcod as libtcod

from components.level import Level

from entity import Entity

from game_messages import MessageLog

from game_states import GameStates

from map_objects.game_map import GameMap

from render_functions import RenderOrder

def get_game_variables(config):
    level_component = Level(current_level=0, current_xp=0, level_up_base=2, level_up_factor=3, level_up_exponent=2)

    player = Entity(0, 0, ' ', libtcod.white, 'Player', blocks=True, render_order=RenderOrder.GHOST, level=level_component)

    entities = [player]

    game_map = GameMap(config)
    game_map.make_map(player, entities)

    message_log = MessageLog(config)

    game_state = GameStates.PLAYERS_TURN

    return player, entities, game_map, message_log, game_state

class Constants:
    window_title = 'Our Glory Shall Not Descend'

    screen_width = 80
    screen_height = 50

    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    fov_algorithm = 0
    fov_light_walls = True
    min_fov_radius = 4

    max_monsters_per_room = 3
    max_items_per_room = 2

    colors = {
        'dark_wall': libtcod.Color(1, 1, 111),
        'dark_ground': libtcod.Color(49, 51, 152),
        'shadowed_wall': libtcod.Color(0, 0, 90),
        'shadowed_ground': libtcod.Color(60, 60, 160),
        'illuminated_wall': libtcod.Color(130, 110, 50),
        'illuminated_ground': libtcod.Color(200, 180, 50)
    }

    constants = {
        'window_title': window_title,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'bar_width': bar_width,
        'panel_height': panel_height,
        'panel_y': panel_y,
        'message_x': message_x,
        'message_width': message_width,
        'message_height': message_height,
        'map_width': map_width,
        'map_height': map_height,
        'room_max_size': room_max_size,
        'room_min_size': room_min_size,
        'max_rooms': max_rooms,
        'fov_algorithm': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'min_fov_radius': min_fov_radius,
        'max_monsters_per_room': max_monsters_per_room,
        'max_items_per_room': max_items_per_room,
        'colors': colors
    }
