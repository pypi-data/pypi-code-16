
import logging
import ttk
from Tkconstants import E, W, NSEW, NORMAL, DISABLED

from .frame import BaseFrame
from ..widget.scroll import TextScroll
from ..helper.text_handler import TextHandler


class LogFrame(BaseFrame):

    def __init__(self,
                 *args,
                 **kwargs):

        self.__enable_poll = False

        BaseFrame.__init__(self, *args, **kwargs)

        BUTTON_WIDTH = 20

        LEFT_COL = self.column.start()
        MIDDLE_COL = self.column.next()
        RIGHT_COL = self.column.next()
        self.columnconfigure(RIGHT_COL, weight=1)

        LEVEL_ROW = self.row.next()

        ttk.Label(self, text=u'Log Level:').grid(row=LEVEL_ROW, column=LEFT_COL, sticky=W)

        self.level_list = [u'DEBUG',
                           u'INFO',
                           u'WARNING',
                           u'ERROR',
                           u'CRITICAL']

        self.__level_var = self.string_var(value=u'INFO',
                                           trace=self.__level_change)
        self.__level = self.combobox(textvariable=self.__level_var,
                                     values=self.level_list,
                                     row=LEVEL_ROW,
                                     column=MIDDLE_COL,
                                     sticky=W)

        self.__clear_button, self.__clear_button_tooltip = self.button(state=NORMAL,
                                                                       text=u'Clear',
                                                                       width=BUTTON_WIDTH,
                                                                       command=self.__clear,
                                                                       row=LEVEL_ROW,
                                                                       column=RIGHT_COL,
                                                                       sticky=E,
                                                                       tooltip=u'Clear the log window')

        CONFIG_ROW = self.row.next()
        self.rowconfigure(CONFIG_ROW, weight=1)
        self.log_text = TextScroll(self, state=DISABLED)
        self.log_text.grid(row=CONFIG_ROW, column=LEFT_COL, columnspan=3, sticky=NSEW)
        self.log_text.configure(font=u'TkFixedFont')

        # Create textLogger
        self.text_handler = TextHandler(self.log_text)
        self.text_handler.setLevel(self.__level_var.get())

        # Add the handler to root logger
        logger = logging.getLogger()
        logger.addHandler(self.text_handler)

        self.__enable_poll = True

    def __level_change(self):
        self.text_handler.setLevel(self.__level_var.get())

    def __clear(self):
        self.text_handler.clear()

    def poll(self):
        if self.__enable_poll:
            self.text_handler.poll()
