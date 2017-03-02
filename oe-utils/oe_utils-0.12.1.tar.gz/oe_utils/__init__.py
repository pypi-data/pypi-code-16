# -*- coding: utf-8 -*-
from collections import Sequence


def conditional_http_tween_factory(handler, registry):
    '''
    Tween that adds ETag headers and tells Pyramid to enable
    conditional responses where appropriate.
    '''
    def conditional_http_tween(request):
        response = handler(request)

        # If the Last-Modified header has been set, we want to enable the
        # conditional response processing.
        if response.last_modified is not None:
            response.conditional_response = True

        # We want to only enable the conditional machinery if either we
        # were given an explicit ETag header by the view or we have a
        # buffered response and can generate the ETag header ourself.
        if response.etag is not None:
            response.conditional_response = True
        # We can only reasonably implement automatic ETags on 200 responses
        # to GET or HEAD requests. The subtles of doing it in other cases
        # are too hard to get right.
        elif request.method in {"GET", "HEAD"} and response.status_code == 200:
            if (isinstance(response.app_iter, Sequence) and
                    len(response.app_iter) == 1):
                response.conditional_response = True
                response.md5_etag()

        return response
    return conditional_http_tween
