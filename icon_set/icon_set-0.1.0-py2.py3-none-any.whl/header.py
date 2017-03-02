import struct

from .exceptions import FileLengthTooLargeError


class Header(object):
    _max_file_length = 0xFFFFFFFF

    def __init__(self, file_length):
        if file_length > self._max_file_length:
            raise FileLengthTooLargeError(
                'File length cannot be larger than {} bytes (~{:.1f} GB). '
                'This is because the Icon Set file structure cannot '
                'represent larger file lengths.'.format(
                    self._max_file_length,
                    self._max_file_length / (1024.0 ** 3)
                )
            )

        self.file_length = file_length

    def as_bytearray(self):
        """
        +---------------------------------------------+
        | Octet       |       0       |         1     |
        | Bit         | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
        +-------------+---------------+---------------+
        | Description | magic literal |  file length  |
        +---------------------------------------------+
        """
        file_length_packed = struct.pack('>I', self.file_length)
        return bytearray('icns', encoding='ascii') + file_length_packed
