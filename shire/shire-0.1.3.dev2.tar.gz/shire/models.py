# -*- coding: utf-8 -*-
import datetime
import json
from importlib import import_module
# Отсутствует в python3
import imp
import os

import peewee


__all__ = ['db', 'Limit', 'JobEntry', 'Queue']


db = peewee.Proxy()


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Limit(BaseModel):
    ENTITY_POOL = 'pool'
    ENTITY_QUEUE = 'queue'
    ENTITY_CHOICES = ((ENTITY_POOL, u'Пул'), (ENTITY_QUEUE, u'Очередь'))

    entity_type = peewee.CharField(max_length=16, choices=ENTITY_CHOICES)
    entity = peewee.CharField(max_length=256)
    limit = peewee.IntegerField(default=1)

    class Meta:
        db_table = 'shire_limit'


class Queue(BaseModel):
    # TODO проверить использование - очереди у нас виртуальные и живут в неймспейсе пула, лимиты на них в Limit
    name = peewee.CharField(max_length=256)
    pool = peewee.CharField(max_length=128)

    class Meta:
        db_table = 'shire_queue'


class JobEntry(BaseModel):
    STATUS_NEW = 'new'
    STATUS_RESTART = 'restart'
    STATUS_ENQUEUED = 'enqueued'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_ENDED = 'ended'
    STATUS_CHOICES = (
        (STATUS_NEW, u'новая'),
        (STATUS_RESTART, u'на перезапуск'),
        (STATUS_ENQUEUED, u'в очереди'),
        (STATUS_IN_PROGRESS, u'выполняется'),
        (STATUS_ENDED, u'завершена'),
    )
    STATUS_DEFAULT = STATUS_NEW
    VALID_STATUSES = {k for k, v in STATUS_CHOICES}
    FUNC_CALL_PATH = 'path'
    FUNC_CALL_CLASS = 'class'
    FUNC_CALL_ARGS = 'args'
    FUNC_CALL_KWARGS = 'kwargs'
    HOST_DEFAULT = 'default'

    func_call_ = peewee.TextField(db_column='func_call')
    pool = peewee.CharField(max_length=256, index=True)
    queue = peewee.CharField(max_length=256)
    status = peewee.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_DEFAULT, index=True)
    host = peewee.CharField(max_length=256, default=HOST_DEFAULT, index=True)
    pool_uuid = peewee.CharField(max_length=64, null=True, index=True)
    worker_uuid = peewee.CharField(max_length=64, null=True)
    worker_pid = peewee.IntegerField(default=0, null=True)
    created_at = peewee.DateTimeField(default=datetime.datetime.now)
    updated_at = peewee.DateTimeField(default=None, null=True, index=True)
    ended_at = peewee.DateTimeField(default=None, null=True)

    class Meta:
        db_table = 'shire_job'

    @property
    def func_call(self):
        return json.loads(self.func_call_)

    @func_call.setter
    def func_call(self, value):
        self.func_call_ = json.dumps(value)

    @classmethod
    def create_job(cls, file_path, file_cls, pool, queue=None, status=None, host=None, args=None, kwargs=None):
        func_call = {
            cls.FUNC_CALL_PATH: file_path,
            cls.FUNC_CALL_CLASS: file_cls,
            cls.FUNC_CALL_ARGS: () if args is None else args,
            cls.FUNC_CALL_KWARGS: {} if kwargs is None else kwargs
        }
        status = status if status in cls.VALID_STATUSES else cls.STATUS_DEFAULT
        host = cls.HOST_DEFAULT if host is None else host
        job = cls(pool=pool, queue=queue, status=status, host=host)
        job.func_call = func_call
        return job

    @property
    def job_cls(self):
        # TODO: Если потребуется поддержка python3, то этот код необходимо будет расширить
        module_path = self.func_call[self.FUNC_CALL_PATH]
        if module_path.endswith('.pyc'):
            module_path = module_path[:-1]
        module_name = 'shire.fake_module{}'.format(module_path.rsplit('_', 1)[0].replace(os.path.sep, '_'))
        fake_module = imp.load_source(module_name, module_path)
        return getattr(fake_module, self.func_call[self.FUNC_CALL_CLASS])

    def get_params(self):
        # параметры для конкретной задачи
        args, kwargs = [], {}
        if self.FUNC_CALL_ARGS in self.func_call:
            args = self.func_call[self.FUNC_CALL_ARGS]
            if not isinstance(args, list):
                raise Exception('func_call args {} must be list!'.format(args))
        if self.FUNC_CALL_KWARGS in self.func_call:
            kwargs = self.func_call[self.FUNC_CALL_KWARGS]
            if not isinstance(kwargs, dict):
                raise Exception('func_call kwargs {} must be dict!'.format(kwargs))
        return args, kwargs

    def set_status(self, status):
        self.status = status
        self.save(only=[JobEntry.status])

    def save(self, force_insert=False, only=None):
        if 'updated_at' not in self._dirty:
            if only is not None and self.__class__.updated_at not in only:
                only = [x for x in only] + [self.__class__.updated_at]
            self.updated_at = datetime.datetime.now()
        return super(self.__class__, self).save(force_insert=force_insert, only=only)
