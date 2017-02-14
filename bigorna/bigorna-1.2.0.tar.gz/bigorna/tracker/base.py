from datetime import datetime
import threading

from sqlalchemy import Column, String, DateTime

from bigorna.commons.config import Config
from bigorna.commons.event_bus import bus, Event
from bigorna.tasks import TaskDefinition, Status, task_status_changed_evt
from bigorna.tracker.persistence import get_sessionmaker

from .persistence import Base


class Job(Base):
    __tablename__ = 'JOB'
    id = Column(String, primary_key=True)
    cmd = Column(String)
    status = Column(String, default=lambda: str(Status.PENDING))
    submitted_by = Column(String)
    submitted_at = Column(DateTime, default=datetime.now)
    last_update = Column(DateTime, onupdate=datetime.now)
    output_file = Column(String)

    @property
    def is_pending(self):
        return self.status == str(Status.PENDING)

    @property
    def is_running(self):
        return self.status == str(Status.RUNNING)

    @property
    def is_success(self):
        return self.status == str(Status.SUCCESS)

    @property
    def is_failed(self):
        return self.status == str(Status.FAILED)

    @property
    def output_stream(self):
        return open(self.output_file, 'r')

    def as_dict(self):
        return {'id': self.id,
                'cmd': self.cmd,
                'status': self.status,
                'submitted_by': self.submitted_by,
                'submitted_at': self.submitted_at,
                'last_update': self.last_update
                }


class JobDao:
    def __init__(self, cfg: Config):
        self._sessionmaker = get_sessionmaker(cfg)
        self.thread_data = threading.local()

    @property
    def session(self):
        if not hasattr(self.thread_data, 'session'):
            ss = self._sessionmaker()
            self.thread_data.session = ss

        return self.thread_data.session

    def save(self, job: Job):
        if job not in self.session.dirty:
            self.session.add(job)
        self.session.commit()

    def get(self, job_id) -> Job:
        return self.session.query(Job).filter_by(id=job_id).one_or_none()

    def get_all(self):
        return self.session.query(Job).order_by(Job.submitted_at.desc(),
                                                Job.last_update.desc()).all()

    def get_not_finished(self):
        return self.session.query(Job)\
            .filter(Job.status != str(Status.FAILED))\
            .filter(Job.status != str(Status.SUCCESS)).all()


class JobTracker:
    def __init__(self, cfg: Config):
        self.dao = JobDao(cfg)
        bus.register(self.__class__.__name__, self.task_updated)

    def create_job(self, task_def: TaskDefinition, submitter) -> Job:
        job = Job(id=task_def.id,
                  cmd=task_def.cmd,
                  submitted_by=submitter,
                  output_file=task_def.output_file)
        self.dao.save(job)
        return job

    def get_job(self, job_id):
        return self.dao.get(job_id)

    def list_jobs(self):
        return self.dao.get_all()

    def force_fail(self):
        jobs = self.dao.get_not_finished()
        count = len(jobs)
        for job in jobs:
            job.status = str(Status.FAILED)
            self.dao.save(job)
        return count

    def task_updated(self, evt: Event):
        if evt.evt_type != task_status_changed_evt:
            return  # guard

        task = evt.content

        job = self.dao.get(task.id)
        if job:
            job.status = str(task.status)
            self.dao.save(job)
