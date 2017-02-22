# This file is part of python-munnel
# Copyright (C) 2017  Nexedi
# Author: Vincent Pelletier <vincent@nexedi.com>
#
# python-munnel is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-functionfs is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with python-munnel.  If not, see <http://www.gnu.org/licenses/>.
import argparse
import libmilter
import signal
import sys

# XXX: this code is overcomplex because instance life scope is neither clearly
# documented nor clearly readable from the code. So give this code more chances
# to fail, to avoid letting mails go through unmodified.

class Munnel(libmilter.ThreadMixin, libmilter.MilterProtocol):
    replacement_recipient_list = None # Override in subclasses
    existing_recipient_list = None # Will be filled/reset during instance life

    def __init__(self, *args, **kw):
        libmilter.ThreadMixin.__init__(self)
        libmilter.MilterProtocol.__init__(self, *args, **kw)

    @libmilter.noReply
    def mailFrom(self, frAddr, cmdDict):
        new_recipient_list = []
        set_recipient_list = self.__dict__.setdefault(
            'existing_recipient_list',
            new_recipient_list,
        )
        assert new_recipient_list is set_recipient_list

    @libmilter.noReply
    def rcpt(self, recip, cmdDict):
        self.existing_recipient_list.append(recip)

    def eob(self, cmdDict):
        delRcpt = self.delRcpt
        for recipient in self.__dict__.pop('existing_recipient_list'):
            delRcpt(recipient)
        addRcpt = self.addRcpt
        for recipient in self.replacement_recipient_list:
            addRcpt(recipient)
        return libmilter.CONTINUE

    def close(self):
        self.__dict__.pop('existing_recipient_list', None)

def main():
    parser = argparse.ArgumentParser(
        description='Milter replacing RCTP TO addresses with configured ones',
    )
    parser.add_argument(
        '--listen',
        required=True,
        help='Socket to listen to (format: "inet:$IP:$PORT" for network '
        'socket, a bare path for unix socket)',
    )
    parser.add_argument(
        'recipient',
        nargs='+',
        help='Addresses to actually send mails to',
    )
    args = parser.parse_args()
    milter = libmilter.ThreadFactory(
        sockstr=args.listen,
        protocol=type(
            'ThisMunnel',
            (Munnel, ),
            {
                'replacement_recipient_list': args.recipient,
            },
        ),
        opts=libmilter.SMFIF_DELRCPT | libmilter.SMFIF_ADDRCPT,
        sockChmod=0660, # Why is libmilter trying to chmod at all !?
    )
    try:
        milter.run()
    except (SystemExit, KeyboardInterrupt):
        pass
    finally:
        milter.close()

if __name__ == '__main__':
    main()
