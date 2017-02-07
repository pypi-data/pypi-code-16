import enum


class FileFormat(enum.Enum):
    registry = enum.auto()
    known_hosts = enum.auto()
