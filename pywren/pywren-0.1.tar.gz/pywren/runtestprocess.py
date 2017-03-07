from __future__ import print_function
import sys
import time
import subprocess
import select
import fcntl
import os
from threading import Thread
import logging
logger = logging.getLogger(__name__)


cmdstr = "python testprocess.py 10 3"
process = subprocess.Popen(cmdstr, shell=True, bufsize=1, 
                           stdout=subprocess.PIPE)



try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

def get_data(stdout, queue):
    with stdout:
        for line in iter(stdout.readline, b''):
            queue.put(line)
            print(line)

q = Queue()

t = Thread(target=get_data, args=(process.stdout, q))

t.daemon = True
t.start()
stdout = b""

while t.isAlive():
    try: 
        line = q.get_nowait()
        stdout += line
        logger.info(line)
    except Empty:
        print("sleeping")
        time.sleep(1)



# fd = process.stdout.fileno()

# fl = fcntl.fcntl(fd, fcntl.F_GETFL)
# fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)


# while True:
#     try:
#         a = process.stdout.read(100)
#         print(a, len(a))
#     except IOError:
#         print("sleeping")
#         time.sleep(1)


#     # retVal+=proc.stdout.read(1)

    # process.communicate(

    # print(stdout)
