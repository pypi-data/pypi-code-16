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

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

import argparse
import signal
import sys
import time
import pigpio
from python_banyan.banyan_base import BanyanBase


class BuzzerPigpio(BanyanBase):
    """
    This is a Python Banyan component to control the Raspberry RedBot Piezo buzzer.
    It controls an RPi GPIO pin connected to the buzzer.

    Component Subscriber Topic: system_buzzer_command
    Protocol Message: {'command': 'tone', 'frequency': FREQUENCY, 'duration': DURATION}
    Frequency is in hz. and duration is in milliseconds
    """

    def __init__(self, back_plane_ip_address=None, subscriber_port='43125', publisher_port='43124', pin=10,
                 process_name=None):
        """
        :param back_plane_ip_address: ip address of backplane
        :param subscriber_port: backplane subscriber port
        :param publisher_port: backplane publisher port
        :param pin: BCM GPIO pin number for buzzer
        :param process_name: Name used in console banner for this component. It is initialized in invocation
                             function, buzzer_pigpio, at the bottom of this file
        """

        # initialize the base class
        super().__init__(back_plane_ip_address, subscriber_port, publisher_port, process_name=process_name)

        self.set_subscriber_topic('system_buzzer_command')
        self.pin = pin

        # allow time for connection to backplane
        time.sleep(.03)

        # this class does not publish any messages

        # configure the gpio pin
        self.pi = pigpio.pi()

        self.pi.set_mode(pin, pigpio.OUTPUT)

        # initialize pin to 0 state
        self.pi.write(self.pin, 0)

        # receive loop is defined in the base class
        self.receive_loop()

    def incoming_message_processing(self, topic, payload):
        """
        Override this method with python_banyan message processor for the application

        :param topic: Message Topic string
        :param payload: Message Data
        :return:
        """
        try:
            command = payload['command']
            if command == 'tone':
                frequency = payload['frequency']
                frequency = int((1000 / frequency) * 1000)
                duration = payload['duration']

                # set the pwm pulse rate for the tone
                # see http://abyz.co.uk/rpi/pigpio/python.html#wave_add_generic
                tone = [pigpio.pulse(1 << self.pin, 0, frequency),
                        pigpio.pulse(0, 1 << self.pin, frequency)]

                self.pi.wave_clear()

                self.pi.wave_add_generic(tone)
                tone_wave = self.pi.wave_create()  # create and save id
                self.pi.wave_send_repeat(tone_wave)

                # if duration == 0:
                #     return

                sleep_time = duration * .001
                time.sleep(sleep_time)
                self.pi.wave_tx_stop()  # stop waveform

                self.pi.wave_clear()  # clear all waveforms

            else:
                raise ValueError

        except ValueError:
            print('led_pigpio topic: ' + topic + '  payload: ' + payload)
            raise


def buzzer_pigpio():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    parser.add_argument("-n", dest="process_name", default="Buzzer Back End", help="Set process name in banner")

    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options['process_name'] = args.process_name

    my_buzzer_pigpio = BuzzerPigpio(**kw_options)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        my_buzzer_pigpio.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    buzzer_pigpio()

