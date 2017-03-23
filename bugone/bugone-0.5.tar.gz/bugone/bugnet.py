"""
Module to deal w/ bugnet packets, extract, build .. and send """


PACKET_HELLO  = 0x01
PACKET_PING   = 0x02
PACKET_PONG   = 0x03
PACKET_GET    = 0x04
PACKET_SET    = 0x05
PACKET_VALUES = 0x06


class BugNet(object):
    def __init__(self,connector):
        self.cn = connector

    def hello(self):
        """ send a hello packet """
        self.cn.send(build_packet(0xFF, PACKET_HELLO))

    def ping(self,dst):
        """ send a ping packet """
        self.cn.send(build_packet(dst, PACKET_PING))

    def pong(self,dst):
        """ send a pong packet """
        self.send(build_packet(dst, PACKET_PONG))

    def set_value(self,dst, src_dev, dst_dev, value):
        """ send a set value packet """
        data = pack_values([(src_dev, dst_dev, value),(0xFF,0xFF,0)])
        self.cn.send(build_packet(dst, PACKET_SET, data=data))

    def request_value(self,dst, src_dev, dst_dev,):
        """ send get value packet & wait for the answer """
        data = pack_values([(src_dev, dest_dev),(0xFF,0xFF)])
        self.send(build_packet(dst, PACKET_GET, data=data))
        data = self.cn.receive()
        if data:
            p = Packet(data)
            if p.type == PACKET_VALUES:
                return p.values[0][2]
        return None

    def receive(self):
        data = self.cn.receive()
        if data and len(data) > 5:
            return Packet(data)

class Packet(object):
    """ Packet API, return formatted binary packet """

    def __init__(self,data = None):
        self.bin = data

    @property
    def src(self):
        """ packet source addr """
        return ord(self.bin[0])

    @property
    def dst(self):
        """ packet dst addr / usually 255 => broadcast """
        return ord(self.bin[1])

    @property
    def router(self):
        """ is it a router / unused right now"""
        return ord(self.bin[2])

    @property
    def type(self):
        """ return packet type """
        return ord(self.bin[3])

    @property
    def counter(self):
        """ return packet counter """
        return bytes_to_integer(self.bin[4:6])

    @property
    def data(self):
        """ return packet payload """
        return self.bin[6:]

    @property
    def values(self):
        """ extract packet values """
        values = []
        data = self.data
        while len(data) > 3:
            src_dev = ord(data[0])
            dst_dev = ord(data[1])
            value_type = data[2]
            value = None
            if value_type == 'I':
                value = bytes_to_integer(data[3:5])
                data = data[5:]
            elif value_type == 'S':
                count = ord(data[3])
                value = data[4:4+count]
                data  = data[4+count:]
            else:
                break
            values.append((src_dev, dst_dev, value))
        return values

    def __str__(self):
        s = "src: %d dst: %d type: %d values [%s] [%d]" % (self.src,self.dst,self.type,self.values,self.counter)
        return s


def build_packet(dst, type_, src = 0, counter = 0, payload = None):
    """ forge a packet """
    data  = chr(src)
    data += chr(dst)
    data += chr(0)
    data += chr(type_)
    data += integer_to_bytes(counter)
    if payload:
        data += payload
    return data


def pack_values(values):
    """ pack a list of values in a payload format """
    data = ""
    for (src_dev, dst_dev, value) in values:
        data += chr(src_dev)
        data += chr(dst_dev)
        if type(value) is int:
            data += 'I' + integer_to_bytes(value)
        elif type(value) is str:
            data += 'S' + chr(len(value)) + value
    return data


def bytes_to_integer(bytes, bigEndian = True):
    res = 0
    if bigEndian: bytes = bytes[::-1]
    for b in bytes:
        res = res << 8
        res += ord(b)
    return res

def integer_to_bytes(value):
    return chr(value & 0x00FF) + chr((value & 0xFF00) >> 8)

