# -*- coding: utf-8 -*-
import os
import yaml


DEFAULT_CONF = {
    'url': 'http://cofo.cf/api.php/',
    'cookies': {'__test': 'd831f6b86960ab065808406a5c3063bf'},
    'table': 't2',
}


class Config(object):

    def __init__(self):

        conf_path = os.path.expanduser("~/.pystoreql.yml")

        if os.path.isfile(conf_path):
            with open(conf_path, 'rb') as fo:
                conf = yaml.load(fo)
        else:
            assert not os.path.exists(conf_path)
            with open(conf_path, 'wb') as fo:
                fo.write(yaml.dump(DEFAULT_CONF))
            conf = DEFAULT_CONF

        for k, v in conf.items():
            setattr(self, k, v)
        assert self.url and self.table
