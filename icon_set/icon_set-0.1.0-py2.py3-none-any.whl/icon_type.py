# -*- coding: utf-8 -*-

from .exceptions import InvalidIconTypeError


class IconType(object):
    def __init__(self, os_type, size, description=None):
        field_size = 4
        if len(os_type) != field_size:
            raise InvalidIconTypeError()

        self.os_type = os_type
        self.size = size
        self.description = description

    def as_bytearray(self):
        """
        +-----------------------------+
        | Octet       |       0       |
        | Bit         | 0 | 1 | 2 | 3 |
        +-------------+---------------+
        | Description |     OSType    |
        +-----------------------------+
        """
        return bytearray(self.os_type, encoding='ascii')


icon_types = [
    IconType(os_type='icp4', size=16, description='16x16 icon in JPEG 2000 or PNG format'),  # noqa
    IconType(os_type='icp5', size=32, description='32x32 icon in JPEG 2000 or PNG format'),  # noqa
    IconType(os_type='ic07', size=128, description='128x128 icon in JPEG 2000 or PNG format'),  # noqa
    IconType(os_type='ic08', size=256, description='256×256 icon in JPEG 2000 or PNG format'),  # noqa
    IconType(os_type='ic09', size=512, description='512×512 icon in JPEG 2000 or PNG format'),  # noqa
    IconType(os_type='ic10', size=1024, description='1024×1024 in 10.7 (or 512x512@2x "retina" in 10.8) icon in JPEG 2000 or PNG format'),  # noqa
    IconType(os_type='ic11', size=32, description='16x16@2x "retina" icon in JPEG 2000 or PNG format'),  # noqa
    IconType(os_type='ic12', size=64, description='32x32@2x "retina" icon in JPEG 2000 or PNG format'),  # noqa
    IconType(os_type='ic13', size=256, description='128x128@2x "retina" icon in JPEG 2000 or PNG format'),  # noqa
    IconType(os_type='ic14', size=512, description='256x256@2x "retina" icon in JPEG 2000 or PNG format')  # noqa
]
