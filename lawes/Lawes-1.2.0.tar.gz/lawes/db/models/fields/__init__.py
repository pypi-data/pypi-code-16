# -*- coding:utf-8 -*-

from lawes.db.models.lookups import RegisterLookupMixin
import datetime
from lawes.core.exceptions import ValidationError

class CheckTypeNone(object):
    pass

class Field(RegisterLookupMixin):
    """ 用于标识是否需要转换和存储的字段
    """
    contribute_to_class = None
    error_message = "{value} value has an invalid format. It must be in {value_type} format."
    # 可以不用设置 default, 获得设置成空
    default_can_set_null = False

    def __init__(self, default=None, db_index=False, unique=False):
        self.default = default
        self.value = default
        self.check_type()
        self.db_index = db_index
        self.unique = unique

    def check_type(self, value=CheckTypeNone()):
        """ 检测子类的类型是否正确
        """
        check_value = value if not isinstance(value, CheckTypeNone) else self.value
        if self.default_can_set_null is True and check_value is None:
            return True
        if not isinstance(check_value, self.field_type):
            raise ValidationError(message=self.error_message,params={'value': check_value, 'value_type': str(self.field_type)},)
        return True

class CharField(Field):

    field_type = str

    def __init__(self, *args, **kwargs):
        super(CharField, self).__init__(*args, **kwargs)

class IntegerField(Field):

    field_type = int

    def __init__(self, *args, **kwargs):
        super(IntegerField, self).__init__(*args, **kwargs)

class FloatField(Field):

    field_type = float

    def __init__(self, *args, **kwargs):
        super(FloatField, self).__init__(*args, **kwargs)

class DateTimeField(Field):

    field_type = datetime.datetime
    default_can_set_null = True

    def __init__(self, *args, **kwargs):
        super(DateTimeField, self).__init__(*args, **kwargs)

class BooleanField(Field):

    field_type = bool

    def __init__(self, *args, **kwargs):
        super(BooleanField, self).__init__(*args, **kwargs)

class ArrayField(Field):

    field_type = list

    def __init__(self, *args, **kwargs):
        super(ArrayField, self).__init__(*args, **kwargs)
