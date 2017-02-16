# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Original work Copyright 2015 Marc Sibson
# Modified work Copyright 2016 Ryler Hockenbury

from __future__ import absolute_import

from datetime import datetime, MINYEAR, timedelta
from math import ceil
import time

try:
    import simplejson as json
except ImportError:
    import json

from celery.beat import Scheduler, ScheduleEntry, DEFAULT_MAX_INTERVAL
from celery.utils.log import get_logger
from celery.utils.timeutils import humanize_seconds
from celery.app import app_or_default

from redis.exceptions import LockError
from redis.client import StrictRedis

from .decoders import MultiBeatJSONEncoder, MultiBeatJSONDecoder

NO_LOCK = 0
OLD_LOCK = 1
NEW_LOCK = 2

def add_defaults(app=None):
    app = app_or_default(app)

    ## TODO: do not allow user to specify some of these
    app.add_defaults({
        'MULTIBEAT_REDIS_URL': app.conf.get('MULTIBEAT_REDIS_URL', app.conf['BROKER_URL']),
        'MULTIBEAT_KEY_PREFIX': app.conf.get('MULTIBEAT_KEY_PREFIX', 'multibeat:'),
        'MULTIBEAT_SCHEDULE_KEY': app.conf.get('MULTIBEAT_KEY_PREFIX', 'multibeat:') + ':schedule',    #
        'MULTIBEAT_LOCK_KEY': app.conf.get('MULTIBEAT_KEY_PREFIX', 'multibeat:') + ':lock',            #
        'MULTIBEAT_LOCK_TIMEOUT': (app.conf.CELERYBEAT_MAX_LOOP_INTERVAL or DEFAULT_MAX_INTERVAL) * 2,
        'MULTIBEAT_COALESCE': app.conf.get('MULTIBEAT_COALESCE', False),
        'MULTIBEAT_GRACE_PERIOD': app.conf.get('MULTIBEAT_GRACE_PERIOD', 0)
    })


def redis(app=None):
    app = app_or_default(app)

    if not hasattr(app, 'multibeat_redis') or app.multibeat_redis is None:
        app.multibeat_redis = StrictRedis.from_url(app.conf.MULTIBEAT_REDIS_URL,
                                                 decode_responses=True)

    return app.multibeat_redis


ADD_ENTRY_ERROR = """\
Couldn't add entry %r to redis schedule: %r. Contents: %r
"""

logger = get_logger(__name__)


def to_timestamp(dt):
    return time.mktime(dt.timetuple())


def from_timestamp(ts):
    return datetime.fromtimestamp(ts)


