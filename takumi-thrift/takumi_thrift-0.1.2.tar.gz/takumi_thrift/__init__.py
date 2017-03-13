# -*- coding: utf-8 -*-

"""
takumi_thrift
~~~~~~~~~~~~~

Thriftpy instruments.

:Example:

client = Client(meta={'client_name': 'test_client', 'client_version': '0.1.0'})
client.ping(meta={'hello': 90, 'world': 123})

@app.api_with_ctx
def ping(ctx):
    print(ctx.meta)
    return Response(value='pong', meta={'hello': 'world'})


Request data frame:

    message_begin args message_end
    meta_begin meta meta_end message_begin args message_end

Response data frame:

    message_begin result message_end
    meta_begin meta meta_end message_begin result message_end
"""

from .processor import Processor
from .client import Client
from .wrappers import Response, Metadata

__all__ = ['Processor', 'Client', 'Response', 'Metadata']
