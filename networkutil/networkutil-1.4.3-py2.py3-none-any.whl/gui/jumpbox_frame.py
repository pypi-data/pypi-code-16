
import getpass
import tkMessageBox
from Tkconstants import W, NORMAL
from paramiko import AuthenticationException

import logging_helper
from .._metadata import __version__, __authorshort__, __module_name__
from ..jumpbox import JumpBox
from ..resources import templates, schema
from uiutil.frame.frame import BaseFrame
from uiutil.window.root import RootWindow
from stateutil.incrementor import Incrementor
from configurationutil import Configuration, cfg_params

logging = logging_helper.setup_logging()

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = __module_name__
cfg_params.APP_AUTHOR = __authorshort__
cfg_params.APP_VERSION = __version__

# Set the config initialisation parameters
JUMPBOX_CFG = u'jumpbox_hosts'
TEMPLATE = templates.jumpbox

# Constants for accessing config items
JB_ADDRESS = u'host'
JB_PORT = u'port'
JB_ELEV_USER = u'elevated_user'

# TODO: Add UI to configure the jump hosts (perhaps this could come from a base device frame?)


class JumpboxException(Exception):
    pass


class JumpboxFrame(BaseFrame):

    def __init__(self,
                 jb_class=JumpBox,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self, *args, **kwargs)

        self.jb = None
        self.jb_class = jb_class

        self.jumpbox_config = Configuration()

        # Register configuration
        self.jumpbox_config.register(config=JUMPBOX_CFG,
                                     config_type=cfg_params.CONST.json,
                                     template=TEMPLATE,
                                     schema=schema.jumpbox)

        self.build_jumpbox_frame()

    def build_jumpbox_frame(self):

        BUTTON_WIDTH = 20
        TEXT_FIELD_WIDTH = 22
        LABEL_WIDTH = 20
        COMBO_WIDTH = 21

        LEFT_COL = self.column.start()
        self.columnconfigure(LEFT_COL, weight=1)
        MIDDLE_COL = self.column.next()
        self.columnconfigure(MIDDLE_COL, weight=1)
        RIGHT_COL = self.column.next()
        self.columnconfigure(RIGHT_COL, weight=1)

        LABEL_ROW = self.row.next()
        self.rowconfigure(LABEL_ROW, weight=1)

        self.label(text=u'Username:', width=LABEL_WIDTH, row=LABEL_ROW, column=LEFT_COL, sticky=W)
        self.label(text=u'Password:', width=LABEL_WIDTH, row=LABEL_ROW, column=MIDDLE_COL, sticky=W)
        self.label(text=u'Jumpbox:', width=LABEL_WIDTH, row=LABEL_ROW, column=RIGHT_COL, sticky=W)

        AUTH_ROW = self.row.next()
        self.rowconfigure(AUTH_ROW, weight=1)

        self.__username_var = self.string_var(value=getpass.getuser())

        self.__build = self.entry(textvariable=self.__username_var,
                                  width=TEXT_FIELD_WIDTH,
                                  row=AUTH_ROW,
                                  column=LEFT_COL)

        self.__password_var = self.string_var()

        self.__password = self.entry(textvariable=self.__password_var,
                                     width=TEXT_FIELD_WIDTH,
                                     show=u'*',
                                     row=AUTH_ROW,
                                     column=MIDDLE_COL)

        self.__jumpbox_list_var = self.string_var()

        self.__jumpbox, self.__jumpbox_tooltip = self.combobox(textvariable=self.__jumpbox_list_var,
                                                               width=COMBO_WIDTH,
                                                               postcommand=self.populate_jumpbox_list,
                                                               row=AUTH_ROW,
                                                               column=RIGHT_COL,
                                                               tooltip=u'Select the jumpbox to connect to...')
        self.rowconfigure(self.row.current, weight=1)

        self.populate_jumpbox_list()

        BUTTON_ROW = self.row.next()
        self.rowconfigure(BUTTON_ROW, weight=1)

        self.__connect_button, self.__connect_button_tooltip = self.button(state=NORMAL,
                                                                           text=u'Connect',
                                                                           width=BUTTON_WIDTH,
                                                                           command=self.__connect,
                                                                           row=BUTTON_ROW,
                                                                           column=RIGHT_COL,
                                                                           tooltip=u'Connect to Jumpbox')

    def populate_jumpbox_list(self):

        jumpbox_list = []

        for row in self.jumpbox_config[JUMPBOX_CFG]:
            jumpbox_list.append(row)

        logging.debug(jumpbox_list)

        self.__jumpbox.config(values=jumpbox_list)

        if jumpbox_list:
            self.__jumpbox_list_var.set(jumpbox_list[0])

    def __connect(self):

        jb_name = self.__jumpbox_list_var.get()

        key = u'{c}.{name}'.format(c=JUMPBOX_CFG,
                                   name=jb_name)

        try:
            jb_config = self.jumpbox_config[key]

        except LookupError:
            raise JumpboxException(u'Could not find jumpbox in config!')

        try:
            self.jb = self.jb_class(host=jb_config[JB_ADDRESS],
                                    username=self.__username_var.get(),
                                    password=self.__password_var.get(),
                                    elevated_username=jb_config[JB_ELEV_USER],
                                    port=int(jb_config[JB_PORT]))

            self.__connect_button.config(text=u'Disconnect', command=self.disconnect)

            self.jb.register_observer(self)

            self.notify_observers(jumpbox=self.jb)

        except AuthenticationException as err:
            logging.warning(err)
            tkMessageBox.showerror(title=u'Authentication Error',
                                   message=err,
                                   parent=self)

        except Exception as err:
            logging.exception(err)

    def disconnect(self):

        if self.jb:
            try:
                self.jb.disconnect()
                self.jb = None
                self.__connect_button.config(text=u'Connect', command=self.__connect)

                self.notify_observers(jumpbox=self.jb)

            except Exception as err:
                logging.exception(err)

    def notify(self,
               notifier,
               **params):

        jumpbox = params.get(u'jumpbox')

        # Check for disconnection!
        if not jumpbox.jumpbox_connected:
            self.jb = None
            self.__connect_button.config(text=u'Connect', command=self.__connect)

            self.notify_observers(jumpbox=self.jb)


class ExampleJumpboxFrame(RootWindow):

    def __init__(self, *args, **kwargs):
        super(ExampleJumpboxFrame, self).__init__(*args, **kwargs)

    def _setup(self):
        __row = Incrementor()
        __column = Incrementor()

        self.title(u"Example Jumpbox Frame")

        self.drm = JumpboxFrame(parent=self._main_frame,
                                grid_row=__row.next(),
                                grid_column=__column.current)
