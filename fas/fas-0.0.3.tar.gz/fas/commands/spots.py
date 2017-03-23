import logging

from ..utils import WaitCompletion
from .command import Command
logger = logging.getLogger(__name__)


class Spots(Command):
    def __init__(self, *args, **kwargs):
        self._logger = logger
        super(Spots, self).__init__(*args, **kwargs)

    def list(self):
        logger.debug('Going to list spots..')
        uri = 'spots/'
        all = self.api.get(uri=uri)
        return all

    def get(self, ip):
        uri = 'spots/{0}'.format(ip)
        response = self.api.get(uri=uri)
        return response

    @WaitCompletion(logger=logger)
    def create(self, wait):
        logger.debug('Going to create a spot, wait={0}'.format(wait))
        uri = 'spots/'
        task_id = self.api.put(uri=uri)
        return "Execution id: {0}".format(task_id)

    @WaitCompletion(logger=logger)
    def delete(self, ip, force_delete, wait):
        logger.debug('Going to delete a spot, wait={0}'.format(wait))
        ip = ip if ip else ''
        uri = 'spots/{0}'.format(ip)
        task_id = self.api.delete(uri=uri)
        return "Execution id: {0}".format(task_id)
