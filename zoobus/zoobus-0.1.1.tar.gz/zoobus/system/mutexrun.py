# coding=utf8

import os
import fcntl
import hashlib
from optparse import OptionParser

def run_command(command):
    # 1 acquire lock, lock
    key = hashlib.md5(command).hexdigest()
    fpath = os.path.join('/tmp/', 'lockrun-%s' % key)
    f = open(fpath, 'w')
    fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)

    # if acquire lock failed, can't goto next operation

    #fcntl.lockf(f,fcntl.LOCK_NB)
    # 2 execute command
    os.system(command)
    f.close()



def main():
    parser = OptionParser()
    parser.add_option("-c", "--command", dest="command",
                      help="execute command", metavar="COMMAND")

    (options, args) = parser.parse_args()
    if not options.command:
        parser.error("need command.")
    run_command(command)
