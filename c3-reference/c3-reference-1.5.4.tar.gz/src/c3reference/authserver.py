#!/bin/env python
"""Reference Implementation of v1 C3 Security Beacon Auth Server."""
import asyncio
import math
import os
import signal
import struct
import time

from binascii import hexlify
from typing import Any, Tuple
from uuid import UUID

from Crypto.Cipher import AES
from Crypto.Hash import CMAC


# Config
HEADER_LENGTH = 3
MASTER_KEY = b'\xc3' * 16
DK0_INTERVAL = 7200
DK1_INTERVAL = 86400


class PacketType:
    """Enum emulation class."""

    KEEPALIVE = 0
    DATA = 1
    SECURE = 2


BEACONS = {}  # type: Dict[bytes, Beacon]


class Beacon:
    def __init__(self, b_id: bytes) -> None:
        self.id = b_id
        cmac = CMAC.new(MASTER_KEY, ciphermod=AES)
        cmac.update(b_id)
        self.key = cmac.digest()
        self.dk = None  # type: int
        self.clock = None  # type: int
        self.clock_origin = None  # type: float
        self.mask = 0

    def validate_dk(self, new_dk: int, new_clock: int) -> bool:
        if self.dk is None or self.clock is None:
            self.dk = new_dk
            self.clock = new_clock
            return True
        # Reset and calculate mask
        for i in range(self.clock + 1, new_clock + 1):
            if i % DK0_INTERVAL == 0:
                self.evolve_dk(0)
            if i % DK1_INTERVAL == 0:
                self.evolve_dk(1)
        self.clock = new_clock
        # If the beacon has been out of sight long enough that we have
        # no contemporary dk info
        if self.mask == 0:
            self.dk = new_dk
            return True
        # Compare the incoming dk masked with our known uncertainty to
        # our generated value
        if self.dk != (new_dk & self.mask):
            print(
                """Failed DK:\n
                \tLocal : {:032b}
                \tBeacon: {:032b}
                \tMask  : {:32b}""".format(self.dk, new_dk, self.mask))
            return False
        self.dk = new_dk
        return True

    def clock_skew(self, new_clock: int) -> float:
        # Returns clock skew in seconds from expected clock time
        if self.clock_origin is not None:
            return time.time() - (self.clock_origin + new_clock)
        else:
            self.clock_origin = time.time() - new_clock
            return 0.0

    def evolve_dk(self, num: int) -> None:
        # Evolve the DK. Same algo as the "beacon", but we know we'll
        # be masking the unknown bits, so shift in zeros
        high, low = self.dk >> 16, self.dk & 0x0000ffff
        mask_high, mask_low = self.mask >> 16, self.mask & 0x0000ffff
        if num == 0:
            low = (low << 1) & 0xffff
            mask_low = (mask_low << 1) & 0xffff
        if num == 1:
            high = (high << 1) & 0xffff
            mask_high = (mask_high << 1) & 0xffff
        self.dk = (high << 16) | (low & 0xffff)
        self.mask = (mask_high << 16) | mask_low


