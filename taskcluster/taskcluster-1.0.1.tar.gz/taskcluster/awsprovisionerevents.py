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


class AwsProvisionerEvents(BaseClient):
    """
    Exchanges from the provisioner... more docs later
    """

    classOptions = {
        "exchangePrefix": "exchange/taskcluster-aws-provisioner/v1/"
    }

    """
    WorkerType Created Message

    When a new `workerType` is created a message will be published to this
    exchange.

    This exchange outputs: ``http://schemas.taskcluster.net/aws-provisioner/v1/worker-type-message.json#``This exchange takes the following keys:

     * routingKeyKind: Identifier for the routing-key kind. This is always `'primary'` for the formalized routing key. (required)

     * workerType: WorkerType that this message concerns. (required)

     * reserved: Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.
    """

    def workerTypeCreated(self, *args, **kwargs):
        return self._makeTopicExchange({'name': 'workerTypeCreated', 'routingKey': [{'multipleWords': False, 'name': 'routingKeyKind', 'required': True, 'summary': "Identifier for the routing-key kind. This is always `'primary'` for the formalized routing key.", 'constant': 'primary'}, {'multipleWords': False, 'name': 'workerType', 'required': True, 'summary': 'WorkerType that this message concerns.'}, {'multipleWords': True, 'name': 'reserved', 'required': False, 'summary': 'Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.'}], 'exchange': 'worker-type-created', 'schema': 'http://schemas.taskcluster.net/aws-provisioner/v1/worker-type-message.json#'}, *args, **kwargs)

    """
    WorkerType Updated Message

    When a `workerType` is updated a message will be published to this
    exchange.

    This exchange outputs: ``http://schemas.taskcluster.net/aws-provisioner/v1/worker-type-message.json#``This exchange takes the following keys:

     * routingKeyKind: Identifier for the routing-key kind. This is always `'primary'` for the formalized routing key. (required)

     * workerType: WorkerType that this message concerns. (required)

     * reserved: Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.
    """

    def workerTypeUpdated(self, *args, **kwargs):
        return self._makeTopicExchange({'name': 'workerTypeUpdated', 'routingKey': [{'multipleWords': False, 'name': 'routingKeyKind', 'required': True, 'summary': "Identifier for the routing-key kind. This is always `'primary'` for the formalized routing key.", 'constant': 'primary'}, {'multipleWords': False, 'name': 'workerType', 'required': True, 'summary': 'WorkerType that this message concerns.'}, {'multipleWords': True, 'name': 'reserved', 'required': False, 'summary': 'Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.'}], 'exchange': 'worker-type-updated', 'schema': 'http://schemas.taskcluster.net/aws-provisioner/v1/worker-type-message.json#'}, *args, **kwargs)

    """
    WorkerType Removed Message

    When a `workerType` is removed a message will be published to this
    exchange.

    This exchange outputs: ``http://schemas.taskcluster.net/aws-provisioner/v1/worker-type-message.json#``This exchange takes the following keys:

     * routingKeyKind: Identifier for the routing-key kind. This is always `'primary'` for the formalized routing key. (required)

     * workerType: WorkerType that this message concerns. (required)

     * reserved: Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.
    """

    def workerTypeRemoved(self, *args, **kwargs):
        return self._makeTopicExchange({'name': 'workerTypeRemoved', 'routingKey': [{'multipleWords': False, 'name': 'routingKeyKind', 'required': True, 'summary': "Identifier for the routing-key kind. This is always `'primary'` for the formalized routing key.", 'constant': 'primary'}, {'multipleWords': False, 'name': 'workerType', 'required': True, 'summary': 'WorkerType that this message concerns.'}, {'multipleWords': True, 'name': 'reserved', 'required': False, 'summary': 'Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.'}], 'exchange': 'worker-type-removed', 'schema': 'http://schemas.taskcluster.net/aws-provisioner/v1/worker-type-message.json#'}, *args, **kwargs)

    funcinfo = {
    }


__all__ = ['createTemporaryCredentials', 'config', '_defaultConfig', 'createApiClient', 'createSession', 'AwsProvisionerEvents']
