
class Protocol:
    def __init__(self):
        self._pulse_length = 0
        self._pulse_repeat = 1
        self._pulse_0 = (0, 0)
        self._pulse_1 = (0, 0)

        self._bit_code = None
        self._pulse_code = None

    def generate_bit_code(self):
        raise NotImplementedError()

    @property
    def bit_code(self):
        return self._bit_code

    @property
    def pulse_code(self):
        return self._pulse_code

    @property
    def pulse_length(self):
        return self._pulse_length

    def get_transmit_data(self):
        if self._pulse_length == 0:
            raise ValueError(
                "The pulse_length was not overwritten in the child class")
        if self._pulse_code is None:
            raise ValueError("The bit_code was not generated")

        return {"pulse_length": self._pulse_length,
                "pulse_code": self._pulse_code,
                "pulse_repeat": self._pulse_repeat}

    def _send_0(self):
        return "1"

    def _send_1(self):
        return "0"

    def _send(self, bit):
        return self._send_0() if bit == "0" else self._send_1()

    def _transmit(self, bit):
        return self._transmit_0() if bit == "0" else self._transmit_1()

    def _transmit_0(self):
        return "1" * self._pulse_0[0] + "0" * self._pulse_0[1]

    def _transmit_1(self):
        return "1" * self._pulse_1[0] + "0" * self._pulse_1[1]

    def _convert_pulse_code(self):
        raise NotImplementedError()
