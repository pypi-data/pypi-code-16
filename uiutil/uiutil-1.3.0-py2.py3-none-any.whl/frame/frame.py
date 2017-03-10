
import ttk

from ..mixin import AllMixIn


class BaseFrame(ttk.Frame,
                AllMixIn):

    def __init__(self,
                 parent,
                 grid_row=0,
                 grid_column=0,
                 *args,
                 **kwargs):

        # TODO: Is this style actually used anywhere?
        style = ttk.Style()
        style.configure(u"ActiveRow.TRadiobutton", foreground=u"blue")
        style.configure(u"ActiveRow.TButton", foreground=u"blue")
        style.configure(u"ActiveRow.TLabel", foreground=u"blue")

        self._grid_row = grid_row
        self._grid_column = grid_column

        # Unfortunately everything Tkinter is written in Old-Style classes so it blows up if you use super!
        ttk.Frame.__init__(self, master=parent, **kwargs)
        AllMixIn.__init__(self, parent=parent, **kwargs)

        self.grid(row=self._grid_row,
                  column=self._grid_column,
                  padx=5,
                  pady=5)

        self._poll()

    def modal_window(self,
                     window):

        window.transient()
        window.grab_set()
        self.wait_window(window)