class MultiBeatSchedulerEntry(ScheduleEntry):
    _meta = None

    def __init__(self, name=None, task=None, schedule=None, args=None, kwargs=None,
                 enabled=True, **clsargs):
        super(MultiBeatSchedulerEntry, self).__init__(name, task, schedule=schedule,
                                                    args=args, kwargs=kwargs, **clsargs)
        self.enabled = enabled

    @staticmethod
    def load_definition(key, app=None, definition=None):
        if definition is None:
            definition = redis(app).hget(key, 'definition')

        if not definition:
            raise KeyError(key)

        definition = MultiBeatSchedulerEntry.decode_definition(definition)

        return definition

    @staticmethod
    def decode_definition(definition):
        return json.loads(definition, cls=MultiBeatJSONDecoder)

    @staticmethod
    def load_meta(key, app=None):
        return MultiBeatSchedulerEntry.decode_meta(redis(app).hget(key, 'meta'))

    @staticmethod
    def decode_meta(meta, app=None):
        if not meta:
            return {'last_run_at': None}

        return json.loads(meta, cls=MultiBeatJSONDecoder)

    @classmethod
    def from_key(cls, key, app=None):
        with redis(app).pipeline() as pipe:
            pipe.hget(key, 'definition')
            pipe.hget(key, 'meta')
            definition, meta = pipe.execute()

        if not definition:
            raise KeyError(key)

        definition = cls.decode_definition(definition)
        meta = cls.decode_meta(meta)
        definition.update(meta)

        entry = cls(app=app, **definition)
        # celery.ScheduleEntry sets last_run_at = utcnow(), which is confusing and wrong
        entry.last_run_at = meta['last_run_at']

        return entry

    @property
    def due_at(self):
        # never run => due now
        if self.last_run_at is None:
            return self._default_now()

        delta = self.schedule.remaining_estimate(self.last_run_at)

        # overdue => due now
        if delta.total_seconds() < 0:
            return self._default_now()

        return self.last_run_at + delta

    @property
    def key(self):
        return app_or_default(self.app).conf['MULTIBEAT_KEY_PREFIX'] + self.name

    @property
    def score(self):
        return to_timestamp(self.due_at)

    @property
    def rank(self):
        return redis(self.app).zrank(self.app.conf.MULTIBEAT_SCHEDULE_KEY, self.key)

    def save(self):
        """
        Save a task definition in Redis
        """
        definition = {
            'name': self.name,
            'task': self.task,
            'args': self.args,
            'kwargs': self.kwargs,
            'options': self.options,
            'schedule': self.schedule,
            'enabled': self.enabled,
        }
        with redis(self.app).pipeline() as pipe:
            pipe.multi()
            pipe.hset(self.key, 'definition', json.dumps(definition, cls=MultiBeatJSONEncoder))
            pipe.zadd(self.app.conf.MULTIBEAT_SCHEDULE_KEY, self.score, self.key)
            pipe.execute()

        return self

    def delete(self):
        """
        Delete task definition from Redis
        """
        with redis(self.app).pipeline() as pipe:
            pipe.multi()
            pipe.zrem(self.app.conf.MULTIBEAT_SCHEDULE_KEY, self.key)
            pipe.delete(self.key)
            pipe.execute()

    def _next_instance(self, last_run_at=None, only_update_last_run_at=False):
        entry = super(MultiBeatSchedulerEntry, self)._next_instance(last_run_at=last_run_at)

        if only_update_last_run_at:
            ## Rollback the update to total_run_count
            entry.total_run_count = self.total_run_count

        meta = {
            'last_run_at': entry.last_run_at,
            'total_run_count': entry.total_run_count,
        }

        with redis(self.app).pipeline() as pipe:
            pipe.multi()
            pipe.hset(self.key, 'meta', json.dumps(meta, cls=MultiBeatJSONEncoder))
            pipe.zadd(self.app.conf.MULTIBEAT_SCHEDULE_KEY, entry.score, entry.key)
            pipe.execute()

        return entry

    __next__ = next = _next_instance

    def reschedule(self, last_run_at=None):
        self.last_run_at = last_run_at or self._default_now()
        meta = {
            'last_run_at': self.last_run_at,
        }
        with redis(self.app).pipeline() as pipe:
            pipe.multi()
            pipe.hset(self.key, 'meta', json.dumps(meta, cls=MultiBeatJSONEncoder))
            pipe.zadd(self.app.conf.MULTIBEAT_SCHEDULE_KEY, self.score, self.key)
            pipe.execute()

    def is_due(self):
        if not self.enabled:
            return False, 5.0  # 5 second delay for re-enable.

        return self.schedule.is_due(self.last_run_at or
                                    datetime(MINYEAR, 1, 1, tzinfo=self.schedule.tz))


