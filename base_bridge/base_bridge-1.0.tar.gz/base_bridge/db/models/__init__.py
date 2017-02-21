# coding=utf-8
__author__ = 'Maple.Liu'

import time
import uuid
import json
from .fields import *
from django.db.models.query import QuerySet

SOFT_DELETE_FIELD_NAME = 'is_deleted'


def get_uuid_str():
    """
    获取UUID的字符串
    :return:
    """
    return uuid.uuid4().hex


def get_time_stamp():
    """
    获取整型时间戳
    :return:
    """
    return int(time.time())


class ModelManager(raw_models.Manager):
    def get_queryset(self):
        """
        自定义过滤QuerySet
        :return:
        """
        if SOFT_DELETE_FIELD_NAME in [e.name for e in self.model._meta.fields]:
            return QuerySet(self.model, using=self._db).filter(is_deleted=False)
        else:
            return QuerySet(self.model, using=self._db)



class Model(raw_models.Model):
    class Meta:
        abstract = True

    # 使用自扩展Manager
    objects = ModelManager()

    # 序列化输出的字段
    output_fields = []

    # 时间日期格式
    datetime_format = '%Y-%m-%d %H:%M:%S'

    # 公共字段
    uuid = CharField(verbose_name=u'UUID', max_length=32, default=get_uuid_str)
    add_timestamp = BigIntegerField(verbose_name=u'入库时间', default=get_time_stamp)
    update_timestamp = BigIntegerField(verbose_name=u'更新时间', default=get_time_stamp)
    is_deleted = BooleanField(verbose_name=u'是否已删除', default=False)

    def as_dict(self, keys=None):
        """
        将ORM对象序列化为字典
        :param keys:
        :return:
        """
        if not keys:
            keys = self.output_fields
        keys += ['add_timestamp', 'update_timestamp', 'uuid']
        object_dict = dict()
        for key in keys:
            value = last_value = getattr(self, key)
            if isinstance(value, raw_models.Model):
                if isinstance(value, self.__class__):
                    last_value = value.__unicode__()
                else:
                    last_value = value.as_dict()
            if last_value is None:
                last_value = ''
            object_dict[key] = last_value
            key_field = self.__class__._meta.get_field(key)
            if key_field.choices: # 如果是下拉列表字段
                object_dict[key+'_map'] = dict(key_field.choices)
        return object_dict

    def as_json(self, keys=None):
        """
        JSON序列化
        :param keys:
        :return:
        """
        return json.dumps(self.as_dict(keys))

    def get_add_time(self):
        """
        从ORM对象时间戳转换为字符串时间格式
        :return:
        """
        return time.strftime(self.datetime_format, time.localtime(self.add_timestamp))
    get_add_time.allow_tags = True
    get_add_time.short_description = u'添加时间'

    def get_update_time(self):
        """
        从ORM对象时间戳转换为字符串时间格式
        :return:
        """
        return time.strftime(self.datetime_format, time.localtime(self.update_timestamp))
    get_update_time.allow_tags = True
    get_update_time.short_description = u'更新时间'

    def soft_delete(self):
        """
        对象软删除，只更新删除标记 is_deleted 为 True
        :return: ObjectId
        """
        self.is_deleted = True
        self.save()
        return self.pk
