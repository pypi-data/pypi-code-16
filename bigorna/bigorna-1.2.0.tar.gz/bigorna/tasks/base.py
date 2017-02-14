from enum import Enum
from uuid import uuid4

from bigorna.commons import Config


task_status_changed_evt = "TaskStatusChanged"


class TaskDefinition:
    def __init__(self, cmd, cwd, output_file_pattern=None):
        assert cmd is not None, "'cmd' can't be None"
        self.id = str(uuid4())
        self.cmd = cmd
        self.base_dir = cwd
        self.output_file = output_file_pattern % self.id if output_file_pattern else None


class Status(Enum):
    PENDING = 1
    RUNNING = 2
    FAILED = 3
    SUCCESS = 4


class TaskFactory:
    def __init__(self, cfg: Config):
        self._tasks = dict(map(lambda x: (x['name'], x), cfg.tasks))

    def create_task_definition(self, task_type, cmd_params, output_file=None) -> TaskDefinition:
        task_cfg = self._tasks[task_type]
        cmd = task_cfg['cmd'].format(**cmd_params)
        return TaskDefinition(cmd, task_cfg.get('base_dir'), output_file)
