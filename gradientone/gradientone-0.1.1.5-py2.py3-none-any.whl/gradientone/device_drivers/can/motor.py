import sys
from time import time
from configparser import ConfigParser
from CANcard import CanCard, CanFrame
from can_helpers import *
from numpy import reshape
from ctypes import c_short
from gradientone import gateway_helpers

cfg = ConfigParser()
cfg.read('/etc/gradient_one.cfg')

### REMOVE THIS BEFORE IT GOES TO THE CUSTOMER
try:
    from raven import Client
    SENTRY_CLIENT = Client(cfg['client']['SENTRY'])
except Exception:
    SENTRY_CLIENT = gateway_helpers.MySentry()
###


PROPERTIES = properties_from_cfg()
INDEX_MAP = generate_index_map(PROPERTIES)
TIMEOUT = 10

STATUS = [['Ready to Switch On', 11], ['Switched on', 10],
          ['Operation Enabled', 12], ['Fault', 5], ['Voltage enabled', 14],
          ['Quick Stop', 2], ['Switch on disabled', 13], ['Warning', 6],
          ['Last trajectory was aborted', 1], ['Remote', 8],
          ['Target Reached', 0], ['Internal Limit Active', 9],
          ['Setpoint acknowledge', 7], ['Following error', 4], ['Moving', 3],
          ['Reserved', 15]]

TRACE_SCALE = 5


