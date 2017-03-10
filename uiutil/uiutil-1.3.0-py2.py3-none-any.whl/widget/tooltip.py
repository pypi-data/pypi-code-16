# encoding: utf-8
# Description:
# Author: Hywel Thomas
# Mods:

try:
    # for Python2
    import Tkinter as tk

except ImportError:
    # for Python3
    import tkinter as tk

u"""
Tooltip.

Places a tooltip near the pointer.

Attempts best fit based on available space above, below, left right
of the pointer, not the control.

Will reduce the font size repeatedly if it doesn't fit.

If it still doesn't fit after reducing to minimum font size,
defaults to the right.

Note that the height and width are estimated based on pixels on Windows 7 for
Courier and Times fonts only. These may differ on other platforms. This could
cause the tooltip to overlay the cursor if positioned above or to the left on
other platforms or with other fonts. That would cause the tooltip to close and
may appear to flicker. Right and below are favoured for this reason.

"""

import logging_helper

logging = logging_helper.setup_logging()

POINTER_SIZE = 20
NAME = 0
POINTS = 1
WEIGHT = 2
WIDTH = 0
HEIGHT = 1

MINIMUM_FONT_SIZE = 8

ESTIMATED_SIZE = {
    u'times': {
        u'6':  (1920 / 478, 1200 / 119),
        u'7':  (1920 / 383, 1200 / 99),
        u'8':  (1920 / 319, 1200 / 85),
        u'10': (1920 / 319, 1200 / 80),
        u'12': (1920 / 239, 1200 / 63)
    },
    u'courier': {
        u'6':  (1920 / 383, 1200 / 149),
        u'7':  (1920 / 383, 1200 / 99),
        u'8':  (1920 / 273, 1200 / 85),
        u'10': (1920 / 239, 1200 / 75),
        u'12': (1920 / 191, 1200 / 66)
    }
}


def estimate_line_height(font):

    try:
        return ESTIMATED_SIZE[font[NAME]][font[POINTS]][HEIGHT]

    except KeyError:
        pass

    try:
        return ESTIMATED_SIZE[u'times'][POINTS][HEIGHT]

    except KeyError:
        return ESTIMATED_SIZE[u'times'][u'10'][HEIGHT]


def estimate_line_width(font):
    try:
        return ESTIMATED_SIZE[font[NAME]][font[POINTS]][WIDTH]

    except KeyError:
        pass

    try:
        return ESTIMATED_SIZE[u'times'][POINTS][WIDTH]

    except KeyError:
        return ESTIMATED_SIZE[u'times'][u'10'][WIDTH]


def reduce_font_size(font):
    try:
        sizes = [int(size) for size in ESTIMATED_SIZE[font[NAME]]]

    except KeyError:
        sizes = [6, 7, 8, 10, 12]

    current_size = int(font[POINTS])

    if current_size == MINIMUM_FONT_SIZE:
        raise ValueError(u'minimum font size')

    while True:
        current_size -= 1

        if current_size in sizes or current_size == MINIMUM_FONT_SIZE:
            break

    font = (font[NAME], str(current_size), font[WEIGHT])

    return font


