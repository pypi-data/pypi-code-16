import requests


def get_user(user):
    target = 'https://tastynode.com/beta/api/user/%s' % user
    r = requests.get(target)
    r = r.json()
    return r


def get_image():
    return 'Temp'


def get_staff():
    return 'Temp'


def random_image():
    return 'Temp'


def node_status():
    return 'Temp'


def server_status():
    return 'Temp'


def teamspeak_status():
    return 'Temp'