class Motor(CanCard):
    def __init__(self, fname=None):
        super(Motor, self).__init__()
        self.fname = fname
        self.frame = None
        # Copley has 8 PDOs. More pieces of data could be delivered if
        # multiple values are assigned to a PDO, but only 8 are used for now.
        self._properties = [None, None, None, None, None, None, None, None]
        self._trace_properties = []
        self._last_assigned = -1
        self._last_values = {}
        self.unplugged = False
        self.trace_reference_period = None
        self.logs = []
        self.verbose = True
        self.address_map = INDEX_MAP

    @property
    def operation(self):
        return True

    @operation.setter
    def operation(self, state):
        data = [0x01 if state else 0x80] + [0x01]
        # ID of master node
        preop = CanFrame(id=0x000, data=data)
        self.xmit(preop)

    @property
    def moving(self):
        return int_to_bit_list(self.property_getter('status_word'))[14]

    @property
    def status(self):
        status_formatted = int_to_bit_list(self.property_getter('status_word'))
        _status = []
        for i in range(len(status_formatted)):
            if status_formatted[i]:
                _status.append(STATUS[i])
        _status = [t[0] for t in sorted(_status, key=lambda t: t[1])]
        return ",".join(_status)

    def log(self, msg):
        if self.verbose:
            print(msg)
        SENTRY_CLIENT.captureException(msg)
        self.logs.append(msg)

    def acknowledge(self):
        if self.unplugged:
            return
        self.sync()
        _ack = self.recv(timeout=TIMEOUT)
        while _ack is not None:
            if len(_ack.data) == 0:
                _ack = self.recv(timeout=TIMEOUT)
                continue
            # if you got an incoming PDO, try again
            if _ack.explanation.find("ERROR") == 0:
                if _ack.explanation.find("no transmit ack") > 0:
                    # if you get a transmit ack error, assume that the motor
                    # is unplugged, exit.
                    self.unplugged = True
                self.log(_ack.explanation)
            elif 255 < _ack.id < 1280:
                self.handle_pdo(_ack)
            elif _ack.id == 0x581:
                if 0x40 < _ack.data[0] < 0x50:
                    self.handle_sdo(_ack.data)
            _ack = self.recv(timeout=TIMEOUT)

    def clear_pdos(self):
        for i in range(8):
            if self.unplugged:
                return
            self.send_sdo(address=[0x1a, i, 0x00], data=[0x00])
            if self.unplugged:
                return
            self.send_sdo(address=[0x18, i, 0x01],
                          data=[0x81, i + 1, 0x00, 0x80])
        self._properties = [None, None, None, None, None, None, None, None]

    def handle_pdo(self, in_frame):
        id_index = in_frame.id - 0x181
        if id_index >= len(self._properties):
            raise ValueError("Got weird id: "+ str(id_index) + "frame id:" + str(in_frame.id) + " properties: "+str(self._properties)) 
        property_name = self._properties[id_index]
        if property_name is None:
            return
        in_data = in_frame.data
        self.set_value(in_data, property_name)

    def set_value(self, in_data, property_name):
        _width = PROPERTIES[property_name]['width']
        if _width != len(in_data):
            self.log(property_name+ " is "+ str(len(in_data))+ "expected" +
                     str(_width))

        if 'scale' in PROPERTIES[property_name].keys():
            _scale = PROPERTIES[property_name]['scale']
        else:
            _scale = 1

        _data_type = PROPERTIES[property_name]['type']
        if len(in_data) < 5:
            output = 0
            for byte_num in range(len(in_data)):
                output += in_data[byte_num] << 8 * byte_num
        else:
            output = in_data
        self._last_values["_" + property_name] = _data_type(output) * _scale

    def handle_sdo(self, data):
        """
        Get data from an incoming SDO, and store it in .
        :param data: the data part of the incoming CAN frame
        :return: nothing
        """
        width = float(0x4F - data[0]) / 4 + 1
        _addr = [data[2], data[1], data[3]]

        index = address_list_to_string(_addr)
        property_name = INDEX_MAP[index]
        out_data = []
        if width > 4:   
            # get the length of the data from the SDO
            width = data[4]
            # create a dummy response frame to get the toggle order right
            in_frame = CanFrame(data=[0x10, 0, 0, 0, 0, 0, 0, 0])
            while in_frame.data[0] == 0x10 or in_frame.data[0] == 0x00:
                toggle_byte = 0x60 if in_frame.data[0] == 0x10 else 0x70
                self.send_sdo(command_code=toggle_byte, address=[0, 0, 0],
                              data=[], acknowledge=False)
                in_frame = self.recv(timeout=TIMEOUT)
                # chop and invert bits 4:1
                num_bytes = (((in_frame.data[0] & 0x0e) >> 1) ^ 0xFF) & 0x07
                out_data += in_frame.data[1:num_bytes + 1]
                width -= num_bytes
        else:
            out_data = data[4:]
        self.set_value(out_data, property_name)

    def move(self, steps=0):
        # Set to profile position mode.  (Move to a target position).
        self.send_sdo(address=[0x60, 0x60, 0x00], data=[0x01])
        # Set target position to steps
        self.send_sdo(address=[0x60, 0x7A, 0x00],
                      data=int_to_hexes(steps, width=4))
        # Set control word bit 4 to 1 (move)
        self.send_sdo(address=[0x60, 0x40, 0x00], data=[0x3F, 0x00])
        # Set control word bit 4 to 0 (done with move commands)
        self.send_sdo(address=[0x60, 0x40, 0x00], data=[0x2F, 0x00])

    def send_sdo(self, address, data, acknowledge=True, command_code=None):
        if command_code is None:
            hex1 = 0x33-4*len(data)
            command_code = 0x21 if hex1 < 0 else hex1
        while len(data) < 4:
            data.append(0)
        data = [command_code]+[address[1]]+[address[0]]+[address[2]]+data
        self.frame = CanFrame(id=0x601, data=data)
        self.xmit(self.frame)
        if acknowledge:
            self.acknowledge()

    def property_getter(self, property_name='current'):
        if PROPERTIES[property_name]['pdo']:
            if property_name not in self._properties:
                self.operation = False
                self.setup_read(property_name)
                self.operation = True
                self.acknowledge()
        else:
            self.send_sdo(command_code=0x40, data=[],
                          address=PROPERTIES[property_name]['index'],
                          acknowledge=False)
            _ack = self.recv(timeout=TIMEOUT)
            self.handle_sdo(_ack.data)
        try: 
            return self._last_values["_" + property_name]
        except Exception as e:
            print(property_name, "not in", self._last_values)
            return None

    def setup_read(self, property_name='current'):
        if property_name in self._properties:
            return
        value = PROPERTIES[property_name]['index']
        bit_width = PROPERTIES[property_name]['width'] * 8
        self._last_assigned += 1
        if self._last_assigned == len(self._properties):
            self._last_assigned = 0
        # Set Number of Mapped objects to zero
        self.send_sdo(address=[0x1A, self._last_assigned, 0x00], data=[0x00])

        # Turn off the TPD last_assigned
        self.send_sdo(address=[0x18, self._last_assigned, 0x01], 
                      data=[0x81 + self._last_assigned, 0x01, 0x00, 0x80])
        # set transmission to every sync
        self.send_sdo(address=[0x18, self._last_assigned, 0x02],
                      data=[0x01])
        # map PDO
        self.send_sdo(address=[0x1A, self._last_assigned, 0x01],
                      data=[bit_width] + [value[2], value[1], value[0]])
        # Turn on the TPDO
        self.send_sdo(address=[0x18, self._last_assigned, 0x01],
                      data=[0x81 + self._last_assigned, 1, 0, 0])
        # Set Number of total Mapped objects to one
        self._properties[self._last_assigned] = property_name
        self.send_sdo(address=[0x1A, self._last_assigned, 0x00],
                      data=[0x01])

    def setup_trace(self, trace_delay=0.0, trace_time=1.0, max_samples=10000,
                    trigger_config=0):
        """
        Setup the CAN Bus to read data in as a trace (instead of as a pdo)
        """
        # first, clear all trace channels
        for chan in range(6):
            chan_name = "trace_channel_"+str(chan+1)
            self.send_sdo(address=PROPERTIES[chan_name]['index'],
                          data=[0, 0])
        
        for property_index in range(len(self._trace_properties)):
            chan_name = "trace_channel_"+str(property_index+1)
            address_hexes = int_to_hexes(lookup_trace_variable_address(
                                         self._trace_properties[property_index]),
                                         width=2)
            self.send_sdo(address=PROPERTIES[chan_name]['index'],
                          data=address_hexes)
        if self.trace_reference_period is None:
            self.trace_reference_period = self.property_getter("trace_reference_period")
        # set the trace_delay
        delay_units = int(trace_delay/self.trace_reference_period)
        self.send_sdo(address=PROPERTIES["trace_delay"]["index"],
                      data=int_to_hexes(delay_units, width=2))
        max_samples = self.property_getter("trace_max_samples")
        # set the trace time
        trace_time /= TRACE_SCALE
        trace_time /= max_samples
        trace_time = int(trace_time/self.trace_reference_period)
        self.send_sdo(address=PROPERTIES["trace_period"]["index"],
                      data=int_to_hexes(trace_time, width=2)[0:2])
        # set the trigger type
        # TODO: break this into components
        trigger_config = int_to_hexes(trigger_config, width=6)
        self.send_sdo(address=PROPERTIES["trace_trigger_configuration"]["index"],
                      data=trigger_config)

    def sync(self):
        sf = CanFrame(id=0x80, data=[])
        self.xmit(sf)

    def do_trace(self, max_counts, max_time, properties, sync=True):
        if sync:
            data = []
            start = time()
            measure_time = time() - start
            while measure_time < max_time and len(data) < max_counts:
                self.move(0)
                measure_time = time() - start
                _point = {'measure_time': measure_time}
                for _property in properties:
                    _point[_property] = self.property_getter(_property)
                data.append(_point)
        else:
            self.clear_pdos()
            self._trace_properties = properties
            self.setup_trace(max_samples=max_counts, trace_time=max_time)
            max_samples = min(self.property_getter("trace_max_samples"), max_counts)
            self.send_sdo(address=PROPERTIES["trace_trigger"]["index"],
                          data=[0, 1])
            last_samples = None
            samples = self.property_getter("trace_sample_count")
            while samples != max_samples:
                self.move(2**16-2)
                self.acknowledge()
                samples = self.property_getter("trace_sample_count")
                if samples != last_samples:
                    last_samples = samples
            self.send_sdo(address=PROPERTIES["trace_trigger"]["index"],
                          data=[0, 0])
            
            trace_period = self.property_getter("trace_period")
            data_array = self.property_getter("trace_data")
            data_array = reshape(data_array, (samples, len(self._trace_properties)))
            data = []
            for row_index in range(len(data_array)):
                _point = {'measure_time': TRACE_SCALE*row_index*trace_period*self.trace_reference_period}
                for col_index in range(len(self._trace_properties)):
                    to_int = c_short(data_array[row_index][col_index]).value
                    input_name = self._trace_properties[col_index]
                    units = lookup_trace_variable_units(input_name)
                    _point[self._trace_properties[col_index]] = to_int*units
                data.append(_point)

        return data


def get_hardware_info(card):
    card.clear_pdos()
    output = {}
    parts =['motor_manufacturer', 'motor_model', 'model_number',
            'model_number', 'drive_name', 'firmware_version_number',
            'drive_hardware_type']
    for part in parts:
        _result = card.property_getter(part)
        output[part] = int(_result) if type(_result) is not str and type(_result) is not bool else _result
    return output


if __name__ == "__main__":
    
    # instantiate the motor controller
    dev = '/dev/copleycan00'
    card = Motor(dev)
    card.open(baud=1000000)
    if card.unplugged:
        print("card unplugged. aborting")
        sys.exit()
    print(get_hardware_info(card))
    print("going to home")
    print(card.status)