class ToolTip(object):

    """
    create a tooltip for a given widget
    '__text' can be a string or a function
    that returns the tooltip __text.
    The *args and *kwargs will be passed
    to the function.
    """

    def __init__(self,
                 widget,
                 text=u'widget info',
                 font=(u"courier", u"10", u"normal"),
                 observe=None,
                 text_colour=u'black',
                 background_colour=u'#ffffaf',
                 justify=u"center",
                 show_when_widget_is_disabled=False,
                 *args,
                 **kwargs):

        self.widget = widget
        self.screen_width = self.widget.winfo_screenwidth()
        self.screen_height = self.widget.winfo_screenheight()
        self.args = args
        self.kwargs = kwargs
        self.update_label(text)
        self.widget.bind(u"<Enter>", self.enter)
        self.widget.bind(u"<Leave>", self.close)
        self.__text = text
        self.font = font
        self.text_colour = text_colour
        self.background_colour = background_colour
        self.justify = justify
        self.show_when_widget_is_disabled = show_when_widget_is_disabled

        if observe is not None:
            observe.register_observer(self)

    @property
    def widget_is_disabled(self):
        try:
            if self.widget.cget(u'state').string == u'disabled':
                return True

        except AttributeError:
            if self.widget.cget(u'state') == u'disabled':
                return True

        return False

    def enter(self,
              event=None):

        self.close()

        if not self.show_when_widget_is_disabled:
            if self.widget_is_disabled:
                    return

        text_value = self.text

        if isinstance(text_value, dict):
            text = text_value.get(u'text',
                                  u'*tooltip error*')

            justify = text_value.get(u'justify',
                                     self.justify)

            background_colour = text_value.get(u'background_colour',
                                               self.background_colour)

            text_colour = text_value.get(u'text_colour',
                                         self.text_colour)

            font = text_value.get(u'font',
                                  self.font)

        else:
            text = unicode(text_value)
            justify = self.justify
            background_colour = self.background_colour
            text_colour = self.text_colour
            font = self.font

        if text:
            x, y, font = self.__best_position(text=text,
                                              font=font)
            # self.widget.cget('state')
            # creates a toplevel window
            self.tw = tk.Toplevel(self.widget)
            # Leaves only the label and removes the app window
            self.tw.wm_overrideredirect(True)
            self.tw.wm_geometry(u"+%d+%d" % (x, y))
            self.label = tk.Label(self.tw,
                                  justify=justify,
                                  background=background_colour,
                                  foreground=text_colour,
                                  font=font)
            self.label.config(text=text)
            self.label.pack(ipadx=1)

    def __fits(self,
               height,
               width,
               left_space,
               right_space,
               top_space,
               bottom_space):

        if height <= bottom_space and width <= self.screen_width:
            return u'under'

        if width <= right_space and height <= self.screen_height:
            return u'right'

        if height <= top_space and width <= self.screen_width:
            return u'above'

        if width <= left_space and height <= self.screen_height:
            return u'left'

    def __best_position(self,
                        text,
                        font=None):

        pointer_x = self.widget.winfo_pointerx()
        pointer_y = self.widget.winfo_pointery()

        left_space = pointer_x - POINTER_SIZE
        right_space = self.screen_width - pointer_x - POINTER_SIZE
        top_space = pointer_y - POINTER_SIZE
        bottom_space = self.screen_height - pointer_y - POINTER_SIZE

        width = max([len(line) for line in text.splitlines()])

        line_count = len(text.splitlines())

        font = (font
                if font
                else self.font)

        while True:
            pixel_height = estimate_line_height(font) * line_count
            pixel_width = estimate_line_width(font) * width
            fits = self.__fits(height=pixel_height,
                               width=pixel_width,
                               left_space=left_space,
                               right_space=right_space,
                               top_space=top_space,
                               bottom_space=bottom_space)

            if fits:
                break

            try:
                font = reduce_font_size(font)

            except ValueError:
                break

        if not fits:
            fits = u'right'

        if fits == u'right':
            x = pointer_x + POINTER_SIZE

        if fits == u'left':
            x = pointer_x - POINTER_SIZE - pixel_width

        if fits == u'under':
            y = pointer_y + POINTER_SIZE

        if fits == u'above':
            y = pointer_y - POINTER_SIZE - pixel_height

        if fits in (u'left', u'right'):
            y = pointer_y - pixel_height / 2
            bottom_posn = y + pixel_height

            if bottom_posn > self.screen_height:
                # position at the bottom
                y = self.screen_height - pixel_height

            if y < 0:
                # position at the top (may cut off below the display)
                y = 0

        if fits in (u'above', u'under'):
            x = pointer_x - pixel_width / 2
            right_posn = x + pixel_width

            if right_posn > self.screen_width:
                # position at the bottom
                x = self.screen_width - pixel_width

            if x < 0:
                # position at the top (may cut off below the display)
                x = 0

        return x, y, font

    def update_label(self,
                     text=None):

        """
        Call this to update either the __text string
        or __text function used to up date the tooltip __text
        """

        if text is not None:
            self.text = text

    @property
    def text(self):

        if isinstance(self.__text, basestring):
            return self.__text

        else:
            # assume that it's a function
            return self.__text(*self.args,
                               **self.kwargs)

    @text.setter
    def text(self,
             value_or_function):
        self.__text = value_or_function

    def notify(self,
               *args,
               **kwargs):

        """
        To use notify to update based on changes in another component, the
        tooltip should be set up with __text as a function, not a value.
        Any arguments will be tossed.
        The notification is just a trigger.
        """

        self.update_label()

    def close(self,
              event=None):

        try:
            if self.tw:
                self.tw.destroy()

        except AttributeError:
            pass


if __name__ == u"__main__":
    from Tkinter import *

    master = Tk()

    def callback():
        print "click!"

    b = Button(master, text=u"OK", command=callback)

    w = 50
    h = 150
    lines = [str(i) + u'.' * (w - len(str(i))) for i in xrange(h)]

    STB_COLOURS = {u'text_colour':       u'white',
                   u'background_colour': u'dark blue'}

    ToolTip(widget=b,
            text=u'\n'.join(lines),
            font=(u"courier", u'12', u"normal"),
            **STB_COLOURS)
    b.pack()

    mainloop()
