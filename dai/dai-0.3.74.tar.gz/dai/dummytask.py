import time
import sys
for i in range(100):
    print('%d'%i)
    sys.stdout.flush()
    time.sleep(0.1)
sys.exit(0)
