"""
Nameko Logstash Dependency Provider
"""
import logging
import logstash

from nameko.extensions import DependencyProvider
from logging import FileHandler


class LogstashDependency(DependencyProvider):

    def __init__(self, local_file=None, log_formatter=None, *args, **kwargs):

        self.local_file = local_file
        if not log_formatter:
            log_formatter = ("%(asctime)s - %(name)s - "
                             "%(levelname)s - %(message)s")
        self.log_formatter = log_formatter

        super(DependencyProvider, self).__init__(*args, **kwargs)

    def setup(self):
        config = self.container.config.get('LOGSTASH', {})

        self.host = config.get('HOST')
        self.port = config.get('PORT', 5959)
        self.log_level = getattr(
            logging, config.get('LOG_LEVEL', 'INFO'))
        self.logger_by_service_name = dict()

    def get_dependency(self, *args, **kwargs):
        worker_ctx = args[0]
        service_name = worker_ctx.service_name
        if not self.logger_by_service_name.get(service_name):
            logger = logging.getLogger(service_name)
            self.logger_by_service_name[service_name] = logger
            logger.setLevel(self.log_level)

            formatter = logging.Formatter(self.log_formatter)
            handler = logstash.LogstashHandler(self.host, self.port, version=1)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            if self.local_file:
                file_handler = FileHandler(self.local_file)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)

        return self.logger_by_service_name[service_name]

