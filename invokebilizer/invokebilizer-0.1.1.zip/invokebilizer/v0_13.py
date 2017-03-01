from invoke import task as _invoke_task
from invoke import __version_info__ as _invoke__version_info__
from .extensions import run_all

__all__ = ['run_all', 'task']

if _invoke__version_info__[0] == 0:
    if _invoke__version_info__[1] >= 13:
        task = _invoke_task
    else:
        def task(*args, **kwargs):
            new_kwargs = {'contextualized': True}
            new_kwargs.update(kwargs)
            return _invoke_task(*args, **new_kwargs)
