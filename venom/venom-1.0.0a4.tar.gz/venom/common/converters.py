import calendar
from typing import TypeVar, Generic

import datetime

from venom.common.messages import Int64Value, Int32Value, StringValue, Float32Value, Float64Value, BoolValue, Timestamp, \
    BytesValue
from venom.converter import Converter

V = TypeVar('V')
T = TypeVar('T')


class _ValueConverter(Generic[V, T], Converter):
    def convert(self, message: V) -> T:
        return message.value

    def format(self, value: T) -> V:
        return self.wire(value=value)


class StringValueConverter(_ValueConverter[StringValue, str]):
    wire = StringValue
    python = str


class BytesValueConverter(_ValueConverter[BytesValue, bytes]):
    wire = BytesValue
    python = bytes


class BooleanValueConverter(_ValueConverter[StringValue, bool]):
    wire = BoolValue
    python = bool


class Int32ValueConverter(_ValueConverter[Int32Value, int]):
    wire = Int32Value
    python = int


class Int64ValueConverter(_ValueConverter[Int64Value, int]):
    wire = Int64Value
    python = int


IntegerValueConverter = Int64ValueConverter


class Float32ValueConverter(_ValueConverter[Float32Value, float]):
    wire = Float32Value
    python = float


class Float64ValueConverter(_ValueConverter[Float64Value, float]):
    wire = Float64Value
    python = float


NumberValueConverter = Float64ValueConverter


class DateConverter(Converter):
    wire = Timestamp
    python = datetime.date

    def convert(self, value: Timestamp) -> datetime.date:
        return datetime.datetime.fromtimestamp(value.seconds).date()

    def format(self, value: datetime.date) -> Timestamp:
        return Timestamp(int(calendar.timegm(value.timetuple())))


class DateTimeConverter(Converter):
    wire = Timestamp
    python = datetime.datetime

    def convert(self, value: Timestamp) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(value.seconds + value.nanos / 10 ** 9)

    def format(self, value: datetime.datetime) -> Timestamp:
        unix = calendar.timegm(value.timetuple())
        seconds = int(unix)
        nanos = int((unix - seconds) * 10 ** 9)
        return Timestamp(seconds, nanos)
