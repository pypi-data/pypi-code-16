import os
import shutil
import sqlite3

import logging_helper
from fdutil.dict_tools import filter_dict
from fdutil.path_tools import ensure_path_exists, pop_path
from configurationutil.cfg_objects.configuration_object import ConfigObject

__author__ = u'Oli Davis'
__copyright__ = u'Copyright (C) 2016 Oli Davis'

logging = logging_helper.setup_logging()

TEMPLATE = u'sqlite3_config_default.db'


class Sqlite3Config(ConfigObject):

    DEFAULT_TEMPLATE = os.path.join(pop_path(__file__), TEMPLATE)

    def __init__(self,
                 *args,
                 **kwargs):

        """ Initialise JSON Config class """

        self.database_connection = None
        self.database_cursor = None
        self.db_open = False
        self.auto_save = False
        self.last_select_table = None

        super(Sqlite3Config, self).__init__(*args, **kwargs)

    # ========================== REQUIRED METHODS ============================
    def _load_config(self,
                     create):

        """ Load config file

        :param create: When True file will be created if it doesn't already exist.
        """

        logging.debug(self._config_file)

        # If file doesn't exist create it
        if not os.path.exists(self._config_file) and create:
            ensure_path_exists(pop_path(self._confile_file))

            # Copy the template into config file location
            shutil.copyfile(self.DEFAULT_TEMPLATE, self._config_file)

    def save(self):

        """ Update config file """

        logging.info(u'Updating config file: {f}'.format(f=self._config_file))
        logging.debug(u'Value: {f}'.format(f=self.cfg))

        self.database_connection.commit()

    def find(self,
             filters):

        """ Get a filtered list of config items

        :param filters: List of filter tuples.
                        Tuple format: (Search Key, Search Value, Condition)
                        First should not have a condition
                        i.e [("A", 123), ("A", 789, u'AND')]
        :return: dict containing the subset of matching items
        """

        return filter_dict(src_dict=self.cfg,  # TODO
                           filters=filters)

    def __getitem__(self, item):
        self.open()

        output = self.cfg[item]  # TODO

        self.close()

        return output

    def __setitem__(self, key, value):
        self.open()

        self.cfg[key] = value  # TODO
        self.save()

        self.close()

    def __delitem__(self, key):
        self.open()

        del self.cfg[key]  # TODO
        self.save()

        self.close()

    def __iter__(self):
        return iter(self.cfg)  # TODO

    def __len__(self):
        return len(self.cfg)  # TODO

    @property
    def cfg(self):
        return self._cfg

    @ConfigObject.cfg.setter
    def cfg(self, value):
        self._cfg = value

    # ========================== ADDITIONAL METHODS ============================
    def open(self):

        if self.database_connection is None:
            try:
                self.database_connection = sqlite3.connect(self._config_file)
                self.db_open = True

            except Exception:
                logging.error(u'Cannot open database {path}.'.format(path=self._config_file))
                raise

        if self.db_open:
            self.set_cursor()

    def close(self):

        try:
            self.database_cursor.close()
            self.database_connection.close()

        except Exception as err:
            logging.debug(err)

        finally:
            self.database_connection = None
            self.database_cursor = None
            self.db_open = False

    def set_cursor(self):
        logging.debug(u'Setting Cursor')
        self.database_cursor = self.database_connection.cursor()

    def get_cursor(self):
        return self.database_cursor
