
import os
import json

import logging_helper
from configuration_object import ConfigObject
from fdutil.dict_tools import filter_dict
from fdutil.parse_json import write_json_to_file
from fdutil.path_tools import ensure_path_exists, pop_path

__author__ = u'Oli Davis'
__copyright__ = u'Copyright (C) 2016 Oli Davis'

logging = logging_helper.setup_logging()

TEMPLATE = u'json_config_default.json'


class JSONConfig(ConfigObject):

    DEFAULT_TEMPLATE = os.path.join(pop_path(__file__), TEMPLATE)

    def __init__(self,
                 *args,
                 **kwargs):

        """ Initialise JSON Config class """

        super(JSONConfig, self).__init__(*args, **kwargs)

    def _load_config(self,
                     create):

        """ Load config file

        :param create: When True file will be created if it doesn't already exist.
        """

        logging.debug(self._config_file)

        # If file doesn't exist create it
        if not os.path.exists(self._config_file) and create:
            pth = self._config_file.split(os.sep)
            fn, ext = pth.pop().split(u'.')

            pth = os.sep.join(pth)

            ensure_path_exists(pth)

            # Load the template
            template = json.load(open(self.DEFAULT_TEMPLATE))

            # Create the file
            write_json_to_file(content=template,
                               output_dir=pth,
                               filename=fn,
                               file_ext=ext)

        self.cfg = json.load(open(self._config_file))

    def save(self):

        """ Update config file """

        logging.info(u'Updating config file: {f}'.format(f=self._config_file))
        logging.debug(u'Value: {f}'.format(f=self.cfg))

        path, fn = os.path.split(self._config_file)
        fn, ext = fn.split(u'.')

        write_json_to_file(content=self.cfg,
                           output_dir=path,
                           filename=fn,
                           file_ext=ext)

    def find(self,
             filters):

        """ Get a filtered list of config items

        :param filters: List of filter tuples.
                        Tuple format: (Search Key, Search Value, Condition)
                        First should not have a condition
                        i.e [("A", 123), ("A", 789, u'AND')]
        :return: dict containing the subset of matching items
        """

        return filter_dict(src_dict=self.cfg,
                           filters=filters)

    def __getitem__(self, item):
        return self.cfg[item]

    def __setitem__(self, key, value):
        self.cfg[key] = value
        self.save()

    def __delitem__(self, key):
        del self.cfg[key]
        self.save()

    def __iter__(self):
        return iter(self.cfg)

    def __len__(self):
        return len(self.cfg)
