import math
from operator import attrgetter
import engine
from engine.util.vector import Vec2

class Graphics(object):
    def init_window(self, window_dimensions, tile_dimensions, caption):
        raise NotImplementedError()
    def clear_screen(self):
        raise NotImplementedError()
    def draw_tile(self, character, fg_color, bg_color):
        raise NotImplementedError()


class Tile(object):
    def __init__(self, character, fg_color, bg_color):
        self.character = character
        self.fg_color = fg_color
        self.bg_color = bg_color

    def draw(self, g, position):
        g.draw_tile(position, self.character, self.fg_color, self.bg_color)


class Color(object):
    def __init__(self, r, g, b, a=255):
        for val in [r, g, b, a]:
            if isinstance(val, float):
                raise ValueError("A Color object cannot contain the float value '" + str(val) + "'.")
            if val < 0 or val > 255:
                raise ValueError('The parameters to a Color object must be in the range [0, 255].')
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def to_RGB_tuple(self):
        return (self.r, self.g, self.b)
    def to_RGBA_tuple(self):
        return (self.r, self.g, self.b, self.a)

    def __hash__(self):
        return hash(self.to_RGBA_tuple())
    def __eq__(self, other):
        return self.r == other.r and self.g == other.g and self.b == other.b and self.a == other.a


class Paint(object):
    def get_tile_color(self, absolute_position, relative_position):
        """absolute_position is absolute in the window, relative_position is relative_position to the Drawable being colored
        The Paint may only use one of them depending on whether it draws absolutely or relatively
        """
        raise NotImplementedError()
    def tick(self, millis):
        pass
class SolidPaint(Paint):
    def __init__(self, color):
        self.color = color
    def get_tile_color(self, absolute_position, relative_position):
        return self.color
class GradientPaint(Paint):
    pass
class LinearGradientPaint(GradientPaint):
    def __init__(self, color1, position1, color2, position2, is_cyclical=True, is_relative=True):
        self.color1 = color1
        self.position1 = position1
        self.color2 = color2
        self.position2 = position2
        self.is_cyclical = is_cyclical
        self.is_relative = is_relative
        self.direction_vector = (self.position2 - self.position1).normalized()
    def get_tile_color(self, relative_position, absolute_position):
        position = relative_position if self.is_relative else absolute_position
        projection = position.dot(self.direction_vector) # project the position onto the linear direction vector
        p1_projection = self.position1.dot(self.direction_vector)
        p2_projection = self.position2.dot(self.direction_vector)
        percent = self._get_percent_along_projection(projection, p1_projection, p2_projection)
        return Color(
            int(round(self.color1.r + percent * (self.color2.r - self.color1.r))),
            int(round(self.color1.g + percent * (self.color2.g - self.color1.g))),
            int(round(self.color1.b + percent * (self.color2.b - self.color1.b))),
            int(round(self.color1.a + percent * (self.color2.a - self.color1.a))),
        )
    def _get_percent_along_projection(self, projection, p1_projection, p2_projection):
        diff = p2_projection - p1_projection
        raw_percent = (projection-p1_projection) / diff
        if self.is_cyclical:
            must_inverse = int(raw_percent) % 2 == 1
            fractional_part = math.modf(raw_percent)[0]
            percent_before_inverse = abs(fractional_part)
            return 1-percent_before_inverse if must_inverse else percent_before_inverse
        else:
            if raw_percent < 0:
                return 0
            elif raw_percent > 1:
                return 1
            else:
                return raw_percent


class Drawable(object):
    def __init__(self, position, fg_paint=None, bg_paint=None):
        self.position = position
        self.fg_paint = fg_paint
        self.bg_paint = bg_paint
        self.tiles = []

    def add_tile(self, tile, offset):
        self.tiles.append((tile, offset))
        # sort in top-to-bottom, left-to-right text order
        self.tiles.sort(key=lambda pair: attrgetter('y', 'x')(pair[1]))
    def add_rectangle(self, dimensions, character, fg_color, bg_color):
        for x in range(dimensions.x):
            for y in range(dimensions.y):
                self.add_tile(Tile(character, fg_color, bg_color), Vec2(x, y))

    def update_drawable(self, millis):
        self._update_paint(millis, self.fg_paint, True)
        self._update_paint(millis, self.bg_paint, False)

    def _update_paint(self, millis, paint, is_foreground):
        if paint is not None:
            paint.tick(millis)
            for tile, offset in self.tiles:
                color = paint.get_tile_color(offset, self.position+offset)
                if is_foreground:
                    tile.fg_color = color
                else:
                    tile.bg_color = color

    def draw(self, g):
        for tile, offset in self.tiles:
            tile.draw(g, self.position+offset)

    def contains_position(self, position):
        for tile, offset in self.tiles:
            tile_position = self.position + offset
            if tile_position == position:
                return True
        return False

    def write_text(self, text):
        characters = engine.parse_text_into_characters(text)
        for tile, offset in self.tiles:
            if len(characters) == 0:
                break
            tile.character = characters[0]
            characters.pop(0)
