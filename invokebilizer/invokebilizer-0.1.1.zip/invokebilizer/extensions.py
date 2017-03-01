from invoke.exceptions import Failure


class TaskListResult(object):
    def __init__(self):
        self.stderr = ''
        self.stdout = ''
        self.exited = 0
        self.pty = False
        self.failed = False
        self.failed_tasks = []

    def add_task_result(self, _task, task_result):
        if task_result is None:
            return

        if task_result.failed:
            self.failed_tasks.append((_task, task_result))
            self.exited = task_result.exited
            self.failed = True

        self.pty = task_result.pty
        self.stderr += task_result.stderr
        self.stdout += task_result.stdout


def run_all(ctx, *tasks):
    result = TaskListResult()
    for _task in tasks:
        try:
            task_result = _task(ctx)
        except Failure as f:
            task_result = f.result

        result.add_task_result(_task, task_result)

    if result.failed:
        def format_task(t):
            name = t[0].name
            _sub_tasks = map(format_task, t[1].failed_tasks) if isinstance(t[1], TaskListResult) else None
            return "%s (%s)" % (name, ', '.join(_sub_tasks)) if _sub_tasks else name

        print('FAILED TASKS: %s' % (', '.join(map(format_task, result.failed_tasks))))
        raise Failure(result)
    return result
