import struct


class IconData(object):
    def __init__(self, icon_type, icon):
        self.icon_type = icon_type
        self.icon = icon

    def as_bytearray(self):
        """
        +---------------------------------------------------------+
        | Octet       |       0       |       1       |    ...    |
        | Bit         | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |    ...    |
        +-------------+---------------+---------------+-----------+
        | Description |     OSType    |     length    | icon data |
        +---------------------------------------------+-----------+
        """
        icon_type_as_bytearray = self.icon_type.as_bytearray()
        length = len(icon_type_as_bytearray) + 4 + len(self.icon)
        length_packed = struct.pack('>I', length)
        return icon_type_as_bytearray + bytearray(length_packed) + self.icon
