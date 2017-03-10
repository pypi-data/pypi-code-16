
import ttk

from ..mixin import AllMixIn


class BaseLabelFrame(ttk.Labelframe,
                     AllMixIn):

    def __init__(self,
                 parent,
                 grid_row=0,
                 grid_column=0,
                 *args,
                 **kwargs):

        self._grid_row = grid_row
        self._grid_column = grid_column

        # Unfortunately everything Tkinter is written in Old-Style classes so it blows up if you use super!
        ttk.LabelFrame.__init__(self, master=parent, **kwargs)
        AllMixIn.__init__(self, parent=parent, **kwargs)

        self.grid(row=self._grid_row,
                  column=self._grid_column,
                  padx=5,
                  pady=5)

        self._poll()

    def _set_title(self, title):
        self.config(text=title)

    def modal_window(self,
                     window):

        window.transient()
        window.grab_set()
        self.wait_window(window)
