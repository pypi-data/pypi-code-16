from inspect import isfunction
from pipeliner.register import Register
from pipeliner.context import Context
from pipeliner.exceptions import TaskDependencyError, PipelineIsNotRunning
from .backend import GeventBackend


class Pipeline(object):
    def __init__(self, *tasks, **kwargs):
        self._providers = {}
        self._backend = GeventBackend()

        self._context = Context(current_pipeline=self, **kwargs)

        self._check_tasks(*tasks)

        self._is_running = False
        self._is_finished = False

    def _check_tasks(self, *tasks):
        for task in tasks:
            if not isfunction(task):
                raise ValueError("Task must be a function")
            if not self._is_applied(task):
                raise ValueError(
                    "Task must be applied before adding to pipeline")

            depends = self._get_depends(task)
            for dep in depends:
                if not self._is_dependency_satisfied(dep):
                    raise TaskDependencyError("Dependency `{}` of task `{}` " \
                        "is not satisfied".format(dep, task.__name__))

            provides = self._get_provides(task)
            for prov in provides:
                self._add_provider(prov, task)

        self._tasks = list(tasks)

    def _is_applied(self, task):
        return hasattr(task, '_applied')

    def _get_depends(self, task):
        return Register().get_depends(task.__name__)

    def _get_provides(self, task):
        return Register().get_provides(task.__name__)

    def _add_provider(self, dependency, task):
        self._providers[dependency] = task

    def _is_dependency_satisfied(self, dependency):
        return (dependency in self._providers) or (dependency in self._context)

    def run(self, wait=False):
        self._is_running = True
        try:
            self._backend.run(self._run_tasks)
            if wait:
                self.wait_until_complete()
        finally:
            self._is_running = False
            self._is_finished = True

    def _run_tasks(self):
        for task in self._tasks:
            self._context = task(self._context)

    def wait_until_complete(self):
        self._backend.wait_until_complete()

    def wait_for(self, pipelines):
        threads = []
        for pipe in pipelines:
            if not pipe._is_running and not pipe._is_finished:
                raise PipelineIsNotRunning()

            threads.append(pipe._backend.current_thread)

        self._backend.wait_for(threads)

    @property
    def tasks(self):
        return self._tasks