class SecBeaconProtocol(object):
    def __init__(self):
        self._rx_buf = bytearray()
        self.transport = None

    def connection_made(self,
                        transport: Any) -> None:
        self.transport = transport
        self.peername = transport.get_extra_info('peername')[0]
        print("{} has connected".format(self.peername))

    def eof_received(self):
        print("{} has disconnected".format(self.peername))

    def data_received(self, data: bytes) -> None:
        if not 0x7e in data:
            self._rx_buf.extend(data)
        else:
            escape = False
            for byte in data:
                if byte == 0x7e:
                    if len(self._rx_buf) > 0:
                        self.process_packet(self._rx_buf)
                        self._rx_buf = bytearray()
                    continue
                elif byte == 0x7d:
                    escape = True
                    continue
                else:
                    if escape:
                        byte = byte | (1 << 5)
                        escape = False
                    self._rx_buf.append(byte)

    def process_packet(self, packet):
        # Header Parsing
        if len(packet) <= HEADER_LENGTH:
            self.transport.write(b'NACK')
            print("Bad packet from: {}".format(self.peername))
            return
        header, record_length, l_id_len = struct.unpack(
            "BBB", packet[:HEADER_LENGTH])
        # version = header >> 4  # Protocol version information unused
        packet_type = header & 0x0f
        l_id = packet[HEADER_LENGTH:HEADER_LENGTH + l_id_len]
        if not l_id:
            self.transport.write(b'NACK')
            print("Bad packet from: {}".format(self.peername))
            return
        if l_id_len == 6:
            try:
                l_id = hexlify(l_id)
            except ValueError:
                # By convention, 6 byte listener IDs will be a MAC
                # address transmitted in binary, but not always... So
                # we try to decode them into something human readable
                pass
        # Report Processing
        data = packet[HEADER_LENGTH + l_id_len:]
        if packet_type == PacketType.DATA:
            num_reports = len(data) // record_length
            for idx in range(num_reports):
                rpt = data[idx * record_length:(idx + 1) * record_length]
                uuid, major, minor, count, distance, variance = struct.unpack(
                    "!16sHHHHH", rpt)
                distance /= 100.0  # encoded as cm, converts to meters
                variance /= 100.0  # encoded as m^2/100, converts to m^2
                uuid = UUID(bytes=uuid)
                print("""\niBeacon Report: {}
\t\tListener ID: {}
\t\tUUID: {}
\t\tMajor/Minor: {}/{}
\t\tNum Sightings: {}
\t\tDistance: {}
\t\tVariance: {}\n""".format(hexlify(rpt).decode(), l_id.decode(), uuid, major,
                             minor, count, distance, variance))
        elif packet_type == PacketType.SECURE:
            (b_id, nonce, msg, tag, distance,
             variance) = struct.unpack("<6s 16s 9s 4s H H", data)
            # BLE Mac comes across the line in reverse order. We
            # reverse it for printing; but MAC calculations are on the
            # raw value
            b_id_print = bytes(
                [b_id[i] for i in range(len(b_id) - 1, -1, -1)]).hex()
            distance = distance / 100
            variance = variance / 100
            if b_id not in BEACONS:
                BEACONS[b_id] = Beacon(b_id)
            beacon = BEACONS[b_id]
            cipher = AES.new(beacon.key, AES.MODE_EAX, nonce, mac_len=4)
            cipher.update(b_id)
            try:
                plaintext = cipher.decrypt_and_verify(msg, tag)
            except ValueError as decrypt_verify_error:
                print("Payload Decipher: {}".format(
                    decrypt_verify_error))
                print("""
Error: {0}
Packet:
\tListener ID: {1}
\tBeacon ID: {2}
\tNonce: {3}
\tPayload: {4}
\tTag: {5}
\tDistance: {6}m
\tVariance: {7}""".format(decrypt_verify_error, l_id.decode(),
                          b_id_print,
                          nonce.hex(), msg.hex(),
                          tag.hex(), distance, variance))
                return
            (clock, dk, flags) = struct.unpack("<IIB", plaintext)
            if beacon.clock and clock <= beacon.clock:
                if beacon.clock_skew(clock) > 2:
                    # Reject old clock values
                    print("Attempted replay of {}".format(clock))
                return
            dk_valid = beacon.validate_dk(dk, clock)
            if dk_valid:
                beacon.mask = 0xffffffff
            print("""
Packet: {0}
\tListener ID: {1}
\tBeacon ID: {2:08x}
\tNonce: {3}
\tPayload: {4}
\t\tClock: {5} (Skew: {6:.2f}s)
\t\tDK: 0x{7:08x} ({8})
\t\tFlags: 0x{9:02x}
\tTag: {10}
\tDistance: {11}m
\tVariance: {12} ({13:.2}m)""".format(hexlify(packet).decode(),
                                      l_id.decode(),
                                      int.from_bytes(b_id, 'big'),
                                      nonce.hex(),
                                      msg.hex(),
                                      clock, beacon.clock_skew(clock), dk,
                                      "Valid" if dk_valid else "Invalid",
                                      flags, tag.hex(), distance, variance,
                                      math.sqrt(variance) * 3))
        elif packet_type == PacketType.KEEPALIVE:
            print("Keepalive from {}".format(hexlify(l_id)))
        else:
            print("Unknown Packet from {}".format(self.peername))
        self.transport.write(b'ACK')

    def error_received(self, exc: Exception) -> None:
        print('Error received:', exc)

    def connection_lost(self, exc: Exception) -> None:
        print("{} has disconnected".format(self.peername))


def start_server(loop, port):
    return loop.create_server(SecBeaconProtocol, port=port)



def main() -> None:
    loop = asyncio.get_event_loop()
    if signal is not None and os.name != 'nt':
        loop.add_signal_handler(signal.SIGINT, loop.stop)

    server = loop.run_until_complete(start_server(loop, 9999))
    print("Listening on {}:{}".format("", 9999))
    loop.run_forever()
    server.close()
    loop.close()


if __name__ == '__main__':
    main()
