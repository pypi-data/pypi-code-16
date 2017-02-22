from oem_format_json.main import JsonFormat
from oem_format_minimize.main import MinimalFormat


class JsonMinimalFormat(JsonFormat, MinimalFormat):
    __key__ = 'minimize+json'

    __extension__ = 'min.json'
