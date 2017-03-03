import engine
from engine.graphics import Tile, Color, Drawable
from engine.util.vector import Vec2

class Backend(object):
    def __init__(self, window_dimensions, tile_dimensions, caption, starting_screen):
        engine.window_dimensions = window_dimensions
        engine.tile_dimensions = tile_dimensions
        self.caption = caption
        self.screens = [starting_screen]

    def run(self):
        raise NotImplementedError()

    def on_tick(self, millis):
        self.get_current_screen().on_tick(millis)

    def on_draw(self, g):
        self.get_current_screen().on_draw(g)

    def get_current_screen(self):
        return self.screens[-1]
    def set_screen(self, screen):
        self.screens.append(screen)
    def go_back_n_screens(self, n):
        for i in range(n):
            self.screens.pop()

    def handle_key_down(self, event):
        self.get_current_screen().handle_key_down(event)
    def handle_key_up(self, event):
        self.get_current_screen().handle_key_up(event)
    def handle_mouse_moved(self, event):
        engine.mouse_position = event.position
        self.get_current_screen().handle_mouse_moved(event)
    def handle_mouse_button_down(self, event):
        self.get_current_screen().handle_mouse_button_down(event)
    def handle_mouse_button_up(self, event):
        self.get_current_screen().handle_mouse_button_up(event)
    def handle_mouse_wheel_scrolled(self, event):
        self.get_current_screen().handle_mouse_wheel_scrolled(event)


class UIElementContainer(Drawable):
    def __init__(self, position):
        super(UIElementContainer, self).__init__(position)
        self.ui_elements = []

    def on_tick(self, millis):
        for elt in self.ui_elements[:]:
            elt.on_tick(millis)
            elt.update_drawable(millis)

    def on_draw(self, g):
        self.draw(g)
        for elt in self.ui_elements[:]:
            elt.on_draw(g)

    def add_child(self, child):
        self.ui_elements.append(child)
    def remove_child(self, child):
        self.ui_elements.remove(child)

    def handle_key_down(self, event):
        self.on_key_down(event)
        for elt in self.ui_elements[:]:
            elt.handle_key_down(event)
    def handle_key_up(self, event):
        self.on_key_up(event)
        for elt in self.ui_elements[:]:
            elt.handle_key_up(event)
    def handle_mouse_moved(self, event):
        self.on_mouse_moved(event)
        for elt in self.ui_elements[:]:
            elt.handle_mouse_moved(event)
    def handle_mouse_button_down(self, event):
        self.on_mouse_button_down(event)
        for elt in self.ui_elements[:]:
            elt.handle_mouse_button_down(event)
    def handle_mouse_button_up(self, event):
        self.on_mouse_button_up(event)
        for elt in self.ui_elements[:]:
            elt.handle_mouse_button_up(event)
    def handle_mouse_wheel_scrolled(self, event):
        self.on_mouse_wheel_scrolled(event)
        for elt in self.ui_elements[:]:
            elt.handle_mouse_wheel_scrolled(event)

    def on_key_down(self, event):
        pass
    def on_key_up(self, event):
        pass
    def on_mouse_moved(self, event):
        pass
    def on_mouse_button_down(self, event):
        pass
    def on_mouse_button_up(self, event):
        pass
    def on_mouse_wheel_scrolled(self, event):
        pass

class Screen(UIElementContainer):
    def __init__(self):
        super(Screen, self).__init__(Vec2(0, 0))
