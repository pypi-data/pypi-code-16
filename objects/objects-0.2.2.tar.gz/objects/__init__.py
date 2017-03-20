"""A corpus of object images."""

from base64 import b64encode
import os

object_dir = os.path.dirname(os.path.realpath(__file__))
objects = [o for o in os.listdir(object_dir) if o.endswith(".jpg")]


def base64(idx):
    """Load an image."""
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, objects[idx])
    with open(path, "rb") as f:
        return b64encode(f.read())
