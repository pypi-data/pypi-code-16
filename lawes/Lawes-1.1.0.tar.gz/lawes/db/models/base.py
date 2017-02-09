# -*- coding:utf-8 -*-

from lawes.db.models.query import queryset
from lawes.db.models.fields import Field

class ModelBase(type):

    def __new__(cls, name, bases, attrs):
        """ 将 Field 转换成对于真实的数据
        """
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        attrs['local_fields'] = {}
        for attr in attrs:
            if hasattr(attrs[attr], 'contribute_to_class'):
                attrs['local_fields'][attr] = attrs[attr]
            if isinstance(attrs[attr], Field):
                attrs[attr] = attrs[attr].value
        return type.__new__(cls, name, bases, attrs)

class Model(object):

    __metaclass__ = ModelBase
    pk_attname = '_id'
    queryset = queryset
    save_fields = []

    def __setattr__(self, key, value):
        super(Model, self).__setattr__(key, value)
        if key in self.local_fields:
            self.local_fields[key].check_type(value=value)
        if hasattr(self, '_id'):
            self.save_fields.append(key)

    def save(self):
        self._save_table()

    def _save_table(self):
        pk_val = self._get_pk_val()
        # true: UPDATE; false: INSERT
        pk_set = pk_val is not None
        if pk_set:
            self._do_update(obj=self)
        else:
            result = self._do_insert(obj=self)
            setattr(self, self.pk_attname, result)

    def _get_pk_val(self):
        """ 获得 _id: None: INSERT; not None: UPDATE
        """
        if not hasattr(self, self.pk_attname):
            return None
        else:
            return getattr(self, self.pk_attname)

    @classmethod
    def _do_insert(cls, obj):
        """ 向 mongodb 插入数据
        """
        return cls.queryset._insert(obj_class=cls, obj=obj)

    @classmethod
    def _do_update(cls, obj):
        """ 向 mongodb 更新数据
        """
        return cls.queryset._update(obj_class=cls, obj=obj)

    @classmethod
    def filter(cls, **query):
        objs = []
        for record in cls.queryset.get_multi(obj_class=cls, **query):
            obj = cls()
            for field in cls.local_fields:
                if field in record:
                    value = record[field]
                else:
                    value = cls.local_fields[field].value
                setattr(obj, field, value)
            obj._id = record['_id']
            objs.append(obj)
        return objs

    @classmethod
    def get(cls, **query):
        obj = cls.filter(**query)
        if len(obj) >= 2:
            raise 'The len > 2!'
        elif len(obj) == 0:
            raise 'The len is 0!'
        return obj[0]

    def to_dict(self, fields=''):
        """ fields： save_fields 显示仅修改的部分
        """
        if fields == 'save_fields':
            fields_type = self.save_fields
        else:
            fields_type = self.local_fields
        result = { field: getattr(self, field) for field in fields_type if hasattr(self, field) }
        if hasattr(self, '_id'):
            result['_id'] = self._id
        return result