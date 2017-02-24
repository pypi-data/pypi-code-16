
from .protocol import Protocol


class HomeEasy(Protocol):

    def __init__(self, address=None, device=None, onoff=None):
        super(self.__class__, self).__init__()

        self._pulse_length = 275
        self._pulse_repeat = 5
        self._pulse_0 = (1, 1)
        self._pulse_1 = (1, 5)

        self._address_length = 26
        self._device_length = 4
        self._group = "0"

        self.address = int(address)
        self.set_device(device)
        self.set_onoff(onoff)

    def set_device(self, device):
        self.device = int(device)

    def set_onoff(self, onoff):
        self.onoff = bool(onoff)

    def generate_bit_code(self):
        address_bin = "{0:b}".format(self.address).zfill(self._address_length)
        device_bin = "{0:b}".format(self.device).zfill(self._device_length)
        onoff_bin = "1" if self.onoff else "0"

        self._bit_code = ""
        # Address bits
        print()
        for i in address_bin:
            self._bit_code += self._send(i)

        # Group
        self._bit_code += self._send_0()

        # ON/OFF
        self._bit_code += self._send(onoff_bin)

        # Device
        for i in device_bin:
            self._bit_code += self._send(i)

        self._bit_code += "0"

        # Generate pulses for the bit_code
        self._convert_pulse_code()

    def _send_0(self):
        return "01"

    def _send_1(self):
        return "10"

    def _convert_pulse_code(self):
        # Initial pulses for HomeEasy protocol
        self._pulse_code = "1"
        self._pulse_code += "0".zfill(36)
        self._pulse_code += "1"
        self._pulse_code += "0".zfill(10)

        for i in self._bit_code:
            self._pulse_code += self._transmit(i)
