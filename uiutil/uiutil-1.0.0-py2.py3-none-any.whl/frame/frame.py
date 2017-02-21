
import ttk

from ..mixin import AllMixIn


class BaseFrame(AllMixIn,
                ttk.Frame):

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

        # Unfortunately everything Tkinter is written in Old-Style classes so it doesn't work with super!
        ttk.Frame.__init__(self, master=parent, **kwargs)

        super(BaseFrame, self).__init__(parent=parent,
                                        *args,
                                        **kwargs)
