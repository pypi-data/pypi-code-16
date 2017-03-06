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
from hcpup.init import CONF

def readconf(configfile):
    '''
    Read the configuration file and check that all values are available

    :return:    a dict holding the config values
    '''

    confp = configparser.ConfigParser()
    if not confp.read(configfile):
        createtemplateconf(configfile)
        sys.exit()

    conf = OrderedDict()
    errors = []

    for s in CONF.keys():
        for p in CONF[s].keys():
            try:
                if CONF[s][p].type == 'bool':
                    conf[p] = confp.getboolean(s, p)
                elif CONF[s][p].type == 'float':
                    conf[p] = confp.getfloat(s, p)
                elif CONF[s][p].type == 'int':
                    conf[p] = confp.getint(s, p)
                elif CONF[s][p].type == 'str':
                    conf[p] = confp.get(s, p)
            except configparser.Error as y:
                print(y)
                if CONF[s][p].req:
                    errors.append(('['+s+']', p, CONF[s][p].type))
                else:
                    conf[p] = None
    if errors:
        err = 'Fatal: {} configuration errors'.format(len(errors))
        for e in errors:
            err += '\n\t{:>8}:\t{}\t{}'.format(e[2],e[0],e[1])
        sys.exit(err)

    return conf

def createtemplateconf(configfile):
    '''
    Ask the user if a template config file shall be created and do so...
    '''
    print('No configuration file found.')
    answer = input('Do you want me to create a template file in the '
                   'current directory (y/n)? ')

    if answer in ['y', 'Y']:
        try:
            with open('.hcpupd.conf', 'w') as outhdl:
                for s in CONF.keys():
                    print('[{}]'.format(s), file=outhdl)
                    for p in CONF[s].keys():
                        print('{} = {}'.format(p, CONF[s][p].example),
                              file=outhdl)
                    print(file=outhdl)
        except Exception as e:
            sys.exit('fatal: failed to created template file...\n    hint: {}'
                     .format(e))
        else:
            print('\nA template file (.hcpupd.conf) has been created in '
                  'the current directory.')
            print('Please edit it to fit your needs...')
            print()
