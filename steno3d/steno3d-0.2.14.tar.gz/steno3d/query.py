from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from six import integer_types

from .client import Comms, needs_login
from .project import Project


MINE = 'api/project/steno3ds/mine'


def _query(url, queue=10):
    cursor = ''
    more = True
    print('Fetching projects from the database ...')
    while more:
        resp = Comms.get('{url}?brief=True&num={n}&cursor={c}'.format(
            url=url, n=queue, c=cursor
        ))
        rjson = resp.json()
        cursor = rjson['cursor']
        more = rjson['more']
        for proj in rjson['data']:
            yield proj
        print('Fetching more projects from the database ...')


def _short_json(proj_json):
    return {'uid': proj_json['uid'],
            'title': proj_json['title'],
            'description': proj_json['description'],
            'created': proj_json['date']}


@needs_login
def my_projects(n=None, queue=100):
    if n is None:
        print('Querying all your projects ...')
        return [_short_json(p) for p in _query(MINE, queue)]
    if not isinstance(n, integer_types):
        raise ValueError('{}: n must be int'.format(n))
    print('Querying your most recent {} project(s) ...'.format(n))
    projs = []
    projit = _query(MINE, min(n, queue))
    for _ in range(n):
        try:
            projs += [_short_json(next(projit))]
        except StopIteration:
            print('{n}: n > total number of projects, {p} returned'.format(
                n=n, p=len(projs)
            ))
            break
    print('...Complete!')
    return projs


@needs_login
def project_by_uid(uid, copy=None):
    return Project._build(uid, copy)


@needs_login
def last_project(copy=None):
    try:
        return project_by_uid(next(_query(MINE, 1))['uid'], copy)
    except StopIteration:
        print('No projects available!')
