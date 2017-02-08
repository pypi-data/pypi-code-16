# !/usr/bin/env python3

"""
Copyright (c) 2017 Alan Yorinks All right reserved.

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

import argparse
import signal
import sys
import time

from python_banyan.banyan_base import BanyanBase

# i2c_htk1633.py

class I2CHtk1633(BanyanBase):
    """
    This class provides the i2c interface to the htk1633 matrix led controller

    """

    # blink rate defines
    HT16K33_BLINK_CMD = 0x80
    HT16K33_BLINK_DISPLAY_ON = 1
    HT16K33_BLINK_OFF = 0
    HT16K33_BLINK_2HZ = 1
    HT16K33_BLINK_1HZ = 2
    HT16K33_BLINK_HALFHZ = 3

    # brightness command
    HT16K33_BRIGHTNESS_CMD = 0xE0
    MAX_BRIGHTNESS = 15

    # oscillator control values
    OSCILLATOR_ON = 0x21
    OSCILLATOR_OFF = 0x20

    # LED states
    OFF = 0
    GREEN = 1
    RED = 2
    YELLOW = 3

    def __init__(self, back_plane_ip_address=None, subscriber_port='43125',
                 publisher_port='43124', device_address=112, process_name=None,
                 blink_rate=HT16K33_BLINK_OFF, brightness=MAX_BRIGHTNESS):
        """

        :param back_plane_ip_address:
        :param subscriber_port:
        :param publisher_port:
        :param device_address:
        :param process_name:
        :param blink_rate:
        :param brightness:
        """
        super().__init__(back_plane_ip_address, subscriber_port, publisher_port, process_name=process_name)

        # pub/sub info
        self.set_subscriber_topic('8x8_matrix')
        self.publisher_topic = 'i2c_8x8_matrix' + str(device_address)

        self.device_address = device_address

        # i2c commands for the htk1633
        # the values will be filled in by the methods for each command
        self.i2c_device = {
            "htk1633": {
                "commands": {
                    "init": [
                        {
                            u"command": u"init",
                            u"device_address": self.device_address
                        }
                    ],
                    "set_oscillator_state": [
                        {
                            u"command": u"write_byte",
                            u"device_address": self.device_address,
                            u"value": self.OSCILLATOR_OFF
                        }
                    ],

                    "set_blink_rate": [
                        {
                            u"command": u"write_byte",
                            u"device_address": self.device_address,
                            u"value": self.HT16K33_BLINK_CMD
                        }
                    ],
                    "set_brightness": [
                        {
                            u"command": u"write_byte",
                            u"device_address": self.device_address,
                            u"value": self.HT16K33_BRIGHTNESS_CMD

                        }
                    ],
                    "write_pixel": [
                        {
                            u"command": u"write_byte_data",
                            u"device_address": self.device_address,
                            u"value": 0
                        }
                    ]
                }
            }
        }

        self.blink_rate = blink_rate
        self.brightness = brightness

        # there are 2 entries per pixel position on the display.
        # one to indicate the green led state and the other for the red.
        # if bits for both leds are on, the pixel will be yellow
        self.display_buffer = bytearray([0] * 16)

        # initialize the device for i2c operations

        time.sleep(.3)

        self.initialize_i2c_device()

        # turn on oscillator
        self.set_oscillator_state(self.OSCILLATOR_ON)
        time.sleep(.3)

        # set blink rate
        self.set_blink_rate(self.blink_rate)
        time.sleep(.3)

        # set brightness
        self.set_brightness(self.brightness)
        time.sleep(.3)

        # set LEDs to Off
        # the buffer is clear at this point, so just output the buffer
        self.output_display_buffer()
        time.sleep(.3)

        time.sleep(.3)

        # kick off the receive loop
        self.receive_loop()

    def initialize_i2c_device(self):
        """
        This method establishes the i2c address of the device on the MCU.
        :return:
        """
        msg = self.i2c_device['htk1633']['commands']['init']
        self.publish_payload(msg, self.publisher_topic)

    def reset_matrix(self):
        self.clear_display_buffer_contents()
        self.set_oscillator_state(self.OSCILLATOR_ON)
        self.set_blink_rate(self.HT16K33_BLINK_OFF)
        self.set_brightness(self.MAX_BRIGHTNESS)
        self.output_display_buffer()

    def set_oscillator_state(self, oscillator_state):
        """
        This method set the oscillator On or Off
        :param oscillator_state:
        :return:
        """

        if oscillator_state not in [self.OSCILLATOR_ON, self.OSCILLATOR_OFF]:
            raise ValueError('Invalid oscillator state requested')

        msg = self.i2c_device['htk1633']['commands']['set_oscillator_state']
        msg[0]['value'] = oscillator_state
        self.publish_payload(msg, self.publisher_topic)

    def set_blink_rate(self, blink_rate):

        if blink_rate not in [self.HT16K33_BLINK_OFF, self.HT16K33_BLINK_1HZ, self.HT16K33_BLINK_2HZ,
                              self.HT16K33_BLINK_HALFHZ]:
            raise ValueError('Invalid blink rate requested')

        msg = self.i2c_device['htk1633']['commands']['set_blink_rate']
        msg[0]['value'] = self.HT16K33_BLINK_CMD | self.HT16K33_BLINK_DISPLAY_ON | blink_rate
        self.publish_payload(msg, self.publisher_topic)

    def set_brightness(self, brightness):
        """
        Set display brightness
        :param brightness:
        :return:
        """
        if brightness < 0 or brightness > self.MAX_BRIGHTNESS:
            raise ValueError('Brightness range is 0 - 15')

        msg = self.i2c_device['htk1633']['commands']['set_brightness']
        msg[0]['value'] = self.HT16K33_BRIGHTNESS_CMD | brightness
        self.publish_payload(msg, self.publisher_topic)

    def set_led(self, led, value):
        """Sets specified LED (value of 0 to 127) to the specified value, 0/False
        for off and 1 (or any True/non-zero value) for on.
        """
        if led < 0 or led > 127:
            raise ValueError('LED must be value of 0 to 127.')
        # Calculate position in byte buffer and bit offset of desired LED.
        pos = led // 8
        offset = led % 8
        if not value:
            # Turn off the specified LED (set bit to zero).
            self.display_buffer[pos] &= ~(1 << offset)
        else:
            # Turn on the specified LED (set bit to one).
            self.display_buffer[pos] |= (1 << offset)

    def output_display_buffer(self):
        """
        Write display buffer contents to LEDs
        :return:
        """
        for i, value in enumerate(self.display_buffer):
            msg = self.i2c_device['htk1633']['commands']['write_pixel']
            msg[0]['value'] = value
            msg[0]['register'] = i
            self.publish_payload(msg, self.publisher_topic)

    def clear_display_buffer_contents(self):
        """
        Clear the display buffer
        :return:
        """
        self.display_buffer = bytearray([0] * 16)

    def set_pixel(self, x, y, value):
        """Set pixel at position x, y to the given value.  X and Y should be values
        of 0 to 8.  Value should be OFF, GREEN, RED, or YELLOW.
        """
        if x < 0 or x > 7 or y < 0 or y > 7:
            # Ignore out of bounds pixels.
            return
        # Set green LED based on 1st bit in value.
        self.set_led(y * 16 + x, 1 if value & self.GREEN > 0 else 0)
        # Set red LED based on 2nd bit in value.
        self.set_led(y * 16 + x + 8, 1 if value & self.RED > 0 else 0)

    def incoming_message_processing(self, topic, payload):
        """
        :param topic: Message Topic string
        :param payload: Message Data
        :return:
        """
        try:
            command = payload['command']
            if command == 'init':
                self.initialize_i2c_device()
            elif command == 'set_oscillator':
                osc_state = payload['osc_state']
                self.set_oscillator_state(osc_state)
            elif command == 'set_blink_rate':
                blink_rate = payload['blink_rate']
                self.set_blink_rate(blink_rate)
            elif command == 'set_brightness':
                brightness = payload['brightness']
                self.set_blink_rate(brightness)
            elif command == 'set_led':
                led = payload['led']
                value = payload['value']
                self.set_led(led, value)
            elif command == 'set_pixel':
                x = payload['x']
                y = payload['y']
                value = payload['value']
                self.set_pixel(x, y, value)
            elif command == 'output_display_buffer':
                self.output_display_buffer()
            elif command == 'clear_display_buffer':
                self.clear_display_buffer_contents()
            elif command == 'reset_matrix':
                self.reset_matrix()
            else:
                # print('led topic: ' + str(topic) + '  payload: ' + str(payload))

                raise ValueError

        except ValueError:
            # print('led topic2: ' + topic + '  payload: ' + payload)
            pass


def i2c_htk1633():
    # noinspection PyShadowingNames

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    parser.add_argument("-n", dest="process_name", default="HTK1633 Matrix Front End",
                        help="Set process name in banner")

    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options['process_name'] = args.process_name

    my_htk = I2CHtk1633(**kw_options)

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
    i2c_htk1633()
