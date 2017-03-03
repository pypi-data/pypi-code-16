import functools

from wizards.wsgi.responsepayload import ResponsePayload


def validate_payload(schema_class, many=False):
    """Perform an initial validation of the request payload using
    the given schema.
    """

    def decorator(func):
        schema = schema_class(
            many=many
        )

        @functools.wraps(func)
        def wrapped(self, request, *args, **kwargs):
            request.payload, errors = self.deserialize(request.get_data())
            if errors:
                return self.render_to_response(
                    status=422,
                    payload=self.serializer.serialize({
                        'code': "DTO_VALIDATION_ERROR",
                        'message': "A Data Transfer Object (DTO) with an unknown schema was received.",
                        'hint': "Refer to the API specification for more information about this endpoint.",
                        'fields': errors
                    }),
                    content_type=self.serializer.content_type
                )

            return func(self, request, *args, **kwargs)

    return decorator

def serializable_response(func):
    """Decorate a controller method that returns a tuple consisting
    of a :class:`~wizards.wsgi.responsepayload.ResponsePayload` object,
    integer specifying the status (optional), dictionary holding the
    headers (optional).
    """

    @functools.wraps(func)
    def wrapped(self, request, **kwargs):
        payload, *args = func(self, request, **kwargs)
        return self.render_to_response(
            payload=ResponsePayload(payload)\
                .serialize(self.serializer.serialize),
            content_type=self.serializer.content_type,
            **dict(zip(['status','headers'], args))
        )

    return wrapped
