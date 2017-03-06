from axsemantics import constants
from axsemantics.errors import (
    APIError,
    AuthenticationError,
)
from axsemantics.net import RequestHandler
import requests


def login(token):
    if len(token) == 40:
        # hope that it's an old style token, for now
        constants.API_TOKEN = token
        constants.API_TOKEN_RINCEWIND = token
    else:
        id_token = login_idm(token)
        if id_token:
            constants.REFRESH_TOKEN = token
            constants.API_TOKEN = id_token
            constants.API_TOKEN_RINCEWIND = id_token
        else:
            raise AuthenticationError


def login_idm(token):
    data = {
        'refresh_token': token
    }
    r = requests.post("https://idm.ax-semantics.com/v1/token-exchange/", json=data)
    if r.status_code == 200:
        return r.json().get('id_token')


def create_object(data, api_token=None, _type=None, **kwargs):
    from axsemantics.resources import (
        ContentProject,
        Thing,
        Training,
    )
    types = {
        'content-project': ContentProject,
        'thing': Thing,
        'training': Training,
    }

    if isinstance(data, list):
        return [create_object(element, api_token, type=_type, **kwargs) for element in data]

    from axsemantics.base import AXSemanticsObject
    if isinstance(data, dict) and not isinstance(data, AXSemanticsObject):
        data = data.copy()

        _class = types.get(_type, AXSemanticsObject)
        return _class.create_from_dict(data, api_token, **kwargs)

    return data


def _get_update_dict(current, previous):
    if isinstance(current, dict):
        previous = previous or {}
        diff = current.copy()
        diff.update({
            key: ''
            for key in set(previous.keys()) - set(current.keys())
        })
        return diff

    return current if current is not None else ""
