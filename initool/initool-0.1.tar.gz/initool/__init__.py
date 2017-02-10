#!/usr/bin/env python3
from sys import argv, stdout, stdin
import argparse
import json
from configparser import ConfigParser

"""
initool set section/option value 
initool get section/option  
initool rm section/option value

"""

class INITool:
    def __init__(self, src):
        """
        @param src string: ini content.
        """
        self.__cfg = ConfigParser()
        # try loading src if its json
        try:
            confdict = json.loads(src)
            self.__cfg.read_dict(confdict)
        except:
            self.__cfg.read_string(src)

    def get_option(self, section, option, showjson=False):
        if showjson:
            return json.dumps(self.__cfg.get(section, option))
        else:
            return self.__cfg.get(section, option)

    def get_section(self, section, showjson=False):
        if showjson:
            return json.dumps(list(self.__cfg.items(section)))
        else:
            res = ""
            for opt, val in self.__cfg.items(section):
                res += opt + "=" + val + "\n"
            
            return res

    def rm_option(self, section, option):
        self.__cfg.remove_option(section, option)

    def rm_section(self, section):
        self.__cfg.remove_section(section)
    
    def set_option(self, section, option, value):
        self.__cfg.set(section, option, value)

    def get_sections(self):
        return self.__cfg.sections

    def as_dict(self):
        obj = {}
        for sect in self.__cfg.sections():
            obj[sect] = {}
            for key, value in self.__cfg.items(sect):
                obj[sect][key] = value

        return obj

    def as_json(self):
        return json.dumps(self.as_dict())

    def show(self, showjson=False):
        if showjson:
            print(self.as_json())
        else:
            self.__cfg.write(stdout)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subparsers')

    getparser = subparsers.add_parser("get", help="get value of an option formatted as section/option")
    getparser.add_argument('-j', "--json", default=False, action="store_true", help="renders ini as json.")

    showparser = subparsers.add_parser("show", help="renders ini file (accepts --json as argument)")
    showparser.add_argument('-j', "--json", default=False, action="store_true", help="renders ini as json.")

    setparser = subparsers.add_parser("set", help="set value of an option formatted as section/option")
    setparser.add_argument('-j', "--json", default=False, action="store_true", help="show output as json.")

    rmparser = subparsers.add_parser("rm", help="remove section or section/option")
    rmparser.add_argument('-j', "--json", default=False, action="store_true", help="show output as json.")


    parsed, args = parser.parse_known_args(argv[1:])
    initool = INITool(stdin.read())
    #print(dir(parsed))
    if parsed.subparsers == 'get':
        showjson = parsed.json
        # sec/key 
        # sec
        key = args[0]
        if "/" in key:
            print(initool.get_option(*key.split("/"), showjson=False))
        else:
            print(initool.get_section(key, showjson))
    elif parsed.subparsers == 'show':
        showjson = parsed.json
        initool.show(showjson)
    elif parsed.subparsers == 'set':
        # sec/key value
        showjson = parsed.json
        key = args[0]
        initool.set_option(*key.split("/"), args[1])
        initool.show(showjson)
    elif parsed.subparsers == 'rm':
        showjson = parsed.json 
        # section
        # section/option
        key = args[0]
        if "/" in key: #want to delete an option
            initool.rm_option(*key.split("/"))
        else:
            initool.rm_section(key)
        initool.show(showjson)

if __name__ == "__main__":
    main()