class MultiBeatScheduler(Scheduler):
    Entry = MultiBeatSchedulerEntry

    def __init__(self, app, **kwargs):
        add_defaults(app)
        super(MultiBeatScheduler, self).__init__(app, **kwargs)

        self.lock_key = kwargs.pop('lock_key', app.conf.MULTIBEAT_LOCK_KEY)
        self.lock_timeout = kwargs.pop('lock_timeout', app.conf.MULTIBEAT_LOCK_TIMEOUT)
        self.lock_interval = ceil(self.lock_timeout / 10.0)
        self.original_interval = self.max_interval

        ## Beat may instantiate this scheduler multiple times, must be idempotent
        ## when 'lazy' argument is set so don't set up the locks until needed
        if 'lazy' not in kwargs or not kwargs['lazy']:
            self._lock = redis(app).lock(self.lock_key, timeout=self.lock_timeout)
            self._has_lock = False

    def setup_schedule(self):
        """
        Merge statically defined local CeleryBeat schedule to remote entry store

        Static schedules are merged each time a CeleryBeat instance starts, and
        a remote entry with the same name as a local entry will be replaced.
        Each static schedule should therefore only be defined once across all
        CeleryBeat instances, or ensure that any duplicate static schedules
        are the same.
        """
        logger.debug('Setting up schedule')
        self.install_default_entries(self.app.conf.CELERYBEAT_SCHEDULE)
        if self.app.conf.CELERYBEAT_SCHEDULE:
            self.update_from_dict(self.app.conf.CELERYBEAT_SCHEDULE)

    def update_from_dict(self, dict_):
        for name, entry in dict_.items():
            try:
                entry = self._maybe_entry(name, entry)
            except Exception as exc:
                logger.error(ADD_ENTRY_ERROR, name, exc, entry)
                continue

            entry.save()
            logger.info("Stored entry %s", entry)

    def reserve(self, entry):
        new_entry = next(entry)
        return new_entry

    @property
    def schedule(self):
        logger.debug('Selecting tasks')

        max_due_at = to_timestamp(self.app.now())
        client = redis(self.app)

        with client.pipeline() as pipe:
            pipe.multi()
            pipe.zrangebyscore(self.app.conf.MULTIBEAT_SCHEDULE_KEY, 0, max_due_at)

            ## Peek into the next tick to accurately calculate sleep between ticks
            pipe.zrangebyscore(self.app.conf.MULTIBEAT_SCHEDULE_KEY,
                               '({}'.format(max_due_at),
                               max_due_at + self.max_interval,
                               start=0, num=1)
            due_tasks, maybe_due = pipe.execute()

        logger.debug('Loading %d tasks', len(due_tasks) + len(maybe_due))
        d = {}
        for key in due_tasks + maybe_due:
            try:
                entry = self.Entry.from_key(key, app=self.app)
            except KeyError:
                logger.warning('failed to load %s, removing', key)
                client.zrem(self.app.conf.MULTIBEAT_SCHEDULE_KEY, key)
                continue

            d[entry.name] = entry

        logger.info('Processing tasks %s' % d)
        return d


    @property
    def get_lock(self):
        if self._has_lock:
            logger.debug('Already have old lock.')
            return OLD_LOCK
        else:
            logger.debug('Trying to acquire new lock...')
            self._has_lock = self._lock.acquire(blocking=False)
            if self._has_lock:
                logger.debug('New lock acquired')
                ## Resume predefined wake up interval once lock is acquired
                self.max_interval = self.original_interval
                return NEW_LOCK
            else:
                logger.debug('Unable to acquire new lock')
                ## Reset wake up interval to lower value to make this
                ## instance more "aggressive" in acquring lock
                self.max_interval = self.lock_interval
                return NO_LOCK

    def catch_up(self):
        """
        Cycle through missed scheduled events and run them to catch up due
        to new lockholder.
        """
        logger.debug('Catching up schedule')

        schedule = self.schedule
        now = self.app.now()
        interval_ts = now - timedelta(seconds=self.app.conf.MULTIBEAT_GRACE_PERIOD)

        ## Find the last run of a task, going back up to a grace period
        last_runs = [x.last_run_at for x in schedule.itervalues() if x.last_run_at is not None]
        last_run = max(last_runs + [interval_ts])

        intervals = []
        for entry in schedule.itervalues():
            interval = entry.is_due()[1]
            if interval:
                intervals.append(interval)
        interval = min(intervals + [self.max_interval])

        ## If the time difference between the latest run and the interval
        ## doesn't catch up to current time, the scheduler needs to play
        ## catch up before running normally.
        run_time = last_run + timedelta(seconds=interval)
        now = self.app.now()

        while run_time < now:
            intervals = []
            try:
                for entry in schedule.itervalues():
                    interval = self.maybe_due(entry, self.publisher)
                    if interval:
                        intervals.append(interval)
            except RuntimeError:
                pass

            interval = min(intervals + [self.max_interval])
            run_time += timedelta(seconds=interval)
            now = self.app.now()

            ## If coalescing is enabled, break out before running more missed
            ## schedule iterations
            if self.app.conf.MULTIBEAT_COALESCE:
                break

        return interval

    def tick(self, **kwargs):
        """
        Run a tick, that is one iteration of the scheduler.
        Executes all due tasks.
        """
        lock_status = self.get_lock
        if lock_status:
            logger.debug('Lock held. Running tick.')

            ## Since the system could have been down, we need to play catch
            ## starting from when the lock expired
            if lock_status == NEW_LOCK:
                return self.catch_up()
            else:
                return super(MultiBeatScheduler, self).tick(**kwargs)
        else:
            ## If we don't control the lock, sleep until the next interval and
            ## see if we get the lock.
            logger.debug('Lock not held. Sleeping for %s' % self.max_interval)
            return self.max_interval

    def close(self):
        if self._lock and self._has_lock:
            logger.debug('Releasing lock...')
            try:
                self._lock.release()
                self._lock = None
                self._has_lock = False
            except LockError:
                pass

        super(MultiBeatScheduler, self).close()

    @property
    def info(self):
        info = ['       . redis -> {}'.format(self.app.conf.MULTIBEAT_REDIS_URL)]
        if self.lock_key:
            info.append('       . lock -> `{}` {} ({}s)'.format(
                self.lock_key, humanize_seconds(self.lock_timeout), self.lock_timeout))
        return '\n'.join(info)
