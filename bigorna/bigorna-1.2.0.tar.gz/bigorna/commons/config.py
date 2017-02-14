import yaml
import os
import logging


class Config:
    DB_FILE = "db_file"

    _REQUIRED = ('db_file',)

    def __init__(self, file='config.yml'):
        self._load_file(file)
        self._update_from_env()
        self._validate()

    def _load_file(self, file):
        with open(file, 'r') as stream:
            self._cfg = yaml.load(stream)

    def _update_from_env(self):
        if Config.DB_FILE in os.environ:
            self._cfg[Config.DB_FILE] = os.environ.get(Config.DB_FILE)

    def _validate(self):
        for key in Config._REQUIRED:
            if key not in self._cfg:
                raise KeyError("Config %s not defined" % key)

    @property
    def db_file(self):
        return self._cfg[Config.DB_FILE]

    @property
    def output_pattern(self):
        return self._cfg.get('output_pattern')

    @property
    def tasks(self):
        return self._cfg.get('tasks', [])

    @property
    def concurrent_tasks(self):
        return self._cfg.get('concurrent_tasks', 1)

    @property
    def task_check_delay(self):
        return self._cfg.get('task_check_interval', 10)

    @property
    def http_port(self):
        return self._cfg.get('http_port', 5555)

    @property
    def schedule(self):
        return self._cfg.get('schedule', [])


def setup_logging(log_file):
    log = '%(asctime)s [%(levelname)s] %(module)s:%(lineno)d %(message)s'
    date = '%Y-%m-%dT%H:%M:%S'
    level = logging.INFO

    logging.basicConfig(filename=log_file, level=level, format=log, datefmt=date)
