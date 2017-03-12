import uuid

import ioc

from ea.lib.datastructures import ImmutableDTO
from ea.cqrs.command import Request
import ea.lib.timezone


class Gateway(object):
    InvalidCommand = type('InvalidCommand', (Exception,), {})
    default_subject_id = ioc.class_property('Gateway.default_subject_id')

    def __init__(self, transport):
        self.transport = transport

    def issue(self, command, issuer=None, cid=None, asynchronous=True):
        """Dispatch a command and execute it. The command is assumed
        to be validated and sanitized before dispatching.
        """
        command_id = str(uuid.uuid4())
        cid = cid or str(uuid.uuid4())
        issuer = issuer or uuid.UUID(int=0)
        if not command.is_valid():
            raise self.InvalidCommand(command.errors)

        request = Request(
            meta={
                'id': command_id,
                'name': command.meta.name,
                'issued': ea.lib.timezone.now(),
                'sid': issuer,
                'cid': cid
            },
            params=command.dump()
        )

        deferred = self.put(request, asynchronous=asynchronous)
        return ImmutableDTO(
            command_id=command_id,
            correlation_id=cid,
            result=deferred,
            wait=deferred.wait
        )

    def put(self, request, asynchronous=True):
        return self.transport.send(request, wait=not asynchronous)
