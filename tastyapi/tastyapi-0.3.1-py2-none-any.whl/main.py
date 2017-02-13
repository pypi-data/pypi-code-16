import requests


def get_user(user):
    target = 'https://tastynode.com/api/user/%s' % user
    r = requests.get(target)
    r = r.json()
    return r


def get_image(keyword):
    target = 'https://tastynode.com/api/random/%s' % keyword
    r = requests.get(target)
    r = r.text()
    return r


def get_staff():
    target = 'https://tastynode.com/api/status/staff'
    r = requests.get(target)
    r = r.json()
    return r


def random_image():
    target = 'https://tastynode.com/api/random/image'
    r = requests.get(target)
    r = r.text()
    return r


def node_status():
    target = 'https://tastynode.com/api/status/nodes'
    r = requests.get(target)
    r = r.json()
    return r


def server_status():
    target = 'https://tastynode.com/api/status/servers'
    r = requests.get(target)
    r = r.json()
    return r


def teamspeak_status():
    target = 'https://tastynode.com/api/status/teamspeak'
    r = requests.get(target)
    r = r.json()
    return r
