
import serial
import serial.tools.list_ports


class Arduino433:

    def __init__(self, port=None, baudrate=9600):
        self._transmit_data_format = "#<pulse_length>:<pulse_code>:<repeat>\0"
        self.available_devices = Arduino433.list_devices()
        self.baudrate = baudrate
        self.set_port(port)

    def set_port(self, port):
        self.port = port if port in self.available_devices else None
        if self.port is None:
            raise SystemError("Device doesnt exist")
        self.comm = serial.Serial(self.port, self.baudrate)

    def open(self):
        self.close()
        self.comm.open()

    def close(self):
        self.comm.close()

    def send(self, msg):
        message = self._transmit_data_format.replace(
                            "<pulse_length>", str(msg["pulse_length"])
                            ).replace(
                            "<pulse_code>", str(hex(int(msg["pulse_code"], 2)))
                            ).replace(
                            "<repeat>", str(msg["pulse_repeat"]))
        self.comm.write(bytes(message, encoding="ascii"))

    def receive(self):
        # TODO: Read non blocking until separator is received. id:3
        #       Method only returns once a full msg exists
        # self.comm.read()
        raise NotImplementedError()

    def list_devices():
        return [i.device for i in serial.tools.list_ports.comports()]
