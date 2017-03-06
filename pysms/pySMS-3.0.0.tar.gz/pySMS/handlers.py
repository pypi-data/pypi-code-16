# -*- coding: utf-8 -*-

import ctypes
import os
import json

import traceback
import pySMS.messagebox as mbox


class Handles(object):

    def __init__(self):
        self.path = os.path.dirname(os.path.realpath(__file__))

    class Data:

        def __init__(self):
            super(Handles.Data, self).__init__()
            self.path = os.path.dirname(os.path.realpath(__file__))

        def load_json_data(self):
            with open(self.path + '\\html\\pathdata\\json\\siteSettings.json', 'r') as fp:
                return json.load(fp)

    class Errors:

        def __init__(self):
            super(Handles.Errors, self).__init__()

        def err_basic(self, msg, title):
            mbox.msgBox(title, msg, 'MB_OK', 'ICON_STOP')

        def err_traceback(self, e, message):
            mbox.msgBox('Uh Oh!', message + ' Traceback: ' + str(e), 'MB_OK', 'ICON_EXCLAIM')

        def err_full_traceback(self, e, message):
            log = format(str(e))
            log_ = traceback.format_exc()+'.\n'+log
            mbox.msgBox('Uh Oh!', message + ' \n Traceback: ' + str(log_), 'MB_OK', 'ICON_EXCLAIM')

        def err_explicit(self, e, message, title, button, icon):
            mbox.msgBox(title, message + 'Traceback: ' + str(e), button, icon)

        def err_custom(self, message, title, button, icon):
            mbox.msgBox(title, message, button, icon)

    class Helpers:

        def __init__(self):
            super(Handles.Helpers, self).__init__()

        def return_module_path(self):
            import pySMS
            path = pySMS.__file__.split('\\')
            return '\\'.join(path[:len(path) - 1])

