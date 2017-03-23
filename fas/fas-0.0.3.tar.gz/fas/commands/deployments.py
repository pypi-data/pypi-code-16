import os
import urllib
import logging
import pkg_resources

from ..utils import WaitCompletion
from .command import Command

logger = logging.getLogger(__name__)


class Deployments(Command):
    def __init__(self, *args, **kwargs):
        super(Deployments, self).__init__(*args, **kwargs)

    def list(self, all=False):
        uri = 'deployments/'
        all = self.api.get(uri=uri)
        return all

    @WaitCompletion(logger=logger)
    def create(self, name, file, wait):
        logger.debug('Going to create deployment: {0}'.format(name))
        uri = 'deployments/'
        query_params = None
        encoded_file_data = urllib.quote(file.read().encode("utf-8"))
        data = {"code": encoded_file_data,
                "requirements": "",
                "name": name}
        task_id = self.api.put(uri, params=query_params, data=data, expected_status_code=200)
        return "Execution id: {0}".format(task_id)

    def update(self, name, file, new_name):
        logger.debug('Going to update deployment: {0}'.format(name))
        if not (file or new_name):
            return 'No action requested, add --file or --new-name'

        uri = 'deployments/{0}'.format(name)
        query_params = None
        encoded_file_data = urllib.quote(file.read().encode("utf-8")) if file else None
        data = {"requirements": ""}
        if encoded_file_data:
            data['code'] = encoded_file_data
        if new_name:
            data['name'] = new_name
        response = self.api.post(uri, params=query_params, data=data, expected_status_code=200)
        return response

    def get(self, name):
        logger.debug('Going to retrieve deployment: {0}'.format(name))
        uri = 'deployments/{0}'.format(name)
        response = self.api.get(uri=uri)
        return response

    def delete(self, name, force):
        logger.debug('Going to delete deployment: {0}'.format(name))
        uri = 'deployments/{0}'.format(name)
        response = self.api.delete(uri=uri)
        return response

    @WaitCompletion(logger=logger)
    def run(self, name, parameters, wait):
        logger.debug('Goring to run {0} `with` parameter: {1}'.format(name, parameters))
        uri = 'deployments/{0}/rpc/'.format(name)
        if isinstance(parameters, dict):
            data = parameters
        elif isinstance(parameters, basestring):
            data = {p.split('=')[0]: p.split('=')[1] for p in parameters}
        else:
            data = None
        task_id = self.api.post(uri=uri,
                                data=data)
        return "Execution id: {0}".format(task_id)

    def samples(self, hello, fib):
        if not (hello or fib):
            return 'No action requested, add --hello or --fib'

        name = 'hello.py' if hello else 'fib.py'
        if os.path.isfile(name):
            return 'File with name `{0}` already exists.'.format(name)
        logger.debug('Going to create a sample file: `{0}`'.format(name))
        resource_package = __name__
        sample_file_name = 'fib.py' if fib else 'hello.py'
        resource_path = '/'.join(('samples', sample_file_name))
        sample = pkg_resources.resource_stream(resource_package, resource_path)
        content = sample.read()
        with open(name, 'w') as sample_file:
            sample_file.write(content)
        return "Sample file `{0}` been created.".format(sample_file_name)

