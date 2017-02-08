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

import argparse
import signal
import sys
import time

import pigpio
# noinspection PyUnresolvedReferences
from python_banyan.banyan_base import BanyanBase


class RPiDigitalOut(BanyanBase):
    """
    This class is the interface class for Raspberry Pi digital
    output control using the pigpio library.

    It is used to set  BCM pins as digital outputs and to set their states.
    """

    def __init__(self, pins, back_plane_ip_address=None, subscriber_port='43125',
                 publisher_port='43124', process_name=None):
        """
        Initialize the BanyanBase parent object.
        Subscribe to topics of interest.
        Create an instance of pigpio

        :param back_plane_ip_address:
        :param subscriber_port:
        :param publisher_port:
        :param process_name:
        """
        # initialize the base class and wait for zmq connections to complete
        super().__init__(back_plane_ip_address, subscriber_port, publisher_port,
                         process_name=process_name)

        time.sleep(.3)

        # set the subscriber topic
        self.set_subscriber_topic('digital_output')

        # create a pigpio object
        # make sure to start the pipgio daemon before starting this component
        self.pi = pigpio.pi()

        # save the requested list of pins that need to be controlled
        self.pins = pins

        # set all the pins in the list to output pins
        for pin in pins:
            self.pi.set_mode(pin, pigpio.OUTPUT)

        # subscribe to digital_output messages
        self.set_subscriber_topic('digital_output')

        # start the receive loop
        self.receive_loop()

    # noinspection PyUnusedLocal
    def incoming_message_processing(self, topic, payload):
        """
        :param topic: Message Topic string
        :param payload: Message Data
        :return:
        """

        # set the state for all the pins in the pin list
        if payload['command'] == 'set_state':
            for pin in self.pins:
                self.pi.write(pin, payload['state'])
        else:
            raise TypeError('Unknown command received')


def rpi_digital_out():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")

    parser.add_argument("-n", dest="process_name", default="LED Back End",
                        help="Set process name in banner")

    parser.add_argument('-p', nargs='+', required=True, type=int, dest='pins',
                        help='Required - Enter a list of space delimited pin numbers')
    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options['process_name'] = args.process_name

    my_rpi_digital_out = RPiDigitalOut(args.pins, **kw_options)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        my_rpi_digital_out.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    rpi_digital_out()
