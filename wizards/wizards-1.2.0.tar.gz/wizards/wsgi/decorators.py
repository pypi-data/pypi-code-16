import functools

from wizards.wsgi.payload import ResponsePayload


def serializable_response(func):
    """Decorate a controller method that returns a tuple consisting
    of a :class:`~wizards.wsgi.responsepayload.ResponsePayload` object,
    integer specifying the status (optional), dictionary holding the
    headers (optional).
    """
    @functools.wraps(func)
    def wrapped(self, request, **kwargs):
        payload, *args = func(self, request, **kwargs)
        if not isinstance(payload, ResponsePayload):
            payload = ResponsePayload(payload)
        content_type, payload = self.serialize_response(request, payload)
        return self.render_to_response(payload,
            content_type=content_type,
            **dict(zip(['status','headers'], args))
        )

    return wrapped
