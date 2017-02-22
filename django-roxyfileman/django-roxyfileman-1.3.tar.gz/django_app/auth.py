from django.http import HttpResponse
from functools import wraps


def auth_decorator(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST':
            return HttpResponse('Hello')
        return view(request, *args, **kwargs)
    return wrapper
