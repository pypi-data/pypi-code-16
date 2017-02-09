# -*- coding: utf-8 -*-
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0
import os

class cfg():
        
    def configparse(section, a, b):
        config = ConfigParser()
        file = os.path.expanduser(os.sep.join(["~","pysms","pysms","html","htmlConfig.cfg"]))
        config.read(file)
        string = config.items(section)[a][b]
        return string
        
    def configwriter(dictMain, fname, flocation):
        config = ConfigParser()
        for key, val in dictMain.items():
            config[key] = val
            with open(flocation + '\\' + fname, 'w')as configfile:
                config.write(configfile)
        