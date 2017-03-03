
import logging
from Tkconstants import EW, DISABLED

from .frame import BaseFrame
from ..widget.scroll import TextScroll
from ..helper.text_handler import TextHandler


class LogTickerFrame(BaseFrame):

    def __init__(self,
                 log_level=u'INFO',
                 *args,
                 **kwargs):

        self.__enable_poll = False

        BaseFrame.__init__(self, height=23, *args, **kwargs)

        self.grid(sticky=EW)
        self.grid_propagate(0)

        LEFT_COL = self.column.start()
        self.columnconfigure(LEFT_COL, weight=1)

        TEXT_ROW = self.row.start()
        self.rowconfigure(TEXT_ROW, weight=1)

        # Create the text
        self.log_text = TextScroll(self,
                                   state=DISABLED,
                                   vbar=False,
                                   hbar=False)
        self.log_text.grid(row=TEXT_ROW, column=LEFT_COL, sticky=EW)
        self.log_text.configure(font=u'TkFixedFont', background=u'#E7E7E7')

        # Create textLogger
        self.text_handler = TextHandler(self.log_text)
        self.text_handler.setFormatter(self.setup_ticker_format())
        self.text_handler.setLevel(log_level)

        # Add the handler to root logger
        logger = logging.getLogger()
        logger.addHandler(self.text_handler)

        self.__enable_poll = True

    def poll(self):
        if self.__enable_poll:
            self.text_handler.poll()

    @staticmethod
    def setup_ticker_format():

        # Setup formatter to define format of log messages
        format_string = u'{timestamp} - {level} : {msg}'.format(timestamp=u'%(asctime)s',
                                                                level=u'%(levelname)-7s',
                                                                msg=u'%(message)s')

        log_formatter = logging.Formatter(fmt=format_string,
                                          datefmt=u'%H:%M:%S')

        return log_formatter

