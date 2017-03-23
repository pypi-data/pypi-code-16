import urllib
import logging

from ..utils import WaitCompletion
from .command import Command

logger = logging.getLogger(__name__)


class Executions(Command):
    def __init__(self, *args, **kwargs):
        super(Executions, self).__init__(*args, **kwargs)

    def list(self, all, deployment):
        logger.debug('Going to retrieve all execution, include completed: `{0}`'.format(all))
        uri = 'executions/'
        executions = self.api.get(uri=uri,
                                  params={'deployment': deployment})
        return executions

    @WaitCompletion(logger=logger)
    def get(self, uuid, wait):
        logger.debug('Going to retrieve status of execution: `{0}`'.format(uuid))
        uri = 'executions/{0}'.format(uuid)
        execution = self.api.get(uri=uri)
        return execution

    def cancel(self, uuid):
        logger.debug('Going to cancel execution: `{0}`'.format(uuid))
        uri = 'executions/{0}'.format(uuid)
        response = self.api.delete(uri=uri)
        return response