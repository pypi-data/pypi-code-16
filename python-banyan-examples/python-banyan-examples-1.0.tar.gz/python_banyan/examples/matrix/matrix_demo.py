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

    """

    def __init__(self, back_plane_ip_address=None, subscriber_port='43125',
                 publisher_port='43124', process_name=None):
        super().__init__(back_plane_ip_address, subscriber_port, publisher_port, process_name=process_name)

        self.publisher_topic = '8x8_matrix'

        # LED states
        self.OFF = 0
        self.GREEN = 1
        self.RED = 2
        self.YELLOW = 3

        time.sleep(.3)

        # reset the matrix
        payload = {'command': 'reset_matrix'}
        self.publish_payload(payload, self.publisher_topic)

    def set_pixel(self, x, y, value):
        payload = {'command': 'set_pixel', 'x': x, 'y': y, 'value': value}
        self.publish_payload(payload, self.publisher_topic)
        payload = {'command': 'output_display_buffer'}
        self.publish_payload(payload, self.publisher_topic)

    def clear_display_buffer_contents(self):
        payload = {'command': 'clear_display_buffer_contents'}
        self.publish_payload(payload, self.publisher_topic)




demo = MatrixDemo(process_name='DEMO')
demo.clear_display_buffer_contents()
for c in [demo.RED, demo.GREEN, demo.YELLOW]:
    # Iterate through all positions x and y.
    for x in range(8):
        for y in range(8):
            # Clear the display buffer.
            # demo.clear_display_buffer_contents()
            # Set pixel at position i, j to appropriate color.
            demo.set_pixel(x, y, c)
            # Write the display buffer to the hardware.  This must be called to
            # update the actual display LEDs.
            # display.write_display()
            # Delay for a quarter second.
            time.sleep(0.25)
            #demo.set_pixel(x, y, demo.OFF)
            demo.clear_display_buffer_contents()

# demo.set_pixel(0, 0, demo.GREEN)
# demo.set_pixel(0, 1, demo.GREEN)
# demo.set_pixel(5, 5, demo.RED)
# demo.set_pixel(7, 7, demo.YELLOW)

