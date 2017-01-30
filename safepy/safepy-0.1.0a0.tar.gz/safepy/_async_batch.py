from asyncio.locks import Lock, Event
from enum import Enum

"""
https://azure.microsoft.com/en-us/blog/new-article-best-practices-for-performance-improvements-using-service-bus-brokered-messaging/
"""


class AcceptResult(Enum):
    not_accepted = 0
    accepted = 1
    last_accepted = 2


class AsyncBatchOperation(object):
    def __init__(self):
        self._event = Event()
        self._event_others = Event()
        self._items = []
        self._result = (None, None)

    async def wait_for_result_async(self, index):
        await self._event_others.wait()

        if self._exception:
            raise copy_exception_with_traceback(self._exception)

        if isinstance(self._result, Sequence):
            return self._result[index]

        # the best effort, we return the result as it is
        return self._result

    async def process_batch(self, batch):
        await self._event.wait()

        result, exception = None, None
        try:
            result = await self._function(*batch.items)
        except Exception as e:
            exception = e

        self._result = result
        self._exception = exception
        self._event_others.set()

    def signal_ready(self):
        self._event.set()

class AsyncBatchProcessor(object):
    def __init__(self, function, batch_factory):
        self._function = function
        self._batch_factory = batch_factory
        self._batch = batch_factory()
        self._lock = Lock()

    async def process(self, item):
        with await self._lock:
            batch = self._batch
            batch_operation = self._batch_operation

            accept_result, key = batch.accept(item)
            if accept_result == AcceptResult.not_accepted:
                # we have to reset the current batch if a new item is not accepted
                # and signal to the result handler
                batch_operation.signal_ready()
                batch, batch_operation = self._reset()

                # intentionally overwritten to handle last_accepted as well
                accept_result, key = batch.accept(item)
                # avoid not accepting single item
                if accept_result == AcceptResult.not_accepted:
                    # now the batch is locked, so no need
                    raise BatchedError("an item rejected from an empty batch")

            if accept_result == AcceptResult.last_accepted:
                batch_operation.signal_ready()
                self._reset()

            current_index = len(batch) - 1