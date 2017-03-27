from __future__ import print_function
import sys
import time

count = int(sys.argv[1])
sleeptime = float(sys.argv[2])

for i in range(count):
    print("{}".format(i))
    sys.stdout.flush()
    time.sleep(sleeptime)

