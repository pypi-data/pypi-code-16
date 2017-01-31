# Copyright 2014-2016 Morgan Delahaye-Prat. All Rights Reserved.
#
# Licensed under the Simplified BSD License (the "License");
# you may not use this file except in compliance with the License.
"""Request and related classes."""


import json
import asyncio

from aiohttp.web_reqrep import Request as BaseRequest


class Request(BaseRequest):
    """Contains all the information about an incoming HTTP request."""

    def __init__(self, *args, **kwargs):
        """Create a new Request."""
        super().__init__(*args, **kwargs)

    @property
    def args(self):
        """Alternate spelling for `Request.GET`."""
        return self.GET

    @asyncio.coroutine
    def json(self, *, loader=json.loads):
        """Parse the request content as JSON."""
        body = yield from self.text()
        if body:
            return loader(body)
        return None

    @asyncio.coroutine
    def _prepare_hook(self, response):
        #
        # allow early catch of HTTPExceptions before matching a rule
        apps = ()
        if self.match_info:
            apps = self.match_info.apps

        for app in apps:
            yield from app.on_response_prepare.send(self, response)
