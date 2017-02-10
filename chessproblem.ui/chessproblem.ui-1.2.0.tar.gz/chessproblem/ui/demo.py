
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gdk, Pango

import sys

import chessproblem.model as model
import chessproblem.model.db as db
from chessproblem.model.memory_db import create_memory_db

from .ui_model import ChessProblemModel
from .board import Board

from chessproblem.io import ChessProblemLatexParser

class DemoFrame(object):
    '''
    The main frame of the demonstration application.
    '''
    def __init__(self, cpe_config, filename=None):
        '''
        Initializes the instance.
        '''
        self.cpe_config = cpe_config
        self.db_service = db.DbService(self.cpe_config.database_url)
        self.memory_db_service = create_memory_db(self.cpe_config.config_dir)
        #
        self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.window.set_title("Demobrett")
        self.window.connect("delete_event", self.on_delete)
        self.window.connect("destroy", self.on_destroy)
        self.window_area = Gtk.VBox(False, 0)
        self.window_area.show()
        self.window.add(self.window_area)
        self.model = ChessProblemModel()
        self.model.add_observer(self._on_current_problem_change)
        self._create_menu()
        # Add the menu bar to the window
        self.window_area.pack_start(self.menu_bar, False, False, 0)
        self.base_area = Gtk.HBox(False, 0)
        self.base_area.set_spacing(8)
        self.base_area.show()
        self.window_area.pack_start(self.base_area, True, True, 0)
        self._create_display_area()
        self.base_area.pack_start(self.display_area, True, True, 0)
        self.window.show()
        from os.path import isfile
        if filename == None or not isfile(filename):
            self.set_filename(filename)
            self._on_current_problem_change()
        else:
            self._open_file(filename)

    def _make_title(self, filename='(New)'):
        return 'ChessProblemEditor - %s' % filename

    def set_filename(self, _new_filename):
        '''
        Registers the _new_filename and changes the ui depending on the
        filename.
        '''
        self._filename = _new_filename;
        if self._filename == None:
            self.window.set_title(self._make_title())
        else:
            self.window.set_title(self._make_title('"' + self._filename + '"'))

    def _create_menu(self):
        '''
        Creates our applications main menu.
        '''
        self.menu_bar = Gtk.MenuBar()
        accel_group = Gtk.AccelGroup()
        self.window.add_accel_group(accel_group)

        # Our file menu
        self.file_menu_item = Gtk.MenuItem("File")
        self.file_menu_item.show()
        self.file_menu = Gtk.Menu()
        self.file_menu_item.set_submenu(self.file_menu)
        # file menu items
        self.file_open_item = self._add_menu_item_with_accelerator(
                self.file_menu, 'Open', self.on_file_open, accel_group, ord('O'), Gdk.ModifierType.CONTROL_MASK)
        sep = Gtk.SeparatorMenuItem()
        sep.show()
        self.file_menu.append(sep)
        self.file_exit_item = self._add_menu_item_with_accelerator(
                self.file_menu, 'Exit', self.on_file_exit, accel_group, ord('Q'), Gdk.ModifierType.CONTROL_MASK)
        self.menu_bar.append(self.file_menu_item)

        # Our problems menu
        self.problems_menu_item = Gtk.MenuItem("Problems")
        self.problems_menu_item.show()
        self.problems_menu = Gtk.Menu()
        self.problems_menu_item.set_submenu(self.problems_menu)
        # problems menu items
        self.problems_first_item = self._add_menu_item_with_accelerator(
                self.problems_menu, 'First', self.on_problems_first, accel_group, 65360)
        self.problems_previous_item = self._add_menu_item_with_accelerator(
                self.problems_menu, 'Previous', self.on_problems_previous, accel_group, 65365)
        self.problems_previous_item.set_sensitive(False)
        self.problems_next_item = self._add_menu_item_with_accelerator(
                self.problems_menu, 'Next', self.on_problems_next, accel_group, 65366)
        self.problems_next_item.set_sensitive(False)
        self.problems_last = self._add_menu_item_with_accelerator(
                self.problems_menu, 'Last', self.on_problems_last, accel_group, 65367)
        self.menu_bar.append(self.problems_menu_item)
        self.menu_bar.show()

    def _add_menu_item_with_accelerator(self, menu, label, handler, accel_group, accel_char, key_modifier=0):
        result = self._add_menu_item(menu, label, handler)
        result.add_accelerator('activate', accel_group, accel_char, key_modifier, Gtk.AccelFlags.VISIBLE)
        return result

    def _add_menu_item(self, menu, label, handler):
        result = Gtk.MenuItem(label)
        result.show()
        result.connect('activate', handler, None)
        menu.append(result)
        return result

    def on_problems_first(self, widget, event, data=None):
        '''
        '''
        self.model.first_problem()

    def on_problems_last(self, widget, event, data=None):
        '''
        '''
        self.model.last_problem()

    def on_problems_previous(self, widget, event, data=None):
        '''
        '''
        self.model.previous_problem()

    def on_problems_next(self, widget, event, data=None):
        '''
        '''
        self.model.next_problem()

    def _on_current_problem_change(self):
        '''
        This method is registered as observer to changes to the current selected problem within the list of problems.
        It is used change the display and adjust the statusbar accordingly.
        '''
        current_problem = self.model.current_problem()
        self.board_display.set_chessproblem(current_problem)
        # Adjust enabled/disabled navigation menus
        self.problems_previous_item.set_sensitive(not self.model.is_first_problem())
        self.problems_next_item.set_sensitive(not self.model.is_last_problem())

    def _create_display_area(self):
        '''
        This method creates the area (a VBox), which is used to display all problem information.
        '''
        self.display_area = Gtk.VBox(False, 0)
        self.display_area.show()
        self.board_area = Gtk.Grid()
        self.board_area.show()
        self.display_area.pack_start(self.board_area, False, False, 5)
        self.board_display = Board(self.model.current_problem(), self.cpe_config.image_pixel_size)
        self.board_display.show()
        # self.board_display.set_click_listener(self._on_board_clicked)
        self.board_window = Gtk.Viewport()
        # self.board_window.set_policy(Gtk.PolicyType.ALWAYS, Gtk.PolicyType.ALWAYS)
        _SCROLLED_WINDOW_EXTEND = 4
        self.board_window.add(self.board_display)
        self.board_window.set_size_request(
            self.board_display.get_width() + _SCROLLED_WINDOW_EXTEND,
            self.board_display.get_height() + _SCROLLED_WINDOW_EXTEND)
        self.board_window.show()
        self.board_area.attach(self.board_window, 0, 0, 1, 1)

    def on_file_open(self, widget, event, data=None):
        '''
        Event handler for menu entry File / Open.
        '''
        dialog = Gtk.FileChooserDialog(
                title='Open file', action=Gtk.FileChooserAction.OPEN,
                buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
        dialog.set_default_response(Gtk.ResponseType.OK)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            self._open_file(filename)
        else:
            LOGGER.info('on_file_open: No files selected')
        dialog.destroy()

    def _open_file(self, filename):
        '''
        '''
        self.set_filename(filename)
        with open(filename, 'r', encoding='utf-8') as f:
            s = f.read()
            parser = ChessProblemLatexParser(self.cpe_config, self.memory_db_service)
            document = parser.parse_latex_str(s)
            self.model.set_document(document)

    def on_file_exit(self, widget, event, data=None):
        '''
        Event handler for menu entry File / Exit.
        '''
        self.quit()

    def on_delete(self, widget, event, data=None):
        '''
        Called when the application should be closed.
        '''
        return True

    def on_destroy(self, widget, data=None):
        '''
        Called when the destroy_event occurs.
        '''
        self.quit()

    def quit(self):
        Gtk.main_quit()
        sys.exit(0)

    def main(self):
        Gtk.main()

