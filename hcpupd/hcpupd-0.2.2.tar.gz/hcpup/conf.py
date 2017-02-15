# The MIT License (MIT)
#
# Copyright (c) 2017 Thorsten Simons (sw@snomis.de)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import configparser
from collections import OrderedDict
import hcpup
# from .init import TEMPLATE

def readconf(configfile):
    '''
    Read the configuration file and check that all values are available

    :return:    a dict holding the config values
    '''
    must = {'bool': {'src': ['upload existing files',
                             'delete after upload',
                             'remove empty folders after upload'],
                     'tgt': ['ssl', 'obfuscate', 'local DNS resolver'],
                     'meta': ['tag_timestamp'],
                     'log': ['debug']},
            'int': {'tgt': ['upload threads']},
            'str': {'src': ['watchdir'],
                    'tgt': ['namespace', 'path', 'user', 'password'],
                    'meta': ['annotation', 'tag_note'],
                    'log': ['logfile']}
            }

    confp = configparser.ConfigParser()
    if not confp.read(configfile):
        createtemplateconf(configfile)
        sys.exit()

    conf = OrderedDict()
    errors = []
    for c in must.keys():
        for t in must[c].keys():
            for v in must[c][t]:
                try:
                    if c == 'bool':
                        conf[v] = confp.getboolean(t, v)
                    elif c == 'int':
                        conf[v] = confp.getint(t, v)
                    elif c == 'str':
                        conf[v] = confp.get(t, v)
                except configparser.Error:
                    errors.append((t, v, c))

    if errors:
        err = 'Fatal: {} configuration errors\n'.format(len(errors))
        for e in errors:
            err += '\t{}'.format(e)
        sys.exit(err)

    return conf

def createtemplateconf(configfile):
    '''Ask the user if a template config file shall be created and do so...'''
    print('No configuration file found.')
    answer = input('Do you want me to create a template file in the '
                   'current directory (y/n)? ')

    if answer in ['y', 'Y']:
        try:
            with open('.hcpupd.conf', 'w') as outhdl:
                print(hcpup.init.TEMPLATE, file=outhdl)
        except Exception as e:
            sys.exit('fatal: failed to created template file...\n    hint: {}'
                     .format(e))
        else:
            print('\nA template file (.hcpupd.conf) has been created in '
                  'the current directory.')
            print('Please edit it to fit your needs...')
            print()
