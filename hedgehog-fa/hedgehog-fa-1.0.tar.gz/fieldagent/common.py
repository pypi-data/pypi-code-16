import logging
import sys

def setupLogging(logging_level):
    root = logging.getLogger()
    root.setLevel(logging_level)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)
    return root;