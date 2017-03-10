# -*- coding: utf-8 -*-
# Copyright (c) 2016 Sqreen. All Rights Reserved.
# Please refer to our terms for more information: https://www.sqreen.io/terms.html
""" Insert custom headers for Flask
"""
import logging

from .headers_insert import BaseHeadersInsertCB


LOGGER = logging.getLogger(__name__)


def convert_to_str(headers):
    """ Encode a list of headers tuples into latin1
    """
    for header_name, header_value in headers:
        header_name = str(header_name.encode('latin-1', errors='replace').decode('latin-1'))
        header_value = str(header_value.encode('latin-1', errors='replace').decode('latin-1'))
        yield (header_name, header_value)


class HeadersInsertCBFlask(BaseHeadersInsertCB):
    """ Callback that add the custom sqreen header
    """

    def post(self, original, response, *args, **kwargs):
        """ Set headers
        """
        try:
            for header_name, header_value in self.headers.items():
                response.headers.set(header_name, header_value)
        except Exception:
            LOGGER.warning("An error occured", exc_info=True)

        return {}
