# -*- coding: utf-8 -*-
import logging
import os
import sys

import datetime

import six

from shire.const import SHIRE_WORKHORSE_PROCESS_NAME


__all__ = [
    'to_list', 'check_pid_is_shire', 'capture_output', 'cleanup_old_jobs', 'execute_job', 'create_console_handler'
]


def create_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger


def create_console_handler(logger, fmt='[ %(asctime)s | %(name)s ] - <%(levelname)s> - %(message)s'):
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(logging.Formatter(fmt))
    logger.addHandler(console)


def to_list(value, default=None):
    if value is None:
        return default if default else []
    if isinstance(value, six.string_types):
        return value.split(',')
    if isinstance(value, (list, tuple)):
        return map(str, value)
    return [str(value), ]


def check_pid_is_shire(pid):
    # Проверяет, что процесс жив и процесс - это shire workhorse
    proc = '/proc/{}/cmdline'.format(pid)
    if os.path.exists(proc):
        with open(proc, 'rb') as f:
            return f.read().startswith(SHIRE_WORKHORSE_PROCESS_NAME)
    return False


class capture_output(object):
    def __init__(self, stdout=None, stderr=None):
        self._stdout = stdout or sys.stdout
        self._stderr = stderr or sys.stderr

    def __enter__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stdout.flush()
        self.old_stderr.flush()
        sys.stdout, sys.stderr = self._stdout, self._stderr

    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush()
        self._stderr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr


def cleanup_old_jobs(days_ago=7):
    from shire.models import JobEntry
    days_ago = datetime.date.today() - datetime.timedelta(days=days_ago)
    query = JobEntry.delete().where(~(JobEntry.updated_at >> None) & (JobEntry.updated_at < days_ago))
    return query.execute()


def execute_job(job_id, config):
    from shire.models import JobEntry
    from shire.job import Job
    job_entry = JobEntry.select().where(JobEntry.id == job_id).first()
    if job_entry is None:
        return False
    args, kwargs = job_entry.get_params()
    # Подготавливаем job_entry к inline-запуску
    job_entry.pool = 'dummy_pool'
    job_entry.queue = 'dummy_queue'
    job_entry.host = 'dummy_host'
    job_entry.status = JobEntry.STATUS_ENQUEUED
    job_entry.save()
    result = Job.execute(config, args=args, kwargs=kwargs, job_entry=job_entry)
    return result.status == JobEntry.STATUS_ENDED


def decode_if_not_empty(value):
    if isinstance(value, six.binary_type):
        return value.decode()
    return value