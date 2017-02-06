from flask import request
from functools import wraps
from . import lambda_helper


def flaskify(lfunction):
    def real_decorator(ffunction):
        @wraps(ffunction)
        def wrapper(*args, **kwargs):
            #  print kwargs
            event = lambda_helper.get_event(request)
            for kwarg in kwargs:
                event['pathParameters'][kwarg] = kwargs[kwarg]
            context = None
            response = lfunction(event, context)
            #  print response
            return response.get('body')
        return wrapper
    return real_decorator
