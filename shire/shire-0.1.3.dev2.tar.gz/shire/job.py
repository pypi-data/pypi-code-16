# -*- coding: utf-8 -*-
import datetime
import sys

from shire.exceptions import RestartJobException
from shire.models import JobEntry
from shire.pool import Pool
from shire.workhorse import Workhorse


__all__ = ['Job', 'RestartJobException']


class DummyWorkhorse(Workhorse):
    def __init__(self, config):
        pool = Pool(config, 'dummy_pool')
        super(DummyWorkhorse, self).__init__(pool=pool, job_id=None)


def start_job(config, **kwargs):
    with config.with_db():
        job_entry = JobEntry.create_job(**kwargs)
        job_entry.save()
        return job_entry


class Job(object):

    @classmethod
    def delay(cls, config, pool, queue=None, args=(), kwargs=None):
        kwargs = {} if kwargs is None else kwargs
        queue = pool if queue is None else queue
        job_entry = start_job(
            config, pool=pool, queue=queue, file_path=sys.modules[cls.__module__].__file__, file_cls=cls.__name__,
            args=args, kwargs=kwargs
        )
        return job_entry

    @classmethod
    def execute(cls, config, args=(), kwargs=None, job_entry=None):
        # Немедленный вызов задачи на выполнение, минуя whip
        kwargs = {} if kwargs is None else kwargs
        job_entry = start_job(
            config, pool='dummy_pool', queue='dummy_queue', file_path=sys.modules[cls.__module__].__file__,
            file_cls=cls.__name__, args=args, kwargs=kwargs, status=JobEntry.STATUS_ENQUEUED, host='dummy_host'
        ) if job_entry is None else job_entry
        # Т.к. execute однопоточный, то повторять выполнение мы должны прямо здесь.
        # Чтобы не достигнуть maximum recursion depth exceeded раскрываем в while
        while True:
            try:
                job_entry.job_cls(DummyWorkhorse(config)).run(*args, **kwargs)
            except RestartJobException:
                continue
            else:
                break
        return job_entry

    def __init__(self, workhorse):
        self.workhorse = workhorse

    @property
    def log(self):
        return self.workhorse.log

    @property
    def config(self):
        return self.workhorse.config

    @property
    def job_entry(self):
        return self.workhorse.job_entry

    def tick(self):
        # Обновляет информацию о последнем обновлении задачи в базу данных
        self.job_entry.updated_at = datetime.datetime.now()
        self.job_entry.save(only=[JobEntry.updated_at])

    def dump_shelve(self, label, data):
        # Реализовать сохранение shelve в соответствии с настройкой в config
        pass

    def run(self, *args, **kwargs):
        raise NotImplementedError()

    def restart(self):
        raise RestartJobException()
