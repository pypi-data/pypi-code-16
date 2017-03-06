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

from os.path import expanduser
from collections import namedtuple, OrderedDict as OD

# initialized needed variables
#
class Gvars:
    """
    Holds constants and variables that need to be present within the
    whole project.
    """

    # version control
    s_version = "0.2.3"
    s_builddate = '2017-03-01'
    s_build = "{}/Sm".format(s_builddate)
    s_minPython = "3.4.3"
    s_description = "hcpupd"
    s_dependencies = ['']

    # constants
    Version = "v.{} ({})".format(s_version, s_build)
    Description = 'hcpupd - HCP upload daemon'
    Author = "Thorsten Simons"
    AuthorMail = "sw@snomis.de"
    AuthorCorp = ""
    AppURL = ""
    License = ""
    Executable = "hcpupd"


CONFIGFILE = ['/var/lib/misc/hcpupd.conf', expanduser('~/.hcpupd.conf'),
              '.hcpupd.conf']

# This describes what we expect from the configuration file, and will be used
# to create a template as well:
ci = namedtuple('ci', ['type', 'req', 'example'])
CONF = OD([('src', OD([('watchdir', ci('str', True, '/watchdir')),
                       ('upload existing files', ci('bool', True, 'yes')),
                       ('delete after upload', ci('str', True, 'no')),
                       ('remove empty folders after upload', ci('bool', True, 'no')),
                       ])),
           ('tgt', OD([('namespace', ci('str', True, 'namespace.tenant.myhcp.domain.com')),
                       ('path', ci('str', True, 'hcpup')),
                       ('user', ci('str', True, 'testuser')),
                       ('password', ci('str', True, 'testpassword')),
                       ('ssl', ci('bool', True, 'yes')),
                       ('obfuscate', ci('str', True, 'no')),
                       ('local DNS resolver', ci('bool', True, 'no')),
                       ('upload threads', ci('int', True, '2')),
                       ])),
           ('meta', OD([('annotation', ci('str', True, 'hcpupd')),
                        ('tag_timestamp', ci('bool', True, 'yes')),
                        ('tag_note', ci('str', True, 'uploaded by hcpupd')),
                        ('retention', ci('bool', True, '0')),
                        ])),
           ('log', OD([('logfile', ci('str', True, '/var/log/hcpupd/hcpupd.log')),
                       ('debug', ci('bool', True, 'no')),
                       ('yammy', ci('bool', False, 'no')),
                       ])),
           ])
