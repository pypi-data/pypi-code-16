
from Tkconstants import HORIZONTAL, EW

from .frame import BaseFrame


class LoadingFrame(BaseFrame):

    def __init__(self, wait_func=None, *args, **kwargs):

        self.wait_func = wait_func

        super(LoadingFrame, self).__init__(*args, **kwargs)

        self.progress = self.progressbar(length=280,
                                         orient=HORIZONTAL,
                                         mode=u'indeterminate',
                                         sticky=EW)
        self.progress.start()

        if self.wait_func is not None:
            self.after(ms=250, func=self.run)

    def run(self):
        self.wait_func()
        self.parent.master.destroy()
