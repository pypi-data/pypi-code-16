"""A corpus of object images."""

from base64 import b64encode
import os

objects = [o for o in os.listdir("objects") if o.endswith(".jpg")]


def base64(idx):
    """Load an image."""
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, objects[idx])
    with open(path, "rb") as f:
        return b64encode(f.read())
