"""
This is the main topshape module.

Classes exported here:
 * TopShapeError: application-specific exception class
 * KeyHandler: handles keyboard interactions
 * EdgeText: handles drawing of the edge sections (Header, Footer)
 * BodyBox: handles drawing of the body of the application.
 * TopShape: main class for interacting with topshape
 * CacheThread: Background thread that calls and caches the results of the user
   defined header, footer and body functions
"""

import time
from threading import Thread
from collections import namedtuple
from urwid import AttrMap, Text, CENTER, LEFT, RIGHT, Columns, ListBox,\
    SimpleListWalker, Frame, MainLoop, ExitMainLoop, Filler, Pile, Edit

ALIGNMENT_MAP = {'left': LEFT,
                 'right': RIGHT,
                 'center': CENTER}


class TopShapeError(Exception):
    """topshape's application-specific exception"""

    pass


class Header(Pile):
    """Class that handles input via a line in the header."""
    def __init__(self, *args, **kwargs):
        """Initialize the object."""
        self.app = None
        super(Header, self).__init__(*args, **kwargs)

    def keypress(self, size, key):
        """
        Handles keypresses sent to the header. See Pile.keypress() for details.
        """
        if key != 'enter':
            return super(Header, self).keypress(size, key)

        self.app.current_method(self.app, self.contents[1][0].edit_text)
        self.app.current_method = None

        self.contents[1] = (Text(''), ('pack', None))
        self.app.update()


class CacheThread(Thread):
    """Thread class for running functions and caching the results"""

    def __init__(self, header_func, body_func, footer_func, refresh_rate,
                 *args, **kwargs):
        """
        Initialize the object.

        :param header_func: See TopShape.create_app()
        :type header_func: function
        :param body_func: See TopShape.create_app()
        :type body_func: function
        :param footer_func: See TopShape.create_app()
        :type footer_func: function
        :param refresh_rate: See TopShape.create_app()
        :type refresh_rate: int
        """
        self._header_func = header_func
        self._body_func = body_func
        self._footer_func = footer_func
        self.refresh_rate = refresh_rate

        self.header = None
        self.footer = None
        self.body = None

        self.ran_once = False

        super(CacheThread, self).__init__(*args, **kwargs)

    def run(self):
        """
        Thread's run() method called when start() is called on the Thread
        object.
        """
        while True:
            self.header = self._header_func()
            self.body = self._body_func()
            self.footer = self._footer_func()

            self.ran_once = True

            time.sleep(self.refresh_rate)


class KeyHandler(namedtuple('KeyHandler', 'app key_map')):
    """Class for handling keypresses."""

    def handle(self, key):
        """
        Handle a single keypress.

        :param key: the key that got pressed
        :type key: str
        """
        if key == 'h':
            self.app.enter_help()
            return

        if (key == 'q' or key == 'esc') and self.app.on_help():
            self.app.exit_help()
            return

        method = self.key_map.get(key)

        if method is None:
            return

        if isinstance(method, (tuple, list)):
            self.app.current_method, question = method

            for alarm in self.app.alarms:
                self.app.remove_alarm(alarm)

            edit = Edit(question + ' ')
            self.app.frame.header.contents[1] = (edit, ('pack', None))
            self.app.frame.header.focus_position = 1
        else:
            method(self.app)

        self.app.draw_screen()


class EdgeText(Text):
    """Class of widget used to display the header and footer."""

    def __init__(self, func):
        """
        Initialize the object.

        :param func: function that returns text to be displayed
        :type func: function
        """
        self.func = func
        super(EdgeText, self).__init__('')

    def update(self):
        """Update the text to be displayed."""
        self.set_text(self.func())


