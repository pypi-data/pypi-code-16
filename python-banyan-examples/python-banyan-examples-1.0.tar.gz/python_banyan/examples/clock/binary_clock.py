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
import sys
import signal
import argparse

from python_banyan.banyan_base import BanyanBase


class BinaryClock(BanyanBase):
    """
    This class is client for "tick_counter" messages and publishes the time to control a binary clock
    using an 8x8 LED matrix display.
    The top line indicates hours.
    The middle line indicates minutes.
    The bottom line indicates seconds.
    """

    def __init__(self, back_plane_ip_address=None, subscriber_port='43125',
                 publisher_port='43124', process_name=None):
        """

        :param back_plane_ip_address:
        :param subscriber_port:
        :param publisher_port:
        :param process_name:
        """
        super().__init__(back_plane_ip_address, subscriber_port, publisher_port, process_name=process_name)

        # published message topics
        self.publisher_topic = '8x8_matrix'

        # subscribed topics

        # LED colors
        self.OFF = 0
        self.GREEN = 1
        self.RED = 2
        self.YELLOW = 3

        # row positions for bcd digits
        self.hour_tens = 0
        self.hour_ones = 1

        self.minute_tens = 3
        self.minute_ones = 4

        self.second_tens = 6
        self.second_ones = 7

        self.processing_enabled = False

        time.sleep(.3)

        subscriber_topics = ['update_seconds', 'update_minutes', 'update_hours']

        for topic in subscriber_topics:
            self.set_subscriber_topic(topic)

        # clear the matrix display and return all display parameters to default values
        self.init_display()

        # ask for the current time
        # this is a one shot at start up.
        self.publish_payload({'first': 'a'}, 'update_me')

        self.processing_enabled = True

        self.receive_loop()

    def init_display(self):
        """
        Publish a reset matrix message request
        :return:
        """

        # clear the buffer and output to display
        payload = {'command': 'clear_display_buffer'}
        self.publish_payload(payload, self.publisher_topic)
        payload = {'command': 'output_display_buffer'}
        self.publish_payload(payload, self.publisher_topic)

        # set all digits to RED indicating a zero

        self.convert_to_binary_and_display('0', self.hour_tens)
        self.convert_to_binary_and_display('0', self.hour_ones)
        self.convert_to_binary_and_display('0', self.minute_tens)
        self.convert_to_binary_and_display('0', self.minute_ones)
        self.convert_to_binary_and_display('0', self.second_tens)
        self.convert_to_binary_and_display('0', self.second_ones)

    def clear_display_buffer_contents(self):
        """
        Clears the display (all pixels off)
        :return:
        """
        payload = {'command': 'clear_display_buffer_contents'}
        self.publish_payload(payload, self.publisher_topic)

    def incoming_message_processing(self, topic, payload):
        """
        This method is overloaded from the base class. It handles all incoming messages
        :param topic:
        :param payload:
        :return:
        """
        if self.processing_enabled:
            if topic == 'update_seconds':
                seconds = payload['seconds']
                self.update_seconds(seconds)
            elif topic == 'update_minutes':
                minutes = payload['minutes']
                self.update_minutes(minutes)
            elif topic == 'update_hours':
                hours = payload['hours']
                self.update_hours(hours)
            else:
                raise ValueError("unknown message topic: " + topic)
        else:
            pass

    def update_hours(self, hours):
        """
        Convert hours to a binary representation and send to matrix
        :param hours:
        :return:
        """
        self.convert_to_binary_and_display(hours[0], self.hour_tens)
        self.convert_to_binary_and_display(hours[1], self.hour_ones)

    def update_minutes(self, minutes):
        """
        Convert minutes to a binary representation and send to matrix

        :param minutes:
        :return:
        """
        self.convert_to_binary_and_display(minutes[0], self.minute_tens)
        self.convert_to_binary_and_display(minutes[1], self.minute_ones)

    def update_seconds(self, seconds):
        """
        Convert seconds to a binary representation and send to matrix

        :param seconds:
        :return:
        """
        self.convert_to_binary_and_display(seconds[0], self.second_tens)
        self.convert_to_binary_and_display(seconds[1], self.second_ones)

    def convert_to_binary_and_display(self, digit, column):
        """
        This method converts an ascii digit to bcd and sets the leds for the column.
        A Red led indicates a zero and a Green led indicates a one
        :param digit:
        :param column:
        :return:
        """

        bcd = ''.join(format(int(c), '04b') for c in str(int(digit, 16)))
        row = 5
        for bit in range(len(bcd)):
            if bcd[bit] == '0':
                payload = {'command': 'set_pixel', 'x': row, 'y': column, 'value': self.RED}
                self.publish_payload(payload, self.publisher_topic)
            else:
                payload = {'command': 'set_pixel', 'x': row, 'y': column, 'value': self.GREEN}
                self.publish_payload(payload, self.publisher_topic)
            row -= 1
        payload = {'command': 'output_display_buffer'}
        self.publish_payload(payload, self.publisher_topic)


def binary_clock():
    # noinspection PyShadowingNames

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    parser.add_argument("-n", dest="process_name", default="Binary Clock",
                        help="Set process name in banner")

    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options['process_name'] = args.process_name

    my_htk = BinaryClock(**kw_options)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        my_htk.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    binary_clock()
