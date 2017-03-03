
import ttk
from Tkconstants import NONE, RIGHT, Y, HORIZONTAL, BOTTOM, X, LEFT, BOTH
from Tkinter import Text, Scrollbar, Pack, Grid, Place


class TextScroll(Text):

    def __init__(self,
                 master=None,
                 vbar=True,
                 hbar=True,
                 *args,
                 **kwargs):

        # Setup a dummy frame
        self.frame = ttk.Frame(master)

        kwarg_upd = {u'wrap': NONE}

        if vbar:
            self.vbar = Scrollbar(self.frame)
            self.vbar.pack(side=RIGHT, fill=Y)
            self.vbar[u'command'] = self.yview
            kwarg_upd[u'yscrollcommand'] = self.vbar.set

        if hbar:
            self.hbar = Scrollbar(self.frame, orient=HORIZONTAL)
            self.hbar.pack(side=BOTTOM, fill=X)
            self.hbar[u'command'] = self.xview
            kwarg_upd[u'xscrollcommand'] = self.hbar.set

        kwargs.update(kwarg_upd)

        Text.__init__(self, self.frame, *args, **kwargs)

        self.pack(side=LEFT, fill=BOTH, expand=True)

        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = vars(Text).keys()
        methods = vars(Pack).keys() + vars(Grid).keys() + vars(Place).keys()
        methods = set(methods).difference(text_meths)

        for m in methods:
            if m[0] != u'_' and m != u'config' and m != u'configure':
                setattr(self, m, getattr(self.frame, m))

    def __str__(self):
        return str(self.frame)
