import types
import engine
from engine.backend import UIElementContainer
from engine.graphics import Tile, Color, SolidPaint, Drawable
from engine.util.vector import Vec2

class UIElement(UIElementContainer):
    def __init__(self, screen, position, dimensions):
        UIElementContainer.__init__(self, position)
        self.screen = screen
        self.dimensions = dimensions
        self.mouse_down_on_element = False

    def on_tick(self, millis):
        pass

    def on_key_down(self, event):
        pass
    def on_key_up(self, event):
        pass
    def on_mouse_moved(self, event):
        if not self.contains_position(event.last_position) and self.contains_position(event.position):
            self.on_mouse_entered(event)
        elif self.contains_position(event.last_position) and not self.contains_position(event.position):
            self.on_mouse_left(event)
        elif self.contains_position(event.last_position) and self.contains_position(event.position):
            self.on_mouse_moved_inside(event)
    def on_mouse_button_down(self, event):
        if self.contains_position(event.position):
            self.mouse_down_on_element = True
            self.on_mouse_down(event)
    def on_mouse_button_up(self, event):
        if self.mouse_down_on_element and self.contains_position(event.position):
            self.on_clicked(event)
        self.mouse_down_on_element = False
        if self.contains_position(event.position):
            self.on_mouse_up(event)
    def on_mouse_wheel_scrolled(self, event):
        if self.contains_position(event.position):
            self.on_mouse_scrolled(event)

    def on_mouse_entered(self, event):
        pass
    def on_mouse_left(self, event):
        pass
    def on_mouse_moved_inside(self, event):
        pass
    def on_mouse_down(self, event):
        pass
    def on_mouse_up(self, event):
        pass
    def on_clicked(self, event):
        pass
    def on_mouse_scrolled(self, event):
        pass


class Button(UIElement):
    def __init__(self, screen, position, dimensions, text):
        super(Button, self).__init__(screen, position, dimensions)

        self.add_rectangle(dimensions, ' ', Color(0, 0, 0), Color(0, 0, 0))

        self.text = text
        self.write_text(text)

        self.base_paint = SolidPaint(Color(200, 200, 200))
        self.hover_paint = SolidPaint(Color(100, 100, 100))
        self.click_paint = SolidPaint(Color(70, 70, 70))
        self.text_base_paint = SolidPaint(Color(255, 255, 255))
        self.text_hover_paint = SolidPaint(Color(255, 255, 255))
        self.text_click_paint = SolidPaint(Color(255, 255, 255))

        self._update_paints()

    def on_clicked(self, event):
        raise NotImplementedError()
    def set_on_clicked(self, func):
        self.on_clicked = types.MethodType(func, self)

    def on_mouse_down(self, event):
        self._update_paints()
    def on_mouse_entered(self, event):
        self._update_paints()
    def on_mouse_left(self, event):
        self._update_paints()
    def on_mouse_button_up(self, event):
        super(Button, self).on_mouse_button_up(event)
        self._update_paints()

    def _update_paints(self):
        if self.mouse_down_on_element:
            self.bg_paint = self.click_paint
            self.fg_paint = self.text_click_paint
        else:
            if self.contains_position(engine.mouse_position):
                self.bg_paint = self.hover_paint
                self.fg_paint = self.text_hover_paint
            else:
                self.bg_paint = self.base_paint
                self.fg_paint = self.text_base_paint
