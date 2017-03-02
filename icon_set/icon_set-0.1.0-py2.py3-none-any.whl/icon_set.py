from io import BytesIO

from PIL import Image

from .header import Header
from .icon_data import IconData
from .icon_type import icon_types


class IconSet():
    def __init__(self):
        self.icon_data = []

    def add_icon_data(self, icon_data):
        self.icon_data.append(icon_data)

    def as_bytearray(self):
        header_length = 4
        file_length = (
            header_length + sum(len(i.as_bytearray()) for i in self.icon_data)
        )
        header = Header(file_length)

        payload = header.as_bytearray()
        for icon_data in self.icon_data:
            payload += icon_data.as_bytearray()

        return payload

    @classmethod
    def from_png(cls, png_file_path):
        instance = cls()
        base_image = Image.open(png_file_path)
        for icon_type in icon_types:
            to_size = [icon_type.size, icon_type.size]

            new_image = base_image.resize(to_size, Image.ANTIALIAS)
            new_image_bytes = BytesIO()
            new_image.save(new_image_bytes, format='PNG')

            icon_data = IconData(icon_type, icon=new_image_bytes.getvalue())
            instance.add_icon_data(icon_data)

        return instance
