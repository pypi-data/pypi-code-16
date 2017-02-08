# !/usr/bin/env python3

"""
Copyright (c) 2016 Alan Yorinks All right reserved.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public
License as published by the Free Software Foundation; either
version 3 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received python_banyan copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

import time
from PIL import Image
from PIL import ImageDraw
from python_banyan.banyan_base import BanyanBase


class MatrixDemo(BanyanBase):
    """
    The first part of the demo is a recreation of the adafruit demo. The second part outputs numerals
    on the display
    """

    def __init__(self, back_plane_ip_address='192.168.2.181', subscriber_port='43125',
                 publisher_port='43124', process_name=None):
        super().__init__(back_plane_ip_address, subscriber_port, publisher_port, process_name=process_name)

        self.publisher_topic = '8x8_matrix'

        # source of table: https://github.com/dhepper/font8x8/blob/master/font8x8_basic.h

        self.matrix = {
            1: [0x0C, 0x0E, 0x0C, 0x0C, 0x0C, 0x0C, 0x3F, 0x00],
            2: [0x1E, 0x33, 0x30, 0x1C, 0x06, 0x33, 0x3F, 0x00],
            3: [0x1E, 0x33, 0x30, 0x1C, 0x30, 0x33, 0x1E, 0x00],
            4: [0x38, 0x3C, 0x36, 0x33, 0x7F, 0x30, 0x78, 0x00],
            5: [0x3F, 0x03, 0x1F, 0x30, 0x30, 0x33, 0x1E, 0x00],
            6: [0x1C, 0x06, 0x03, 0x1F, 0x33, 0x33, 0x1E, 0x00],
            7: [0x3F, 0x33, 0x30, 0x18, 0x0C, 0x0C, 0x0C, 0x00],
            8: [0x1E, 0x33, 0x33, 0x1E, 0x33, 0x33, 0x1E, 0x00],
            9: [0x1E, 0x33, 0x33, 0x3E, 0x30, 0x18, 0x0E, 0x00],
            0: [0x3E, 0x63, 0x73, 0x7B, 0x6F, 0x67, 0x3E, 0x00],
            # colon
            11: [0x00, 0x0C, 0x0C, 0x00, 0x00, 0x0C, 0x0C, 0x00]
        }

        # LED states
        self.OFF = 0
        self.GREEN = 1
        self.RED = 2
        self.YELLOW = 3

        time.sleep(.3)

        # reset the matrix
        payload = {'command': 'reset_matrix'}
        self.publish_payload(payload, self.publisher_topic)

        # self.walk_display()

    def walk_display(self):
        for c in [self.RED, self.GREEN, self.YELLOW]:
            # Iterate through all positions x and y.
            for x in range(8):
                for y in range(8):
                    # Clear the display buffer.
                    self.set_pixel(x, y, c)
                    time.sleep(.25)
                    # Write the display buffer to the hardware.  This must be called to
                    # update the actual display LEDs.
                    # display.write_display()
                    # Delay for a quarter second.
                    # demo.set_pixel(x, y, demo.OFF)
                    #self.clear_display_buffer_contents()
                    payload = {'command': 'set_pixel', 'x': x, 'y': y, 'value': 0}
                    self.publish_payload(payload, self.publisher_topic)

                    # time.sleep(.125)

    def set_pixel(self, x, y, value):
        # payload = {'command': 'clear_display_buffer'}
        payload = {'command': 'set_pixel', 'x': x, 'y': y, 'value': value}
        self.publish_payload(payload, self.publisher_topic)
        payload = {'command': 'output_display_buffer'}
        self.publish_payload(payload, self.publisher_topic)
        # time.sleep(delay)


    def clear_display_buffer_contents(self):
        payload = {'command': 'clear_display_buffer'}
        self.publish_payload(payload, self.publisher_topic)
        payload = {'command': 'output_display_buffer'}
        self.publish_payload(payload, self.publisher_topic)



    def image_x(self):
        # First create an 8x8 RGB image.
        image = Image.new('RGB', (8, 8))

        # Then create a draw instance.
        draw = ImageDraw.Draw(image)

        # Draw a filled yellow rectangle with red outline.
        draw.rectangle((0, 0, 7, 7), outline=(255, 0, 0), fill=(255, 255, 0))

        # Draw an X with two green lines.
        draw.line((1, 1, 6, 6), fill=(0, 255, 0))
        draw.line((1, 6, 6, 1), fill=(0, 255, 0))

        self.set_image(image)
        payload = {'command': 'output_display_buffer'}
        self.publish_payload(payload, self.publisher_topic)

        # Draw the image on the display buffer.
        # display.set_image(image)
        # payload = {'command': 'set_image', 'image':image}
        # self.publish_payload(payload, self.publisher_topic)

        # Draw the buffer to the display hardware.
        # payload = {'command': 'output_display_buffer'}
        # self.publish_payload(payload, self.publisher_topic)

        # Pause for 5 seconds
        # time.sleep(5)

    def set_image(self, image):
        """Set display buffer to Python Image Library image.  Red pixels (r=255,
        g=0, b=0) will map to red LEDs, green pixels (r=0, g=255, b=0) will map to
        green LEDs, and yellow pixels (r=255, g=255, b=0) will map to yellow LEDs.
        All other pixel values will map to an unlit LED value.
        """
        imwidth, imheight = image.size
        if imwidth != 8 or imheight != 8:
            raise ValueError('Image must be an 8x8 pixels in size.')
        # Convert image to RGB and grab all the pixels.
        pix = image.convert('RGB').load()
        # Loop through each pixel and write the display buffer pixel.
        for x in [0, 1, 2, 3, 4, 5, 6, 7]:
            for y in [0, 1, 2, 3, 4, 5, 6, 7]:
                color = pix[(x, y)]
                # Handle the color of the pixel.
                if color == (255, 0, 0):
                    self.set_pixel(x, y, self.RED)
                elif color == (0, 255, 0):
                    self.set_pixel(x, y, self.GREEN)
                elif color == (255, 255, 0):
                    self.set_pixel(x, y, self.YELLOW)
                else:
                    # Unknown color, default to LED off.
                    self.set_pixel(x, y, self.OFF)

    def display_numeral(self, num, color):
        # get the bit map for the digit
        digit = self.matrix[num]

        self.clear_display_buffer_contents()
        row_num = 0
        for row in reversed(digit):
            col_num = 0
            for y in range(8):
                b = row & 1
                row = row >> 1
                if(b):
                    payload = {'command': 'set_pixel', 'x': row_num, 'y': col_num, 'value': color}
                    self.publish_payload(payload, self.publisher_topic)
                else:
                    payload = {'command': 'set_pixel', 'x': row_num, 'y': col_num, 'value': self.OFF}
                    self.publish_payload(payload, self.publisher_topic)
                col_num += 1
            row_num += 1
            payload = {'command': 'output_display_buffer'}
            self.publish_payload(payload, self.publisher_topic)



demo = MatrixDemo(process_name='DEMO')
# demo.walk_display()
time.sleep(1)
demo.image_x()
time.sleep(4)

for x in range(2):
    demo.display_numeral(1, demo.YELLOW)
    time.sleep(1)
    demo.display_numeral(2, demo.YELLOW)
    time.sleep(1)
    demo.display_numeral(11, demo.RED)
    time.sleep(1)
    demo.display_numeral(3, demo.GREEN)
    time.sleep(1)
    demo.display_numeral(8, demo.GREEN)
    time.sleep(1)
    demo.display_numeral(11, demo.RED)
    time.sleep(1)
    demo.display_numeral(4, demo.GREEN)
    time.sleep(1)
    demo.display_numeral(7, demo.GREEN)
    time.sleep(2)
    demo.clear_display_buffer_contents()



