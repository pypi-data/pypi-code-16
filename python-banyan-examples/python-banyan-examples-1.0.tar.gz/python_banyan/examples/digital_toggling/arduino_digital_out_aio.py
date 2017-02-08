#!/usr/bin/python3
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

You should have received python_banyan copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

# arduino_digital_out_aio.py


from pymata_aio.pymata3 import PyMata3
from pymata_aio.constants import Constants
import time
import sys
import signal
import argparse
import zmq
import umsgpack

from python_banyan.banyan_base import BanyanBase


class ArduinoDigitalOutAIO(BanyanBase):
    """
    This class is the interface class for Arduino output using the
    pymata-aio library.

    It is used to set a BCM pin as a digital output and to set its state.
    """

    def __init__(self, pins, back_plane_ip_address=None, subscriber_port='43125', publisher_port='43124',
                 process_name=None):

        super().__init__(back_plane_ip_address, subscriber_port, publisher_port,
                         process_name=process_name)

        time.sleep(.3)

        # initialize pin direction

        self.pins = pins

        self.board = PyMata3()

        for pin in pins:
            self.board.set_pin_mode(pin, Constants.OUTPUT)

        self.set_subscriber_topic('digital_output')

        self.receive_loop()

    def receive_loop(self):
        """
        This is the receive loop for zmq messages.

        It is assumed that this method will be overwritten to meet the needs of the application and to handle
        received messages.
        :return:
        """
        while True:
            try:
                data = self.subscriber.recv_multipart(zmq.NOBLOCK)
                self.incoming_message_processing(data[0].decode(), umsgpack.unpackb(data[1]))
            except zmq.error.Again:
                try:
                    self.board.sleep(self.loop_time)
                    pass
                except KeyboardInterrupt:
                    self.clean_up()

    def incoming_message_processing(self, topic, payload):
        """
        Override this method with a custom python_banyan message processor for subscribed messages

        :param topic: Message Topic string
        :param payload: Message Data
        :return:
        """

        # set the state of the pin specified in the message.
        if payload['command'] == 'set_state':
            for pin in self.pins:
                self.board.digital_write(pin, payload['state'])
        else:
            raise TypeError('Unknown command received')


def arduino_digital_out():
    # noinspection PyShadowingNames

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    parser.add_argument("-n", dest="process_name", default="Arduino Digital Output",
                        help="Set process name in banner")

    parser.add_argument('-p', nargs='+', required=True, type=int, dest='pins', help='Required - Enter a list of space '
                                                                                    'delimited pin numbers')

    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options['process_name'] = args.process_name

    ard_dig_out = ArduinoDigitalOutAIO(args.pins, **kw_options)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        ard_dig_out.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    arduino_digital_out()
