
import ttk

from ..mixin import AllMixIn


class BaseLabelFrame(AllMixIn,
                     ttk.Labelframe):

    def __init__(self,
                 parent,
                 grid_row=0,
                 grid_column=0,
                 *args,
                 **kwargs):

        self._grid_row = grid_row
        self._grid_column = grid_column

        # Unfortunately everything Tkinter is written in Old-Style classes so it doesn't work with super!
        ttk.LabelFrame.__init__(self, master=parent, **kwargs)

        super(BaseLabelFrame, self).__init__(parent=parent,
                                             text=u'Base Label Frame:',
                                             *args,
                                             **kwargs)

    def _set_title(self, title):
        self.config(text=title)
