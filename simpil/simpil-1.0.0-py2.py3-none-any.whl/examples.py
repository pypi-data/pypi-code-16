# -*- coding: utf-8 -*-
# Author: Hywel Thomas

from simpil_image import SimpilImage
from simpil_constants import (RED,
                              GREEN,
                              BLUE,
                              WHITE)



# font = ImageFont.truetype(u"C:\Windows\Fonts\consola.ttf", 36)

PYTHON_IMAGE_URL = u"https://s-media-cache-ak0.pinimg.com/736x/13/e5/c3/13e5c3587e3010552923f30310fe1563.jpg"
PYTHON_IMAGE_FILENAME = u'images/python.jpg'
RED_RECT = u'images/red_rect.jpg'
ORANGE_AND_UKE = u'images/orange_and_uke.jpg'
ORANGE_AND_UKE_MANIPULATED = u'images/orange_and_uke_manipulated.jpg'

# Pulls image from a requests url
python = SimpilImage(source=PYTHON_IMAGE_URL,
                     destination=PYTHON_IMAGE_FILENAME)

# Reads and image from a file and saves a copy to a new file
orange_and_uke = SimpilImage(source=ORANGE_AND_UKE,
                             destination=ORANGE_AND_UKE_MANIPULATED)

# Creates a new image (No source supplied)
red_rect = SimpilImage(width=400,
                       height=200,
                       background_colour=RED,
                       destination=RED_RECT)

# Above image is created and saved.
# This wipes any previous RED_RECT file
#
red_rect = SimpilImage(source=RED_RECT)


# Adds text to the images. Autosave will be enabled. The files are saved
# Each time one of the functions is called.

for image in (python,
              orange_and_uke,
              red_rect):

    image.shadowed_text(text=u'Shadow',
                        x=25,
                        y=80,
                        colour=GREEN,
                        shadow_size=3)

    image.outlined_text(text=u"Outline",
                        x=50,
                        y=150,
                        colour=RED,
                        outline_colour=WHITE,
                        outline_size=3)

    image.text(text=u"Text",
               x=10,
               y=10,
               colour=BLUE)
