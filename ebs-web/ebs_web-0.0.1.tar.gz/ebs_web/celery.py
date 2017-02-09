# coding=utf-8

from celery import Celery


def create_celery_app(app):
    """ Create a celery app instance."""
    celery = Celery(app.import_name, broker=app.config[u'CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        """Add flask context to the celery tasks created.
        """
        abstract = True

        def __call__(self, *args, **kwargs):
            """Return Task within a Flask app context.
            Returns:
                A Task (instance of Celery.celery.Task)
            """
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    celery.app = app
    return celery
