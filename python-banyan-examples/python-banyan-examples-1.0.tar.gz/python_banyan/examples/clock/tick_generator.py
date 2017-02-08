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

# tick_generator.py

from __future__ import absolute_import
import argparse
import signal
import sys
import time

# noinspection PyUnresolvedReferences
from python_banyan.banyan_base import BanyanBase


class TickGenerator(BanyanBase):
    """
    This class will publish a "tick" message on a periodic basis. The period default
    is 1 seconds, but may be set by the tick_duration_time parameter

    """

    def __init__(self, back_plane_ip_address=None, subscriber_port='43125',
                 publisher_port='43124',
                 process_name='None', loop_time=.1, tick_duration_time=1.0, ):
        """

        :param back_plane_ip_address:
        :param subscriber_port:
        :param publisher_port:
        :param process_name:
        :param loop_time:
        :param tick_duration_time:
        """
        # initialize the base class
        super(TickGenerator, self).__init__(back_plane_ip_address, subscriber_port, publisher_port,
                                            process_name=process_name,
                                            loop_time=loop_time)

        # allow time for ZeroMQ connections to form
        time.sleep(.03)

        self.tick_duration_time = tick_duration_time

        self.tick_topic = 'tick'
        self.tick_payload = {'tick': True}

        # This is a forever loop that publishes a tick message, once per second
        while True:
            try:
                self.publish_payload(self.tick_payload, self.tick_topic)
                time.sleep(self.tick_duration_time)
            except KeyboardInterrupt:
                sys.exit(0)


def tick_generator():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    parser.add_argument("-d", dest="tick_duration_time", default="1.0",
                        help="Set tick duration time")
    parser.add_argument("-n", dest="process_name", default="Local Tick_Generator", help="Set process name in banner")
    parser.add_argument("-t", dest="loop_time", default=".1", help="Event Loop Timer in seconds")

    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options['process_name'] = args.process_name
    kw_options['loop_time'] = float(args.loop_time)
    kw_options['tick_duration_time'] = float(args.tick_duration_time)

    my_tick_gen = TickGenerator(**kw_options)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        my_tick_gen.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    tick_generator()
