"""
Nameko Logstash Dependency Provider
"""
from nameko.extensions import DependencyProvider
import logging
import logstash


class LogstashDependency(DependencyProvider):

    def setup(self):
        config = self.container.config.get('LOGSTASH', {})

        self.host = config.get('HOST')
        self.port = config.get('PORT', 5959)
        self.log_level = getattr(
            logging, config.get('LOG_LEVEL', 'INFO'))

    def get_dependency(self, *args, **kwargs):
        worker_ctx = args[0]
        logger = logging.getLogger(worker_ctx.service_name)
        logger.setLevel(self.log_level)
        logger.addHandler(
            logstash.LogstashHandler(self.host, self.port, version=1))
        return logger

