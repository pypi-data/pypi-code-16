# -*- coding: utf-8 -*-
# Author: Hywel Thomas

from logging import warning
import StringIO
from PIL import Image
from PIL import ImageDraw
import requests
from simpil_constants import (DEFAULT_FONT,
                              JPEG,
                              WHITE,
                              BLACK,
                              RGB)

class SimpilImage(object):

    def __init__(self,
                 source=None,
                 destination=None,
                 width=None,
                 height=None,
                 background_colour=None,
                 autosave=True,
                 font=None):
        """
        There are four ways to initialise the image.

        1. From a URL - fetches the image at given URL
        2. From image data - data representing the image, such as data already
                             read from a file. The data should be supplied as
                             a StringIO object or a string
        3. From a filename - reads from the file if it exists
        4. From dimensions - creates an image with width and height,
                            of background colour

        :param source: 1) File to read
                       2) URL of an image to fetch
                       3) Image data as StringIO
                       4) Image data as string

        :param destination: File to save/autosave to
        :param url: URL of an image to fetch
        :param image_data: Image data of pre-fetched image
        :param width: Width in pixels of an image to create
        :param height: Height in pixels of an image we want to create
        :param background_colour: Fill colour of a created image
        :param autosave: Flag to indicate whether to autosave changes.
                         Default is True.
                         Note that for files, if the destination is not
                         supplied, changes will overwrite the original file
        :param font: A default font to use when adding text. If not supplied,
                     The DEFAULT_FONT from simpil_constants is used.
        """
        self.source = source
        self.destination = destination

        self.__autosave = autosave

        skip_autosave_on_init = False

        if isinstance(source, StringIO.StringIO):
            self.image = Image.open(source)

        elif source and u'http' in source:
            data = requests.get(source).content
            self.image = Image.open(StringIO.StringIO(data))

        elif isinstance(source, basestring):
            try:
                self.image = Image.open(source)
                if not destination:
                    self.destination = source

                if destination == source:
                    # Don't save over the top if there's no change
                    skip_autosave_on_init = False

            except IOError:
                self.image = Image.open(StringIO.StringIO(source))

        else:
            # Couldn't open anything, make a new image
            self.__new_image(width=width,
                             height=height,
                             background_colour=background_colour)

        self.draw = ImageDraw.Draw(self.image)
        self.default_font = (font
                             if font
                             else DEFAULT_FONT)

        if not skip_autosave_on_init:
            self.autosave()

    @property
    def width(self):
        raise NotImplementedError(u'TODO')

    @property
    def height(self):
        raise NotImplementedError(u'TODO')

    def __new_image(self,
                    width,
                    height,
                    background_colour
                    ):
        """
        Creates an image with the given dimensions and filled with the
        background colour
        """
        if not(width and height):
            raise ValueError(u'You must provide a height and a width '
                             u'when creating a new image')

        background_colour = (background_colour
                             if background_colour
                             else BLACK)

        self.image = Image.new(mode=RGB,
                               size=(width, height),
                               color=background_colour)

    def text(self,
              text,
              x,
              y,
              font = None,
              colour = WHITE,):

        """
        Draws text on the image

        :param text: Text string to draw
        :param x: horizontal position
        :param y: vertical position
        :param font: The find object to use
        :param colour: foreground text colour
        :return:
        """

        font = font if font else self.default_font

        self.draw.text(xy=(x, y),
                       text=text,
                       fill=colour,
                       font=font)
        self.autosave()

    def shadowed_text(self,
                      text,
                      x,
                      y,
                      font = None,
                      colour = WHITE,
                      shadow_colour = BLACK,
                      shadow_size=1):
        """
        Draws text with a bottom-right shadow. Useful for making text stand out
        again a background that is similar to the text colour

        :param text: Text string to draw
        :param x: horizontal position
        :param y: vertical position
        :param font: The find object to use
        :param colour: foreground text colour
        :param shadow_colour: Outline colour
        :param shadow_size: Size of the outline in pixels
        :return:
        """

        font = font if font else self.default_font

        position = (x, y)

        shadow_positions = [(xx, yy)
                            for xx in range(x, x + shadow_size + 1)
                            for yy in range(y, y + shadow_size + 1)
                            if not(xx == x and yy == y)]

        for shadow_position in shadow_positions:
            self.draw.text(xy=shadow_position,
                           text=text,
                           fill=shadow_colour,
                           font=font)
        self.draw.text(xy=position,
                       text=text,
                       fill=colour,
                       font=font)
        self.autosave()

    def outlined_text(self,
                      text,
                      x,
                      y,
                      font = None,
                      colour = WHITE,
                      outline_colour = BLACK,
                      outline_size = 1):
        """
        Draws text with an outline. Useful for making text stand out against
        a background that is similar to the text colour

        :param text: Text string to draw
        :param x: horizontal position
        :param y: vertical position
        :param font: The find object to use
        :param colour: foreground text colour
        :param outline_colour: Outline colour
        :param outline_size: Size of the outline in pixels
        :return:
        """
        font = font if font else self.default_font
        position = (x, y)
        outline_positions = [(xx, yy)
                             for xx in range(x - outline_size,
                                             x + outline_size + 1)
                             for yy in range(y - outline_size,
                                             y + outline_size + 1)
                             if not(xx == x and yy == y)]

        for outline_position in outline_positions:
            self.draw.text(xy=outline_position,
                           text=text,
                           fill=outline_colour,
                           font=font)
        self.draw.text(xy=position,
                       text=text,
                       fill=colour,
                       font=font)
        self.autosave()

    def save(self,
             filename=None):
        """
        Save the image to a file. Will use the filename provided.
        If the filename is not provided, will use a previously
        configured destination.  Supply of filename will not
        alter where autosave is done.

        :param filename:
        :return:
        """
        filename = filename if filename else self.destination
        if filename:
            self.image.save(filename)
        else:
            warning(u"Can't save: (No filename provided)")

    def autosave(self,
                 filename=None):
        """
        Called by self after operations that alter the image.
        Can also be called outside the object to enable autosave
        and to supply an auto save filename

        :param filename: Filename for autosave
        :return: None
        """
        if filename:
            self.destination = filename
            self.__autosave = True

        if self.__autosave and self.destination:
            self.save()

    def image_data(self,
                   format=JPEG):
        """
        Returns the raw image data in the desired format.
        This can be used when there's no need to save the
        file to disk, such as for images dynamically created
        from webserver requests.

        :param format: Format of the image file
        :return: raw image data
        """
        output = StringIO.StringIO()
        self.image.save(output,
                        format=format)
        image_data = output.getvalue()
        output.close()
        return image_data
