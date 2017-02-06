import requests
from pyblynkrestapi.BlynkClient import TCP_Client
import threading
import collections
import json
import logging


class PyBlynkException(Exception):
    pass

PinHandler = collections.namedtuple('PinHandler', 'pin_number handler')

class PyBlynkRestApi(object):
    """
    http://docs.blynkapi.apiary.io/#
    Wrapper around the Blynk Rest APIs

    https://github.com/xandr2/blynkapi/blob/master/blynkapi/Blynk.py
    https://github.com/xandr2/blynkapi/tree/master/blynkapi
    """
    def __init__(self, auth_token, start_heartbeat=False):
        self.server = 'blynk-cloud.com'
        self.port = '80'
        self.scheme = 'http'
        self.auth_token = auth_token
        self.blynk = TCP_Client()
        self.blynk.connect()
        self.blynk.auth(auth_token)
        self.read_pin_handlers = []
        self.set_pin_handlers = []
        self.handlers = []
        self.run_interval = None
        self.is_stopped = False
        if start_heartbeat:
            self.start_blynk_heartbeat()
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

    def _get_blynk_server_url(self):
        return "{0}://{1}:{2}/{3}".format(self.scheme, self.server, self.port, self.auth_token)

    def start_blynk_heartbeat(self):
        if not self.is_stopped:
            self.blynk.keepConnection()
            threading.Timer(2, self.start_blynk_heartbeat).start()

    def get_pin_value(self, pin_name):
        """
        Read the value from the Blynk App for the pin specified.
        For example, a common use case is to create a Button in the
        Blynk app, give it a pin number such as V1, and have this method
        read the value of the Blynk App button.

        :param pin_name:
        :return: Array of String values.
            Button: single element array of zero or one.  If the button has not been
                    pressed then the value is an empty string
            Slider: single element array of the slider value.
            JoyStick: two element array of the X/Y values.  In the definition
                      of the element, [0] element is assigned a virtual pin,
                      and the [1] element is assigned a different virtual pin.
                      The pin_name can be either of the pins assigned to the joystick
            ZeRGBa: three element array with the order in the array being:
                    Red,Green,Blue values
                    The pin_name can be any of the pins assigned to the zeRGBa
                    element.
        """
        if not pin_name:
            raise PyBlynkException(message="Invalid pin_name: {}".format(pin_name))
        try:

            url = "{}/get/{}".format(self._get_blynk_server_url(), pin_name)

            response_body = requests.get(url,params={})

            #print(response_body.json())

            pin_value = response_body.json()
            if len(pin_value) == 1:
                pin_value = pin_value[0]
        except:
            self.logger.exception("Read Pin Error")
            pin_value = None

        return pin_value

    def set_pin_value(self, pin_name, value):
        if not pin_name:
            raise PyBlynkException(message="Invalid pin_name: {}".format(pin_name))

        try:
            url = "{}/update/{}".format(self._get_blynk_server_url(), pin_name)

            payload = """
            [
                "{}"
            ]
            """.format(value)

            headers = {
                'Content-Type': 'application/json'
            }

            requests.put(url, data=payload, headers=headers, verify=False)
        except:
            self.logger.exception("Set Pin Error")
        #print("set_pin_value: {},{}".format(url, payload))

    def led_on(self, pin_name):
        self.set_pin_value(pin_name, 255)

    def led_off(self, pin_name):
        self.set_pin_value(pin_name, 0)

    def set_led(self, pin_name, value):
        if value == 0:
            self.led_off(pin_name)
        else:
            self.led_on(pin_name)

    def set_lcd(self, line0_pin_number, line0_value, line1_pin_number, line1_value):
        self.set_pin_value(line0_pin_number, line0_value)
        self.set_pin_value(line1_pin_number, line1_value)

    def add_read_pin_handler(self, pin_number, handler):
        ph = PinHandler(pin_number=pin_number, handler=handler)
        self.read_pin_handlers.append(ph)

    def add_set_pin_handler(self, pin_number, handler):
        ph = PinHandler(pin_number=pin_number, handler=handler)
        self.set_pin_handlers.append(ph)

    def add_handler(self, handler):
        ph = PinHandler(pin_number=-1, handler=handler)
        self.handlers.append(ph)

    def _run_read_handlers(self):
        # loop through all of the read pins
        for pin_handler in self.read_pin_handlers:
            try:
                pin_value = self.get_pin_value(pin_handler.pin_number)
                pin_handler.handler(pin_value, pin_handler.pin_number, self)
            except:
                self.logger.exception("Exception processing read pin handlers")

        # reset the timer to call back again
        threading.Timer(self.run_interval, self._run_read_handlers).start()

    def _run_set_handlers(self):

        # loop through all fo the set pins
        for pin_handler in self.set_pin_handlers:
            try:
                pin_value = pin_handler.handler(pin_handler.pin_number, self)
                self.set_pin_value(pin_handler.pin_number, pin_value)
            except:
                self.logger.exception("Exception processing read pin handlers")

        # reset the timer to call back again
        threading.Timer(self.run_interval, self._run_set_handlers).start()

    def _run_handlers(self):
        # loop through all of the generic handlers
        for pin_handler in self.handlers:
            try:
                pin_handler.handler(self)
            except:
                self.logger.exception("Exception processing read pin handlers")

        # reset the timer to call back again
        threading.Timer(self.run_interval, self._run_handlers).start()

    def run(self, interval):
        self.run_interval = interval
        self._run_read_handlers()
        self._run_set_handlers()
        self._run_handlers()


    def send_push_notification(self, contents):
        """

        :param contents:
        :return:
        """
        payload = {
            'body': "'{}'".format(contents),
        }


        headers = {
            'Content-Type': 'application/json'
        }

        url = "{}/notify".format(self._get_blynk_server_url())

        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        if response.status_code != 200:
            raise Exception("Send Notify Error: {}".format(response.content))


    def send_email(self, subject, contents, to_email_address=None):
        """
        Send email to the specified address or if no to_email_address
        is specified then use the email address in the email widget

        For this api to work, there has to be an email widget in the app
        and the app needs to be running.

        :param subject: Email subject
        :param title:  Email contents
        :param to_email_address: optional, address to send to.  If None
                then use the widgets email address.
        :return: void, Exception if status is not 200
        """
        if to_email_address:
            payload = {
                'to': to_email_address,
                'title': contents,
                'subj': subject
            }
        else:
            payload = {
                'title': contents,
                'subj': subject
            }


        headers = {
            'Content-Type': 'application/json'
        }

        url = "{}/email".format(self._get_blynk_server_url())

        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        if response.status_code != 200:
            raise Exception("Send Email Error: {}".format(response.content))

