# -*- coding: utf-8 -*-
import setproctitle

import six
import os
import uuid
import sys

import datetime
import warnings

from shire.const import SHIRE_WORKHORSE_PROCESS_NAME
from shire.exceptions import RestartJobException
from shire.models import JobEntry, db
from shire.utils import capture_output


__all__ = ['Workhorse', 'WorkhorseStatusContext']


class WorkhorseStatusContext(object):

    def __init__(self, workhorse):
        self.workhorse = workhorse

    def __enter__(self):
        job_entry = self.workhorse.job_entry
        job_entry.pool_uuid = self.workhorse.pool.uuid
        job_entry.worker_uuid = self.workhorse.uuid
        job_entry.worker_pid = self.workhorse.pid
        job_entry.status = JobEntry.STATUS_IN_PROGRESS
        job_entry.save(only=[JobEntry.status, JobEntry.worker_uuid, JobEntry.worker_pid, JobEntry.pool_uuid])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        job_entry = self.workhorse.job_entry
        job_entry.status = JobEntry.STATUS_RESTART if exc_type == RestartJobException else JobEntry.STATUS_ENDED
        job_entry.updated_at = datetime.datetime.now()
        job_entry.save(only=[JobEntry.updated_at, JobEntry.status])


class Daemon(object):

    def __init__(self):
        self._uuid = None
        self._pid = None

    @property
    def uuid(self):
        if not self._uuid:
            self._uuid = str(uuid.uuid4())
        return self._uuid

    @property
    def pid(self):
        if not self._pid:
            self._pid = os.getpid()
        return self._pid


class Workhorse(Daemon):

    def __init__(self, pool, job_id):
        super(Workhorse, self).__init__()
        self.pool = pool
        self.config = pool.config
        self.log = pool.log
        self.job_id = job_id
        self.job_entry = None

    @property
    def project_dir(self):
        project_dir = self.config.get(self.config.SHIRE_SECTION, {}).get(
            self.config.SHIRE_PROJECT_DIR, self.config.SHIRE_PROJECT_DIR_DEFAULT
        )
        if not project_dir:
            return None

        return os.path.abspath(project_dir)

    def fork(self):
        pid = os.fork()
        if pid:
            return pid
        # унаследовали signal.signal(signal.SIGTERM, pool.terminate)
        # надо сказать инстансу пула, что мы теперь - workhorse
        self.pool.i_am_pool = False
        setproctitle.setproctitle('{} job_id={}'.format(SHIRE_WORKHORSE_PROCESS_NAME, self.job_id) + ' ' * 128)
        # отдельное соединение для потомка
        db.initialize(self.config.get_db())
        try:
            self.run()
        except Exception as exc:
            self.log.exception('In job #{} with workhorse uuid {} (pool {}/{})'.format(
                self.job_id, self.uuid, self.pool.name, self.pool.uuid))
            sys.exit(1)
        else:
            sys.exit(0)
        finally:
            db.close()

    def run(self):
        self.job_entry = self._load_from_db()
        if self.project_dir and self.project_dir not in sys.path:
            sys.path.insert(0, self.project_dir)

        stream = six.StringIO()
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            with capture_output(stream, stream):
                job = self.job_entry.job_cls(workhorse=self)
                args, kwargs = self.job_entry.get_params()
                try:
                    with WorkhorseStatusContext(workhorse=self):
                        job.run(*args, **kwargs)
                except RestartJobException:
                    pass  # обработано в shire.workhorse.WorkhorseStatusContext#__exit__
        output = stream.getvalue() or None
        if output is not None:
            try:
                self.log.info(u'Got output for job #{}: \n{}'.format(self.job_id, output))
            except UnicodeDecodeError:
                pass

    def _load_from_db(self):
        job_entry = JobEntry.get(JobEntry.id == self.job_id)
        return job_entry
