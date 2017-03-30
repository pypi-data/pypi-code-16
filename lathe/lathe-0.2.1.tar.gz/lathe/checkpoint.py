import numpy as np
import errno


def save(path, checkpoint):
    if checkpoint:
        np.save(open(path, 'w'), checkpoint)


def load(path):
    checkpoint = None
    try:
        checkpoint = np.load(open(path, 'rb'))[()]
    except IOError as e:
        # if file doesn't exist then we assume the user wants to create it
        if e.errno != errno.EEXIST:
            raise
    return checkpoint