class BodyBox(ListBox):
    """Class of widget that displays the body."""

    def __init__(self, columns, func, sorting_column=None,
                 default_column_size=10, default_column_alignment='center',
                 default_column_order='desc'):
        """
        Initialize the object.

        :param columns: tuple (or list) of columns. Each column is a dict
                        with keys 'label', 'size', 'alignment' and 'order'.
                        Only 'label' is required.
        :type columns: tuple (or list) of dicts
        :param func: generator function that returns tuples (or lists) of str
                     objects.
        :type func: function
        :param sorting_column: sorting column
        :type sorting_column: str
        :param default_column_size: default column size
        :type default_column_size: int
        :param default_column_alignment: default column alignment
        :type default_column_alignment: str
        :param default_column_order: default column order. 'asc' or 'desc'
        :type default_column_order: str
        """
        if len(columns) == 0:
            raise TopShapeError('You need at least one column.')
        self.default_column_size = default_column_size
        self.default_column_alignment = default_column_alignment
        self.default_column_order = default_column_order
        self.columns = columns
        self.func = func
        self.sorting_column = sorting_column or columns[0]['label']
        super(BodyBox, self).__init__(SimpleListWalker([]))

    def _sort_key(self, row):
        """
        Sorting key function for rows.

        :param row: a row
        :type row: tuple (or list)
        :return: value of the current sorting column in row
        :rtype: str
        """
        index = self.column_names.index(self.sorting_column)
        for _type in (int, float):
            try:
                return _type(row[index])
            except ValueError:
                pass
        return row[index]

    @property
    def sorting_column(self):
        """
        Return the current sorting column.

        :return: current sorting column
        :rtype: str
        """
        return self._sorting_column

    @sorting_column.setter
    def sorting_column(self, sorting_column):
        """
        Set the current sorting column

        :param sorting_column: column name
        :type sorting_column: str
        """
        if sorting_column not in self.column_names:
            raise TopShapeError('Not a valid body column name.')
        self._sorting_column = sorting_column

    @property
    def column_names(self):
        """
        Return the column names.

        :return: column names
        :rtype: list of str
        """
        return [column['label'] for column in self.columns]

    @property
    def columns(self):
        """
        Return the columns.

        :return: the columns
        :rtype: list of tuples
        """
        return self._columns

    @columns.setter
    def columns(self, columns):
        """
        Set the columns.

        :param columns: the columns to store
        :type columns: list (or tuple) of tuples
        """
        self._columns = []

        for column in columns:
            new_column = {'size': self.default_column_size,
                          'alignment': self.default_column_alignment,
                          'order': self.default_column_order}

            new_column.update(column)

            if 'label' not in new_column.keys():
                raise TopShapeError('Column {} is missing the \'label\' '
                                    'key.'.format(str(new_column)))

            self._columns.append(new_column)

    def update(self):
        """Update the state of the BodyBox object."""
        columns = []
        for column in self.columns:
            label, size, alignment, _ = [column[key] for key in
                                         ('label',
                                          'size',
                                          'alignment',
                                          'order')]
            columns.append((size, AttrMap(Text(('reversed', label),
                                               align=ALIGNMENT_MAP[alignment],
                                               wrap='clip'),
                                          'reversed')))

        # Set the column headers
        self.body[:] = [AttrMap(Columns(columns, 1), 'reversed')]

        column_index = self.column_names.index(self.sorting_column)
        reverse = self.columns[column_index]['order'] == 'desc'
        for row in sorted(self.func(), key=self._sort_key, reverse=reverse):
            columns = []
            for index, column in enumerate(self.columns):
                columns.append((column['size'], Text(row[index],
                                                     align=ALIGNMENT_MAP[
                                                         column['alignment']],
                                                     wrap='clip')))
            self.body.append(Columns(columns, 1))

    def move_sort_right(self):
        """
        Move the sorting column to the right of the current sorting column.
        If the current column is the rightmost column, this results in a no-op.
        """
        index = self.column_names.index(self.sorting_column)
        if index == len(self.column_names)-1:  # we're at the rightmost column
            return
        self.sorting_column = self.column_names[index+1]
        self.update()

    def move_sort_left(self):
        """
        Move the sorting column to the left of the current sorting column.
        If the current column is the leftmost column, this results in a no-op.
        """
        index = self.column_names.index(self.sorting_column)
        if index == 0:  # we're at the leftmost column
            return
        self.sorting_column = self.column_names[index-1]
        self.update()


