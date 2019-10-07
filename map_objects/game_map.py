import tcod as libtcod
from random import randint

from components.ai import BasicMonster
from components.equipment import Equipment, EquipmentSlots
from components.equippable import Equippable
from components.fighter import Fighter
from components.inventory import Inventory
from components.item import Item
from components.level import Level
from components.stairs import Stairs
from entity import Entity
from game_messages import Message
from item_functions import cast_lightning, cast_fireball, cast_confuse, heal
from map_objects.rectangle import Rect
from map_objects.tile import Tile
from random_utils import from_dungeon_level, random_choice_from_dict
from render_functions import RenderOrder


class GameMap:
    def __init__(self, config, dungeon_level=1):
        self.config = config
        self.width = config.map_width
        self.height = config.map_height
        self.tiles = self.initialize_tiles()
        self.dungeon_level = dungeon_level

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

        return tiles

    def make_map(self, player, entities):
        rooms = []
        num_rooms = 0

        center_of_last_room_x = None
        center_of_last_room_y = None

        for r in range(self.config.max_rooms):
            # random width and height
            w = randint(self.config.room_min_size, self.config.room_max_size)
            h = randint(self.config.room_min_size, self.config.room_max_size)
            # random position without going out of the boundaries of the map
            x = randint(0, self.config.map_width - w - 1)
            y = randint(0, self.config.map_height - h - 1)

            # "Rect" class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)

            # run through the other rooms and see if they intersect with this one
            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                # this means there are no intersections, so this room is valid

                # "paint" it to the map's tiles
                self.create_room(new_room)

                # center coordinates of new room
                (new_x, new_y) = new_room.center()

                center_of_last_room_x = new_x
                center_of_last_room_y = new_y

                if num_rooms == 0:
                    # this is the first room, where the player starts at
                    player.x = new_x
                    player.y = new_y
                else:
                    # all rooms after the first:
                    # connect it to the previous room with a tunnel

                    # center coordinates of previous room
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    # flip a coin (random number that is either 0 or 1)
                    if randint(0, 1) == 1:
                        # first move horizontally, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        # first move vertically, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                self.place_entities(new_room, entities)

                # finally, append the new room to the list
                rooms.append(new_room)
                num_rooms += 1

        stairs_component = Stairs(self.dungeon_level + 1)
        down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, '>', libtcod.white, 'Stairs',
                             render_order=RenderOrder.STAIRS, stairs=stairs_component)
        entities.append(down_stairs)

    def create_room(self, room):
        # go through the tiles in the rectangle and make them passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False

    def place_entities(self, room, entities):
        max_monsters_per_room = from_dungeon_level([[2, 1], [3, 4], [5, 6]], self.dungeon_level)
        max_items_per_room = from_dungeon_level([[1, 1], [2, 4]], self.dungeon_level)

        # Get a random number of monsters
        number_of_monsters = randint(0, max_monsters_per_room)
        number_of_items = randint(0, max_items_per_room)

        monster_chances = {
            'rat': from_dungeon_level([[80, 1], [40, 3], [15, 5]], self.dungeon_level),
            'goblin': from_dungeon_level([[15, 1], [40, 3], [15, 5]], self.dungeon_level),
            'orc': from_dungeon_level([[20, 2], [30, 4], [60, 6]], self.dungeon_level),
            'troll': from_dungeon_level([[15, 3], [30, 5], [60, 7]], self.dungeon_level)
        }

        item_chances = {
            'torch': 10,
            'healing_potion': 35,
            'dagger': from_dungeon_level([[7, 1]], self.dungeon_level),
            'buckler': from_dungeon_level([[7, 2]], self.dungeon_level),
            'sword': from_dungeon_level([[35, 4]], self.dungeon_level),
            'shield': from_dungeon_level([[35, 8]], self.dungeon_level),
            'lightning_scroll': from_dungeon_level([[25, 4]], self.dungeon_level),
            'fireball_scroll': from_dungeon_level([[25, 6]], self.dungeon_level),
            'confusion_scroll': from_dungeon_level([[10, 2]], self.dungeon_level)
        }
        for i in range(number_of_monsters):
            # Choose a random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                monster_choice = random_choice_from_dict(monster_chances)

                if monster_choice == 'rat':
                    level_component = Level(current_level=1, current_xp=0, level_up_base=100, level_up_factor=100)
                    fighter_component = Fighter(hp=5, defense=0, power=1, body=monster_choice, xp=10, will_power = 0)
                    ai_component = BasicMonster()
                    monster = Entity(x, y, 'r', libtcod.dark_amber, 'Rat', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
                elif monster_choice == 'goblin':
                    level_component = Level(current_level=1, current_xp=0, level_up_base=40, level_up_factor=150)
                    fighter_component = Fighter(hp=10, defense=0, power=2, body=monster_choice, fov=7, xp=20, level=level_component, will_power = 1)
                    ai_component = BasicMonster()
                    monster = Entity(x, y, 'g', libtcod.dark_green, 'Goblin', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component, inventory = Inventory(2), equipment = Equipment())
                elif monster_choice == 'orc':
                    fighter_component = Fighter(hp=20, defense=0, power=4, body=monster_choice, fov=4, xp=35, will_power = 2)
                    ai_component = BasicMonster()
                    monster = Entity(x, y, 'o', libtcod.darker_green, 'Orc', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component, inventory = Inventory(10), equipment = Equipment())
                else:
                    fighter_component = Fighter(hp=30, defense=2, power=8, body=monster_choice, xp=100, will_power = 3)
                    ai_component = BasicMonster()
                    monster = Entity(x, y, 'T', libtcod.darkest_green, 'Troll', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component, inventory = Inventory(15), equipment = Equipment())

                entities.append(monster)

        for i in range(number_of_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                item_choice = random_choice_from_dict(item_chances)

                if item_choice == 'healing_potion':
                    item_component = Item(use_function=heal, amount=40)
                    item = Entity(x, y, '!', libtcod.violet, 'Healing Potion', render_order=RenderOrder.ITEM,
                                  item=item_component)
                elif item_choice == 'torch':
                    equippable_component = Equippable(EquipmentSlots.OFF_HAND, fov_bonus=5)
                    item = Entity(x, y, 't', libtcod.yellow, 'Torch', equippable=equippable_component)
                elif item_choice == 'sword':
                    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=3)
                    item = Entity(x, y, '/', libtcod.sky, 'Sword', equippable=equippable_component)
                elif item_choice == 'shield':
                    equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=2)
                    item = Entity(x, y, '[', libtcod.darker_orange, 'Shield', equippable=equippable_component)
                elif item_choice == 'dagger':
                    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=1)
                    item = Entity(x, y, '/', libtcod.red, 'Small Dagger', equippable=equippable_component)
                elif item_choice == 'buckler':
                    equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=1)
                    item = Entity(x, y, '[', libtcod.red, 'Rotten Buckler', equippable=equippable_component)
                elif item_choice == 'fireball_scroll':
                    item_component = Item(use_function=cast_fireball, targeting=True, targeting_message=Message(
                        'Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan),
                                          damage=25, radius=3)
                    item = Entity(x, y, '#', libtcod.red, 'Fireball Scroll', render_order=RenderOrder.ITEM,
                                  item=item_component)
                elif item_choice == 'confusion_scroll':
                    item_component = Item(use_function=cast_confuse, targeting=True, targeting_message=Message(
                        'Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan))
                    item = Entity(x, y, '#', libtcod.light_pink, 'Confusion Scroll', render_order=RenderOrder.ITEM,
                                  item=item_component)
                else:
                    item_component = Item(use_function=cast_lightning, damage=40, maximum_range=5)
                    item = Entity(x, y, '#', libtcod.yellow, 'Lightning Scroll', render_order=RenderOrder.ITEM,
                                  item=item_component)

                entities.append(item)

    def next_floor(self, player, message_log, constants):
        self.dungeon_level += 1
        entities = [player]

        self.tiles = self.initialize_tiles()
        self.make_map(player, entities)

        if player.fighter:
            player.fighter.heal(player.fighter.max_hp // 2)

        message_log.add_message(Message('You take a moment to rest, and recover your strength.', libtcod.light_violet))

        return entities
