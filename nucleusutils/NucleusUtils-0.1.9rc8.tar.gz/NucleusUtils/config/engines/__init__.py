from .json import JsonLoader
from .xml import XmlLoader

default = (
    ('json', JsonLoader),
    ('xml', XmlLoader),
)
