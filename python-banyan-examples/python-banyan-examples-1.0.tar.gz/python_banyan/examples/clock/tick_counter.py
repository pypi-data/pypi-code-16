"""
Copyright (c) 2016-2017 Alan Yorinks All right reserved.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public
License as published by the Free Software Foundation; either
version 3 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

# tick_counter.py

import argparse
import signal
import sys
import time
import datetime

from python_banyan.banyan_base import BanyanBase


class TickCounter(BanyanBase):
    """
    This class receives subscribes for tick messages

    """

    def __init__(self, back_plane_ip_address=None, subscriber_port='43125', publisher_port='43124',
                 process_name=None, loop_time=.1):
        """

        :param back_plane_ip_address:
        :param subscriber_port:
        :param publisher_port:
        :param process_name:
        """
        # initialize the base class
        super().__init__(back_plane_ip_address, subscriber_port, publisher_port, process_name=process_name,
                         loop_time=loop_time)

        # allow time for connection
        time.sleep(.03)

        # event message from RPi
        self.set_subscriber_topic('tick')

        # message from GUI requesting for all of the time units
        self.set_subscriber_topic('update_me')

        current_time = datetime.datetime.now().time()
        self.hours = self.prev_hour = current_time.hour
        self.minutes = current_time.minute
        self.seconds = current_time.second

        self.publish_payload({'hours': str(self.hours).zfill(2)}, 'update_hours')
        self.publish_payload({'minutes': str(self.minutes).zfill(2)}, 'update_minutes')
        self.publish_payload({'seconds': str(self.seconds).zfill(2)}, 'update_seconds')

        # receive loop is defined in the base class
        self.receive_loop()

    def incoming_message_processing(self, topic, payload):
        """
        This method accumulates ticks and publishes update message for the GUI

        :param topic: Message Topic string
        :param payload: Message Data
        :return:
        """

        if topic == 'tick':
            self.seconds += 1

            if self.seconds == 60:

                current_time = datetime.datetime.now().time()
                self.seconds = current_time.second
                self.publish_payload({'seconds': str(self.seconds).zfill(2)}, 'update_seconds')

                self.hours = current_time.hour

                if self.hours != self.prev_hour:
                    self.prev_hour = self.hours
                    self.publish_payload({'hours': str(self.hours).zfill(2)}, 'update_hours')

                if self.minutes != current_time.minute:
                    self.minutes = current_time.minute
                    self.publish_payload({'minutes': str(self.minutes).zfill(2)}, 'update_minutes')

                self.seconds = current_time.second
            else:
                self.publish_payload({'seconds': str(self.seconds).zfill(2)}, 'update_seconds')

        elif topic == 'update_me':
            # current_time = datetime.datetime.now().time()
            self.publish_payload({'hours': str(self.hours).zfill(2)}, 'update_hours')
            self.publish_payload({'minutes': str(self.minutes).zfill(2)}, 'update_minutes')
            self.publish_payload({'seconds': str(self.seconds).zfill(2)}, 'update_seconds')


def tick_counter():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    parser.add_argument("-n", dest="process_name", default="Tick Counter", help="Set process name in banner")
    parser.add_argument("-t", dest="loop_time", default=".1", help="Event Loop Timer in seconds")

    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options['process_name'] = args.process_name
    kw_options['loop_time'] = float(args.loop_time)

    my_tick_counter = TickCounter(**kw_options)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        my_tick_counter.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    tick_counter()
