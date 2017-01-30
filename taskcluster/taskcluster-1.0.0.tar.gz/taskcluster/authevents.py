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


class AuthEvents(BaseClient):
    """
    The auth service, typically available at `auth.taskcluster.net`
    is responsible for storing credentials, managing assignment of scopes,
    and validation of request signatures from other services.

    These exchanges provides notifications when credentials or roles are
    updated. This is mostly so that multiple instances of the auth service
    can purge their caches and synchronize state. But you are of course
    welcome to use these for other purposes, monitoring changes for example.
    """

    classOptions = {
        "exchangePrefix": "exchange/taskcluster-auth/v1/"
    }

    """
    Client Created Messages

    Message that a new client has been created.

    This exchange outputs: ``http://schemas.taskcluster.net/auth/v1/client-message.json#``This exchange takes the following keys:

     * reserved: Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.
    """

    def clientCreated(self, *args, **kwargs):
        return self._makeTopicExchange({'schema': 'http://schemas.taskcluster.net/auth/v1/client-message.json#', 'routingKey': [{'multipleWords': True, 'summary': 'Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.', 'name': 'reserved', 'required': False}], 'exchange': 'client-created', 'name': 'clientCreated'}, *args, **kwargs)

    """
    Client Updated Messages

    Message that a new client has been updated.

    This exchange outputs: ``http://schemas.taskcluster.net/auth/v1/client-message.json#``This exchange takes the following keys:

     * reserved: Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.
    """

    def clientUpdated(self, *args, **kwargs):
        return self._makeTopicExchange({'schema': 'http://schemas.taskcluster.net/auth/v1/client-message.json#', 'routingKey': [{'multipleWords': True, 'summary': 'Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.', 'name': 'reserved', 'required': False}], 'exchange': 'client-updated', 'name': 'clientUpdated'}, *args, **kwargs)

    """
    Client Deleted Messages

    Message that a new client has been deleted.

    This exchange outputs: ``http://schemas.taskcluster.net/auth/v1/client-message.json#``This exchange takes the following keys:

     * reserved: Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.
    """

    def clientDeleted(self, *args, **kwargs):
        return self._makeTopicExchange({'schema': 'http://schemas.taskcluster.net/auth/v1/client-message.json#', 'routingKey': [{'multipleWords': True, 'summary': 'Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.', 'name': 'reserved', 'required': False}], 'exchange': 'client-deleted', 'name': 'clientDeleted'}, *args, **kwargs)

    """
    Role Created Messages

    Message that a new role has been created.

    This exchange outputs: ``http://schemas.taskcluster.net/auth/v1/role-message.json#``This exchange takes the following keys:

     * reserved: Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.
    """

    def roleCreated(self, *args, **kwargs):
        return self._makeTopicExchange({'schema': 'http://schemas.taskcluster.net/auth/v1/role-message.json#', 'routingKey': [{'multipleWords': True, 'summary': 'Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.', 'name': 'reserved', 'required': False}], 'exchange': 'role-created', 'name': 'roleCreated'}, *args, **kwargs)

    """
    Role Updated Messages

    Message that a new role has been updated.

    This exchange outputs: ``http://schemas.taskcluster.net/auth/v1/role-message.json#``This exchange takes the following keys:

     * reserved: Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.
    """

    def roleUpdated(self, *args, **kwargs):
        return self._makeTopicExchange({'schema': 'http://schemas.taskcluster.net/auth/v1/role-message.json#', 'routingKey': [{'multipleWords': True, 'summary': 'Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.', 'name': 'reserved', 'required': False}], 'exchange': 'role-updated', 'name': 'roleUpdated'}, *args, **kwargs)

    """
    Role Deleted Messages

    Message that a new role has been deleted.

    This exchange outputs: ``http://schemas.taskcluster.net/auth/v1/role-message.json#``This exchange takes the following keys:

     * reserved: Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.
    """

    def roleDeleted(self, *args, **kwargs):
        return self._makeTopicExchange({'schema': 'http://schemas.taskcluster.net/auth/v1/role-message.json#', 'routingKey': [{'multipleWords': True, 'summary': 'Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.', 'name': 'reserved', 'required': False}], 'exchange': 'role-deleted', 'name': 'roleDeleted'}, *args, **kwargs)

    funcinfo = {
    }


__all__ = ['createTemporaryCredentials', 'config', '_defaultConfig', 'createApiClient', 'createSession', 'AuthEvents']
