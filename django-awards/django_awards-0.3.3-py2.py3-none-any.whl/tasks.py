from celery.task import Task

from ..notifications.contextmanagers import BatchNotifications


class AsyncBadgeAward(Task):
    ignore_result = True

    def run(self, badge, state, **kwargs):
        # from celery.contrib import rdb; rdb.set_trace()
        with BatchNotifications():
            badge.actually_possibly_award(**state)
