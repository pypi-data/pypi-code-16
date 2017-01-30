# coding=utf-8
#####################################################
# THIS FILE IS AUTOMATICALLY GENERATED. DO NOT EDIT #
#####################################################
# noqa: E128,E201
from .client import BaseClient
from .client import createApiClient
from .client import config
from .client import createTemporaryCredentials
from .client import createSession
_defaultConfig = config


class Github(BaseClient):
    """
    The github service, typically available at
    `github.taskcluster.net`, is responsible for publishing pulse
    messages in response to GitHub events.

    This document describes the API end-point for consuming GitHub
    web hooks
    """

    classOptions = {
        "baseUrl": "https://github.taskcluster.net/v1"
    }

    def githubWebHookConsumer(self, *args, **kwargs):
        """
        Consume GitHub WebHook

        Capture a GitHub event and publish it via pulse, if it's a push,
        release or pull request.

        This method is ``experimental``
        """

        return self._makeApiCall(self.funcinfo["githubWebHookConsumer"], *args, **kwargs)

    def builds(self, *args, **kwargs):
        """
        List of Builds

        A paginated list of builds that have been run in
        Taskcluster. Can be filtered on various git-specific
        fields.

        This method takes output: ``http://schemas.taskcluster.net/github/v1/build-list.json#``

        This method is ``experimental``
        """

        return self._makeApiCall(self.funcinfo["builds"], *args, **kwargs)

    def ping(self, *args, **kwargs):
        """
        Ping Server

        Respond without doing anything.
        This endpoint is used to check that the service is up.

        This method is ``stable``
        """

        return self._makeApiCall(self.funcinfo["ping"], *args, **kwargs)

    funcinfo = {
        "githubWebHookConsumer": {           'args': [],
            'method': 'post',
            'name': 'githubWebHookConsumer',
            'route': '/github',
            'stability': 'experimental'},
        "builds": {           'args': [],
            'method': 'get',
            'name': 'builds',
            'output': 'http://schemas.taskcluster.net/github/v1/build-list.json#',
            'query': [           'continuationToken',
                                 'limit',
                                 'organization',
                                 'repository',
                                 'sha'],
            'route': '/builds',
            'stability': 'experimental'},
        "ping": {           'args': [],
            'method': 'get',
            'name': 'ping',
            'route': '/ping',
            'stability': 'stable'},
    }


__all__ = ['createTemporaryCredentials', 'config', '_defaultConfig', 'createApiClient', 'createSession', 'Github']
