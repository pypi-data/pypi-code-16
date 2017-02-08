# -*- coding:utf-8 -*-

from lawes.db.models.lookups import RegisterLookupMixin
import datetime

class NOT_PROVIDED:
    pass

class Field(RegisterLookupMixin):
    # 用于标识是否需要转换和存储的字段
    contribute_to_class = None

    def __init__(self, default=NOT_PROVIDED, ):
        self.default = default
        self.value = default

class CharField(Field):
    # TODO index
    def __init__(self, *args, **kwargs):
        super(CharField, self).__init__(*args, **kwargs)
        if not isinstance(self.default, str):
            raise "default error"
        self.value = self.default

class IntegerField(Field):
    # TODO
    def __init__(self, *args, **kwargs):
        super(IntegerField, self).__init__(*args, **kwargs)
        if not isinstance(self.default, int):
            raise "default error"
        self.value = int(self.default)

class FloatField(Field):
    # TODO
    def __init__(self, *args, **kwargs):
        super(FloatField, self).__init__(*args, **kwargs)
        if not isinstance(self.default, float):
            raise "default error"
        self.value = float(self.default)

class DateTimeField(Field):
    # TODO
    def __init__(self, *args, **kwargs):
        super(DateTimeField, self).__init__(*args, **kwargs)
        if not isinstance(self.default, datetime):
            raise "default error"
        self.value = str(self.default)

class BooleanField(Field):
    # TODO
    def __init__(self, *args, **kwargs):
        super(BooleanField, self).__init__(*args, **kwargs)
        if not isinstance(self.default, bool):
            raise "default error"
        self.value = bool(self.default)