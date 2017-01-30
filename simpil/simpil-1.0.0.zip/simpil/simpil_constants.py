# -*- coding: utf-8 -*-
# Author: Hywel Thomas

from logging import warning
import StringIO
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import requests

RGB = u"RGB"
JPEG = u"JPEG"
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255,)
WHITE = (255, 255, 255)
DEFAULT_FONT = ImageFont.load_default()
