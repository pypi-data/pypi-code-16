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


class QueueEvents(BaseClient):
    """
    The queue, typically available at `queue.taskcluster.net`, is responsible
    for accepting tasks and track their state as they are executed by
    workers. In order ensure they are eventually resolved.

    This document describes AMQP exchanges offered by the queue, which allows
    third-party listeners to monitor tasks as they progress to resolution.
    These exchanges targets the following audience:
     * Schedulers, who takes action after tasks are completed,
     * Workers, who wants to listen for new or canceled tasks (optional),
     * Tools, that wants to update their view as task progress.

    You'll notice that all the exchanges in the document shares the same
    routing key pattern. This makes it very easy to bind to all messages
    about a certain kind tasks.

    **Task specific routes**, a task can define a task specific route using
    the `task.routes` property. See task creation documentation for details
    on permissions required to provide task specific routes. If a task has
    the entry `'notify.by-email'` in as task specific route defined in
    `task.routes` all messages about this task will be CC'ed with the
    routing-key `'route.notify.by-email'`.

    These routes will always be prefixed `route.`, so that cannot interfere
    with the _primary_ routing key as documented here. Notice that the
    _primary_ routing key is always prefixed `primary.`. This is ensured
    in the routing key reference, so API clients will do this automatically.

    Please, note that the way RabbitMQ works, the message will only arrive
    in your queue once, even though you may have bound to the exchange with
    multiple routing key patterns that matches more of the CC'ed routing
    routing keys.

    **Delivery guarantees**, most operations on the queue are idempotent,
    which means that if repeated with the same arguments then the requests
    will ensure completion of the operation and return the same response.
    This is useful if the server crashes or the TCP connection breaks, but
    when re-executing an idempotent operation, the queue will also resend
    any related AMQP messages. Hence, messages may be repeated.

    This shouldn't be much of a problem, as the best you can achieve using
    confirm messages with AMQP is at-least-once delivery semantics. Hence,
    this only prevents you from obtaining at-most-once delivery semantics.

    **Remark**, some message generated by timeouts maybe dropped if the
    server crashes at wrong time. Ideally, we'll address this in the
    future. For now we suggest you ignore this corner case, and notify us
    if this corner case is of concern to you.
    """

    classOptions = {
        "exchangePrefix": "exchange/taskcluster-queue/v1/"
    }

    """
    Task Defined Messages

    When a task is created or just defined a message is posted to this
    exchange.

    This message exchange is mainly useful when tasks are scheduled by a
    scheduler that uses `defineTask` as this does not make the task
    `pending`. Thus, no `taskPending` message is published.
    Please, note that messages are also published on this exchange if defined
    using `createTask`.

    This exchange outputs: ``http://schemas.taskcluster.net/queue/v1/task-defined-message.json#``This exchange takes the following keys:

     * routingKeyKind: Identifier for the routing-key kind. This is always `'primary'` for the formalized routing key. (required)

     * taskId: `taskId` for the task this message concerns (required)

     * runId: `runId` of latest run for the task, `_` if no run is exists for the task.

     * workerGroup: `workerGroup` of latest run for the task, `_` if no run is exists for the task.

     * workerId: `workerId` of latest run for the task, `_` if no run is exists for the task.

     * provisionerId: `provisionerId` this task is targeted at. (required)

     * workerType: `workerType` this task must run on. (required)

     * schedulerId: `schedulerId` this task was created by. (required)

     * taskGroupId: `taskGroupId` this task was created in. (required)

     * reserved: Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.
    """

    def taskDefined(self, *args, **kwargs):
        return self._makeTopicExchange({'name': 'taskDefined', 'routingKey': [{'multipleWords': False, 'name': 'routingKeyKind', 'required': True, 'summary': "Identifier for the routing-key kind. This is always `'primary'` for the formalized routing key.", 'constant': 'primary'}, {'multipleWords': False, 'name': 'taskId', 'required': True, 'summary': '`taskId` for the task this message concerns'}, {'multipleWords': False, 'name': 'runId', 'required': False, 'summary': '`runId` of latest run for the task, `_` if no run is exists for the task.'}, {'multipleWords': False, 'name': 'workerGroup', 'required': False, 'summary': '`workerGroup` of latest run for the task, `_` if no run is exists for the task.'}, {'multipleWords': False, 'name': 'workerId', 'required': False, 'summary': '`workerId` of latest run for the task, `_` if no run is exists for the task.'}, {'multipleWords': False, 'name': 'provisionerId', 'required': True, 'summary': '`provisionerId` this task is targeted at.'}, {'multipleWords': False, 'name': 'workerType', 'required': True, 'summary': '`workerType` this task must run on.'}, {'multipleWords': False, 'name': 'schedulerId', 'required': True, 'summary': '`schedulerId` this task was created by.'}, {'multipleWords': False, 'name': 'taskGroupId', 'required': True, 'summary': '`taskGroupId` this task was created in.'}, {'multipleWords': True, 'name': 'reserved', 'required': False, 'summary': 'Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.'}], 'exchange': 'task-defined', 'schema': 'http://schemas.taskcluster.net/queue/v1/task-defined-message.json#'}, *args, **kwargs)

    """
    Task Pending Messages

    When a task becomes `pending` a message is posted to this exchange.

    This is useful for workers who doesn't want to constantly poll the queue
    for new tasks. The queue will also be authority for task states and
    claims. But using this exchange workers should be able to distribute work
    efficiently and they would be able to reduce their polling interval
    significantly without affecting general responsiveness.

    This exchange outputs: ``http://schemas.taskcluster.net/queue/v1/task-pending-message.json#``This exchange takes the following keys:

     * routingKeyKind: Identifier for the routing-key kind. This is always `'primary'` for the formalized routing key. (required)

     * taskId: `taskId` for the task this message concerns (required)

     * runId: `runId` of latest run for the task, `_` if no run is exists for the task. (required)

     * workerGroup: `workerGroup` of latest run for the task, `_` if no run is exists for the task.

     * workerId: `workerId` of latest run for the task, `_` if no run is exists for the task.

     * provisionerId: `provisionerId` this task is targeted at. (required)

     * workerType: `workerType` this task must run on. (required)

     * schedulerId: `schedulerId` this task was created by. (required)

     * taskGroupId: `taskGroupId` this task was created in. (required)

     * reserved: Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.
    """

    def taskPending(self, *args, **kwargs):
        return self._makeTopicExchange({'name': 'taskPending', 'routingKey': [{'multipleWords': False, 'name': 'routingKeyKind', 'required': True, 'summary': "Identifier for the routing-key kind. This is always `'primary'` for the formalized routing key.", 'constant': 'primary'}, {'multipleWords': False, 'name': 'taskId', 'required': True, 'summary': '`taskId` for the task this message concerns'}, {'multipleWords': False, 'name': 'runId', 'required': True, 'summary': '`runId` of latest run for the task, `_` if no run is exists for the task.'}, {'multipleWords': False, 'name': 'workerGroup', 'required': False, 'summary': '`workerGroup` of latest run for the task, `_` if no run is exists for the task.'}, {'multipleWords': False, 'name': 'workerId', 'required': False, 'summary': '`workerId` of latest run for the task, `_` if no run is exists for the task.'}, {'multipleWords': False, 'name': 'provisionerId', 'required': True, 'summary': '`provisionerId` this task is targeted at.'}, {'multipleWords': False, 'name': 'workerType', 'required': True, 'summary': '`workerType` this task must run on.'}, {'multipleWords': False, 'name': 'schedulerId', 'required': True, 'summary': '`schedulerId` this task was created by.'}, {'multipleWords': False, 'name': 'taskGroupId', 'required': True, 'summary': '`taskGroupId` this task was created in.'}, {'multipleWords': True, 'name': 'reserved', 'required': False, 'summary': 'Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.'}], 'exchange': 'task-pending', 'schema': 'http://schemas.taskcluster.net/queue/v1/task-pending-message.json#'}, *args, **kwargs)

    """
    Task Running Messages

    Whenever a task is claimed by a worker, a run is started on the worker,
    and a message is posted on this exchange.

    This exchange outputs: ``http://schemas.taskcluster.net/queue/v1/task-running-message.json#``This exchange takes the following keys:

     * routingKeyKind: Identifier for the routing-key kind. This is always `'primary'` for the formalized routing key. (required)

     * taskId: `taskId` for the task this message concerns (required)

     * runId: `runId` of latest run for the task, `_` if no run is exists for the task. (required)

     * workerGroup: `workerGroup` of latest run for the task, `_` if no run is exists for the task. (required)

     * workerId: `workerId` of latest run for the task, `_` if no run is exists for the task. (required)

     * provisionerId: `provisionerId` this task is targeted at. (required)

     * workerType: `workerType` this task must run on. (required)

     * schedulerId: `schedulerId` this task was created by. (required)

     * taskGroupId: `taskGroupId` this task was created in. (required)

     * reserved: Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.
    """

    def taskRunning(self, *args, **kwargs):
        return self._makeTopicExchange({'name': 'taskRunning', 'routingKey': [{'multipleWords': False, 'name': 'routingKeyKind', 'required': True, 'summary': "Identifier for the routing-key kind. This is always `'primary'` for the formalized routing key.", 'constant': 'primary'}, {'multipleWords': False, 'name': 'taskId', 'required': True, 'summary': '`taskId` for the task this message concerns'}, {'multipleWords': False, 'name': 'runId', 'required': True, 'summary': '`runId` of latest run for the task, `_` if no run is exists for the task.'}, {'multipleWords': False, 'name': 'workerGroup', 'required': True, 'summary': '`workerGroup` of latest run for the task, `_` if no run is exists for the task.'}, {'multipleWords': False, 'name': 'workerId', 'required': True, 'summary': '`workerId` of latest run for the task, `_` if no run is exists for the task.'}, {'multipleWords': False, 'name': 'provisionerId', 'required': True, 'summary': '`provisionerId` this task is targeted at.'}, {'multipleWords': False, 'name': 'workerType', 'required': True, 'summary': '`workerType` this task must run on.'}, {'multipleWords': False, 'name': 'schedulerId', 'required': True, 'summary': '`schedulerId` this task was created by.'}, {'multipleWords': False, 'name': 'taskGroupId', 'required': True, 'summary': '`taskGroupId` this task was created in.'}, {'multipleWords': True, 'name': 'reserved', 'required': False, 'summary': 'Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.'}], 'exchange': 'task-running', 'schema': 'http://schemas.taskcluster.net/queue/v1/task-running-message.json#'}, *args, **kwargs)

    """
    Artifact Creation Messages

    Whenever the `createArtifact` end-point is called, the queue will create
    a record of the artifact and post a message on this exchange. All of this
    happens before the queue returns a signed URL for the caller to upload
    the actual artifact with (pending on `storageType`).

    This means that the actual artifact is rarely available when this message
    is posted. But it is not unreasonable to assume that the artifact will
    will become available at some point later. Most signatures will expire in
    30 minutes or so, forcing the uploader to call `createArtifact` with
    the same payload again in-order to continue uploading the artifact.

    However, in most cases (especially for small artifacts) it's very
    reasonable assume the artifact will be available within a few minutes.
    This property means that this exchange is mostly useful for tools
    monitoring task evaluation. One could also use it count number of
    artifacts per task, or _index_ artifacts though in most cases it'll be
    smarter to index artifacts after the task in question have completed
    successfully.

    This exchange outputs: ``http://schemas.taskcluster.net/queue/v1/artifact-created-message.json#``This exchange takes the following keys:

     * routingKeyKind: Identifier for the routing-key kind. This is always `'primary'` for the formalized routing key. (required)

     * taskId: `taskId` for the task this message concerns (required)

     * runId: `runId` of latest run for the task, `_` if no run is exists for the task. (required)

     * workerGroup: `workerGroup` of latest run for the task, `_` if no run is exists for the task. (required)

     * workerId: `workerId` of latest run for the task, `_` if no run is exists for the task. (required)

     * provisionerId: `provisionerId` this task is targeted at. (required)

     * workerType: `workerType` this task must run on. (required)

     * schedulerId: `schedulerId` this task was created by. (required)

     * taskGroupId: `taskGroupId` this task was created in. (required)

     * reserved: Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.
    """

    def artifactCreated(self, *args, **kwargs):
        return self._makeTopicExchange({'name': 'artifactCreated', 'routingKey': [{'multipleWords': False, 'name': 'routingKeyKind', 'required': True, 'summary': "Identifier for the routing-key kind. This is always `'primary'` for the formalized routing key.", 'constant': 'primary'}, {'multipleWords': False, 'name': 'taskId', 'required': True, 'summary': '`taskId` for the task this message concerns'}, {'multipleWords': False, 'name': 'runId', 'required': True, 'summary': '`runId` of latest run for the task, `_` if no run is exists for the task.'}, {'multipleWords': False, 'name': 'workerGroup', 'required': True, 'summary': '`workerGroup` of latest run for the task, `_` if no run is exists for the task.'}, {'multipleWords': False, 'name': 'workerId', 'required': True, 'summary': '`workerId` of latest run for the task, `_` if no run is exists for the task.'}, {'multipleWords': False, 'name': 'provisionerId', 'required': True, 'summary': '`provisionerId` this task is targeted at.'}, {'multipleWords': False, 'name': 'workerType', 'required': True, 'summary': '`workerType` this task must run on.'}, {'multipleWords': False, 'name': 'schedulerId', 'required': True, 'summary': '`schedulerId` this task was created by.'}, {'multipleWords': False, 'name': 'taskGroupId', 'required': True, 'summary': '`taskGroupId` this task was created in.'}, {'multipleWords': True, 'name': 'reserved', 'required': False, 'summary': 'Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.'}], 'exchange': 'artifact-created', 'schema': 'http://schemas.taskcluster.net/queue/v1/artifact-created-message.json#'}, *args, **kwargs)

    """
    Task Completed Messages

    When a task is successfully completed by a worker a message is posted
    this exchange.
    This message is routed using the `runId`, `workerGroup` and `workerId`
    that completed the task. But information about additional runs is also
    available from the task status structure.

    This exchange outputs: ``http://schemas.taskcluster.net/queue/v1/task-completed-message.json#``This exchange takes the following keys:

     * routingKeyKind: Identifier for the routing-key kind. This is always `'primary'` for the formalized routing key. (required)

     * taskId: `taskId` for the task this message concerns (required)

     * runId: `runId` of latest run for the task, `_` if no run is exists for the task. (required)

     * workerGroup: `workerGroup` of latest run for the task, `_` if no run is exists for the task. (required)

     * workerId: `workerId` of latest run for the task, `_` if no run is exists for the task. (required)

     * provisionerId: `provisionerId` this task is targeted at. (required)

     * workerType: `workerType` this task must run on. (required)

     * schedulerId: `schedulerId` this task was created by. (required)

     * taskGroupId: `taskGroupId` this task was created in. (required)

     * reserved: Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.
    """

    def taskCompleted(self, *args, **kwargs):
        return self._makeTopicExchange({'name': 'taskCompleted', 'routingKey': [{'multipleWords': False, 'name': 'routingKeyKind', 'required': True, 'summary': "Identifier for the routing-key kind. This is always `'primary'` for the formalized routing key.", 'constant': 'primary'}, {'multipleWords': False, 'name': 'taskId', 'required': True, 'summary': '`taskId` for the task this message concerns'}, {'multipleWords': False, 'name': 'runId', 'required': True, 'summary': '`runId` of latest run for the task, `_` if no run is exists for the task.'}, {'multipleWords': False, 'name': 'workerGroup', 'required': True, 'summary': '`workerGroup` of latest run for the task, `_` if no run is exists for the task.'}, {'multipleWords': False, 'name': 'workerId', 'required': True, 'summary': '`workerId` of latest run for the task, `_` if no run is exists for the task.'}, {'multipleWords': False, 'name': 'provisionerId', 'required': True, 'summary': '`provisionerId` this task is targeted at.'}, {'multipleWords': False, 'name': 'workerType', 'required': True, 'summary': '`workerType` this task must run on.'}, {'multipleWords': False, 'name': 'schedulerId', 'required': True, 'summary': '`schedulerId` this task was created by.'}, {'multipleWords': False, 'name': 'taskGroupId', 'required': True, 'summary': '`taskGroupId` this task was created in.'}, {'multipleWords': True, 'name': 'reserved', 'required': False, 'summary': 'Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.'}], 'exchange': 'task-completed', 'schema': 'http://schemas.taskcluster.net/queue/v1/task-completed-message.json#'}, *args, **kwargs)

    """
    Task Failed Messages

    When a task ran, but failed to complete successfully a message is posted
    to this exchange. This is same as worker ran task-specific code, but the
    task specific code exited non-zero.

    This exchange outputs: ``http://schemas.taskcluster.net/queue/v1/task-failed-message.json#``This exchange takes the following keys:

     * routingKeyKind: Identifier for the routing-key kind. This is always `'primary'` for the formalized routing key. (required)

     * taskId: `taskId` for the task this message concerns (required)

     * runId: `runId` of latest run for the task, `_` if no run is exists for the task.

     * workerGroup: `workerGroup` of latest run for the task, `_` if no run is exists for the task.

     * workerId: `workerId` of latest run for the task, `_` if no run is exists for the task.

     * provisionerId: `provisionerId` this task is targeted at. (required)

     * workerType: `workerType` this task must run on. (required)

     * schedulerId: `schedulerId` this task was created by. (required)

     * taskGroupId: `taskGroupId` this task was created in. (required)

     * reserved: Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.
    """

    def taskFailed(self, *args, **kwargs):
        return self._makeTopicExchange({'name': 'taskFailed', 'routingKey': [{'multipleWords': False, 'name': 'routingKeyKind', 'required': True, 'summary': "Identifier for the routing-key kind. This is always `'primary'` for the formalized routing key.", 'constant': 'primary'}, {'multipleWords': False, 'name': 'taskId', 'required': True, 'summary': '`taskId` for the task this message concerns'}, {'multipleWords': False, 'name': 'runId', 'required': False, 'summary': '`runId` of latest run for the task, `_` if no run is exists for the task.'}, {'multipleWords': False, 'name': 'workerGroup', 'required': False, 'summary': '`workerGroup` of latest run for the task, `_` if no run is exists for the task.'}, {'multipleWords': False, 'name': 'workerId', 'required': False, 'summary': '`workerId` of latest run for the task, `_` if no run is exists for the task.'}, {'multipleWords': False, 'name': 'provisionerId', 'required': True, 'summary': '`provisionerId` this task is targeted at.'}, {'multipleWords': False, 'name': 'workerType', 'required': True, 'summary': '`workerType` this task must run on.'}, {'multipleWords': False, 'name': 'schedulerId', 'required': True, 'summary': '`schedulerId` this task was created by.'}, {'multipleWords': False, 'name': 'taskGroupId', 'required': True, 'summary': '`taskGroupId` this task was created in.'}, {'multipleWords': True, 'name': 'reserved', 'required': False, 'summary': 'Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.'}], 'exchange': 'task-failed', 'schema': 'http://schemas.taskcluster.net/queue/v1/task-failed-message.json#'}, *args, **kwargs)

    """
    Task Exception Messages

    Whenever TaskCluster fails to run a message is posted to this exchange.
    This happens if the task isn't completed before its `deadlìne`,
    all retries failed (i.e. workers stopped responding), the task was
    canceled by another entity, or the task carried a malformed payload.

    The specific _reason_ is evident from that task status structure, refer
    to the `reasonResolved` property for the last run.

    This exchange outputs: ``http://schemas.taskcluster.net/queue/v1/task-exception-message.json#``This exchange takes the following keys:

     * routingKeyKind: Identifier for the routing-key kind. This is always `'primary'` for the formalized routing key. (required)

     * taskId: `taskId` for the task this message concerns (required)

     * runId: `runId` of latest run for the task, `_` if no run is exists for the task.

     * workerGroup: `workerGroup` of latest run for the task, `_` if no run is exists for the task.

     * workerId: `workerId` of latest run for the task, `_` if no run is exists for the task.

     * provisionerId: `provisionerId` this task is targeted at. (required)

     * workerType: `workerType` this task must run on. (required)

     * schedulerId: `schedulerId` this task was created by. (required)

     * taskGroupId: `taskGroupId` this task was created in. (required)

     * reserved: Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.
    """

    def taskException(self, *args, **kwargs):
        return self._makeTopicExchange({'name': 'taskException', 'routingKey': [{'multipleWords': False, 'name': 'routingKeyKind', 'required': True, 'summary': "Identifier for the routing-key kind. This is always `'primary'` for the formalized routing key.", 'constant': 'primary'}, {'multipleWords': False, 'name': 'taskId', 'required': True, 'summary': '`taskId` for the task this message concerns'}, {'multipleWords': False, 'name': 'runId', 'required': False, 'summary': '`runId` of latest run for the task, `_` if no run is exists for the task.'}, {'multipleWords': False, 'name': 'workerGroup', 'required': False, 'summary': '`workerGroup` of latest run for the task, `_` if no run is exists for the task.'}, {'multipleWords': False, 'name': 'workerId', 'required': False, 'summary': '`workerId` of latest run for the task, `_` if no run is exists for the task.'}, {'multipleWords': False, 'name': 'provisionerId', 'required': True, 'summary': '`provisionerId` this task is targeted at.'}, {'multipleWords': False, 'name': 'workerType', 'required': True, 'summary': '`workerType` this task must run on.'}, {'multipleWords': False, 'name': 'schedulerId', 'required': True, 'summary': '`schedulerId` this task was created by.'}, {'multipleWords': False, 'name': 'taskGroupId', 'required': True, 'summary': '`taskGroupId` this task was created in.'}, {'multipleWords': True, 'name': 'reserved', 'required': False, 'summary': 'Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.'}], 'exchange': 'task-exception', 'schema': 'http://schemas.taskcluster.net/queue/v1/task-exception-message.json#'}, *args, **kwargs)

    """
    Task Group Resolved Messages

    A message is published on task-group-resolved whenever all submitted
    tasks (whether scheduled or unscheduled) for a given task group have
    been resolved, regardless of whether they resolved as successful or
    not. A task group may be resolved multiple times, since new tasks may
    be submitted against an already resolved task group.

    This exchange outputs: ``http://schemas.taskcluster.net/queue/v1/task-group-resolved.json#``This exchange takes the following keys:

     * routingKeyKind: Identifier for the routing-key kind. This is always `'primary'` for the formalized routing key. (required)

     * taskGroupId: `taskGroupId` for the task-group this message concerns (required)

     * schedulerId: `schedulerId` for the task-group this message concerns (required)

     * reserved: Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.
    """

    def taskGroupResolved(self, *args, **kwargs):
        return self._makeTopicExchange({'name': 'taskGroupResolved', 'routingKey': [{'multipleWords': False, 'name': 'routingKeyKind', 'required': True, 'summary': "Identifier for the routing-key kind. This is always `'primary'` for the formalized routing key.", 'constant': 'primary'}, {'multipleWords': False, 'name': 'taskGroupId', 'required': True, 'summary': '`taskGroupId` for the task-group this message concerns'}, {'multipleWords': False, 'name': 'schedulerId', 'required': True, 'summary': '`schedulerId` for the task-group this message concerns'}, {'multipleWords': True, 'name': 'reserved', 'required': False, 'summary': 'Space reserved for future routing-key entries, you should always match this entry with `#`. As automatically done by our tooling, if not specified.'}], 'exchange': 'task-group-resolved', 'schema': 'http://schemas.taskcluster.net/queue/v1/task-group-resolved.json#'}, *args, **kwargs)

    funcinfo = {
    }


__all__ = ['createTemporaryCredentials', 'config', '_defaultConfig', 'createApiClient', 'createSession', 'QueueEvents']
