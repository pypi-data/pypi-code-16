import math
import pyrogi
from pyrogi.util.vector import Vec2

LEFT_BUTTON = 1
MIDDLE_BUTTON = 2
RIGHT_BUTTON = 3
SCROLL_WHEEL_UP = 4
SCROLL_WHEEL_DOWN = 5

def pixel_position_to_tile_position(position):
    return Vec2(math.floor(position.x/pyrogi.tile_dimensions.x), math.floor(position.y/pyrogi.tile_dimensions.y))

class Event(object):
    pass

class KeyDownEvent(Event):
    def __init__(self, character, key, modifier):
        self.character = character
        self.key = key
        self.modifier = modifier
class KeyUpEvent(Event):
    def __init__(self, key, modifier):
        self.key = key
        self.modifier = modifier
class MouseMovedEvent(Event):
    def __init__(self, position, relative_position, buttons):
        self.position = pixel_position_to_tile_position(Vec2(position))
        self.relative_pixels = Vec2(relative_position)
        self.last_position = pixel_position_to_tile_position(Vec2(position)-Vec2(relative_position))
        self.relative_tiles = self.position - self.last_position
        self.buttons = buttons
class MouseButtonDownEvent(Event):
    def __init__(self, position, button):
        self.position = pixel_position_to_tile_position(Vec2(position))
        self.button = button
class MouseButtonUpEvent(Event):
    def __init__(self, position, button):
        self.position = pixel_position_to_tile_position(Vec2(position))
        self.button = button
class MouseWheelScrolledEvent(Event):
    def __init__(self, position, scroll_amount):
        self.position = pixel_position_to_tile_position(Vec2(position))
        self.scroll_amount = scroll_amount