class TopShape(MainLoop):
    """
    Main class for interacting with topshape.

    You instantiate an object of this class by calling the
    TopShape.create_app() function.
    """

    def __init__(self, frame, key_mapping, refresh_rate, help_text,
                 cache_thread):
        """
        Initialize the object.

        :param frame: frame object
        :type frame: Frame
        :param key_mapping: maps keys to key handler functions
        :type key_mapping: dict
        :param refresh_rate: refresh rate (in seconds)
        :type refresh_rate: int
        :param help_text: text to display in help widget
        :type help_text: str
        """
        self.refresh_rate = refresh_rate
        self.frame = frame
        self._key_handler = KeyHandler(self, key_mapping)
        self.help_text = help_text
        self._saved_widget = None
        self._cache_thread = cache_thread
        self.alarms = []
        palette = [('reversed', 'black', 'light gray')]

        self.frame.header.app = self

        super(TopShape, self).__init__(
            self.frame, palette,
            unhandled_input=self._key_handler.handle)

    def update(self):
        """
        Update the state of the TopShape object and set the next update event.
        """
        self.frame.header.contents[0][0].update()
        self.frame.body.update()
        self.frame.footer.update()

        self.alarms.append(self.set_alarm_in(self.refresh_rate,
                                             lambda x, y: self.update()))

    def run(self):
        """Run the application loop."""
        self._cache_thread.start()

        # Wait until we have something in the cache thread
        while not self._cache_thread.ran_once:
            time.sleep(0.1)

        self.update()
        super(TopShape, self).run()

    def enter_help(self):
        """Cause the help output to be displayed."""
        if self.on_help():
            return
        self._saved_widget = self.widget
        self.widget = Filler(Text(self.help_text), 'top')

    def exit_help(self):
        """Cause the help output to disappear."""
        if not self.on_help():
            return
        self.widget = self._saved_widget
        self._saved_widget = None

    def on_help(self):
        """
        Return whether or not we are currently displaying the help screen.

        :return: True if help screen is currently displayed, False otherwise.
        :rtype: bool
        """
        return isinstance(self.widget, Filler)

    def move_sort_right(self):
        """
        Move the sorting column to the right. Results in no-op if current
        sorting column is the rightmost column.
        """
        if self.on_help():
            return
        self.widget.body.move_sort_right()

    def move_sort_left(self):
        """
        Move the sorting column to the left. Results in no-op if current
        sorting column is the leftmost column.
        """
        if self.on_help():
            return
        self.widget.body.move_sort_left()

    @staticmethod
    def exit():
        """Causes main loop to exit."""
        raise ExitMainLoop()

    @classmethod
    def create_app(cls, columns, body_func, header_func=None,
                   footer_func=None, key_mapping=None, refresh_rate=2,
                   sorting_column=None, help_text=None):
        """
        Function that creates the TopShape object.

        :param columns: tuple (or list) of columns. Each column is a dict
                        with keys 'label', 'size', 'alignment' and 'order'.
                        Only 'label' is required and must be a string.
                        'size' must be an integer and is a number of
                        characters. 'alignment' must be one of 'center',
                        'right' or 'left'. 'order' must be either
                        'asc' or 'desc'
        :type columns: tuple (or list) of dicts
        :param body_func: function that returns tuples (or lists) of strings
                          to be displayed in the body. Each item in the tuple
                          must correspond to a column defined in columns.
                          This function will be called repeatedly at an
                          interval defined by 'refresh_rate'.
        :type body_func: function
        :param header_func: function that returns a string that will be the
                            content of the header section. If not specified,
                            there will be no header section. This function will
                            be called repeatedly at an interval defined by
                            'refresh_rate'.
        :type header_func: function
        :param footer_func: function that returns a string that will be the
                            content of the footer section. If not specified,
                            there will be no footer section. This function will
                            be called repeatedly at an interval defined by
                            'refresh_rate'.
        :type footer_func: function
        :param key_mapping: maps keypresses to functions. When a key is
                            pressed the corresponding function will be called
                            with the the TopShape object as an argument.
                            If key_mapping is None, the mapping will be set to
                            {'q': lambda app: app.exit()}.
        :type key_mapping: dict
        :param refresh_rate: period of the loop in seconds.
        :type refresh_rate: int
        :param sorting_column: name of column to sort by. Must exist in
                               columns.
        :type sorting_column: str
        :param help_text: text to be displayed in the help output.
        :type help_text: str
        :return: the TopShape object
        :rtype: TopShape
        """

        cache_thread = CacheThread(header_func,
                                   body_func,
                                   footer_func,
                                   refresh_rate)
        cache_thread.daemon = True

        header_text = EdgeText(lambda: cache_thread.header)
        header = Header((('pack', header_text), ('pack', Text(''))))

        body = BodyBox(columns, lambda: cache_thread.body, sorting_column)

        footer = EdgeText(lambda: cache_thread.footer)

        frame = Frame(body, header, footer)
        frame.focus_position = 'header'

        if key_mapping is None:
            key_mapping = {'q': lambda app: app.exit()}
        help_text = help_text or ''

        return cls(frame, key_mapping, refresh_rate, help_text, cache_thread)
