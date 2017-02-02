#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import os

import sys
from copy import deepcopy

import yaml

__author__ = 'Marco Bartel'

LOG = logging.getLogger(__name__)


class XYaml(object):
    @classmethod
    def merge(cls, a, b, path=None, update=True):
        if path is None: path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    cls.merge(a[key], b[key], path + [str(key)])
                elif a[key] == b[key]:
                    pass
                elif isinstance(a[key], list) and isinstance(b[key], list):
                    a[key] = b[key]
                elif update:
                    a[key] = b[key]
                else:
                    raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
            else:
                a[key] = b[key]
        return a

    @classmethod
    def _load(cls, filePath=None):
        includes = []
        lineData = []
        mixins = {}

        dictData = {}
        fd = open(filePath, "r")
        data = fd.read()
        fd.close()

        sd = data.splitlines()
        for l in sd:
            if l.strip().startswith("{%"):
                cmd, parameters = cls.extractCommand(l)
                if cmd == "include":
                    incFilePath = parameters[0]
                    if not os.path.isabs(incFilePath):
                        incFilePath = os.path.join(os.path.dirname(filePath), incFilePath)
                    includes.append(incFilePath)
                elif cmd == "mixin":
                    pass

            else:
                lineData.append(l)

        for incFilePath in includes:
            incData, mixins = cls._load(filePath=incFilePath)
            if incData:
                cls.merge(dictData, incData)

        loaded = yaml.load("\n".join(lineData))
        if loaded:
            cls.merge(dictData, loaded)

        return dictData, mixins

    @classmethod
    def load(cls, filePath):
        absFilePath = os.path.abspath(filePath)
        LOG.debug("loading {abs}".format(abs=absFilePath))
        ret, mixins = cls._load(absFilePath)
        return ret

    @classmethod
    def extractCommand(cls, line):
        cmdline = line.strip().split()
        cmdsplit = []
        write = False
        for d in cmdline:
            if write:
                if d == "%}":
                    write = False
                    continue
                else:
                    cmdsplit.append(d)

            if d == "{%":
                write = True

        return cmdsplit[0].lower(), cmdsplit[1:]


load = XYaml.load


if __name__=="__main__":
    filePath = sys.argv[-1]
    config = load(filePath=filePath)
    print(json.dumps(config, sort_keys=True, indent=4))