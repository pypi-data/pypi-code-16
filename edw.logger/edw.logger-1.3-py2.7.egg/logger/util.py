""" Utility functions.
"""


def get_ip(request):
    if "HTTP_X_FORWARDED_FOR" in request.environ:
        # Virtual host
        ip = request.environ["HTTP_X_FORWARDED_FOR"]
    elif "HTTP_HOST" in request.environ:
        # Non-virtualhost
        ip = request.environ["REMOTE_ADDR"]
    else:
        ip = None

    return ip


def get_user_data(request):
    try:
        user = request.get('AUTHENTICATED_USER')
    except AttributeError:
        return dict(user='NO_REQUEST', ip='NO_REQUEST')

    return dict(user=user.getUserName(), ip=get_ip(user.REQUEST))
