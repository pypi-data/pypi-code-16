from webtest import TestApp as Client
import pytest
from jsonschema import Draft3Validator

from more.jsonschema import JsonSchemaApp, loader


def test_jsonschema():
    class User(object):
        def __init__(self, name=None, age=None):
            self.name = name
            self.age = age

    user_schema = {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'minLength': 3
            },
            'age': {
                'type': 'integer',
                'minimum': 10
            }
        },
        'required': ['name', 'age']
    }

    class App(JsonSchemaApp):
        pass

    user = User()

    @App.path(model=User, path='/')
    def get_user():
        return user

    @App.json(model=User, request_method='POST', load=loader(user_schema))
    def user_post(self, request, json):
        for key, value in json.items():
            setattr(self, key, value)

    c = Client(App())

    c.post_json('/', {'name': 'Somebody', 'age': 22})
    assert user.name == 'Somebody'
    assert user.age == 22

    r = c.post_json('/', {'name': 'Another'}, status=422)
    assert r.json == ["'age' is a required property"]

    r = c.post_json('/', {'name': 'Another', 'age': 8}, status=422)
    assert r.json == ['8 is less than the minimum of 10']

    r = c.post_json('/', {'name': 'An', 'age': 8}, status=422)
    assert r.json == [
        '8 is less than the minimum of 10',
        "'An' is too short"
    ]

def test_jsonschema_Draft3Validator():
    class User(object):
        def __init__(self, name=None, age=None):
            self.name = name
            self.age = age

    user_schema = {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'minLength': 3,
                'required': True
            },
            'age': {
                'type': 'integer',
                'minimum': 10,
                'required': True
            }
        }
    }

    class App(JsonSchemaApp):
        pass

    user = User()

    @App.path(model=User, path='/')
    def get_user():
        return user

    load = loader(user_schema, validator=Draft3Validator)

    @App.json(model=User, request_method='POST', load=load)
    def user_post(self, request, json):
        for key, value in json.items():
            setattr(self, key, value)

    c = Client(App())

    c.post_json('/', {'name': 'Somebody', 'age': 22})
    assert user.name == 'Somebody'
    assert user.age == 22

    r = c.post_json('/', {'name': 'Another'}, status=422)
    assert r.json == ["'age' is a required property"]

    r = c.post_json('/', {'name': 'Another', 'age': 8}, status=422)
    assert r.json == ['8 is less than the minimum of 10']

    r = c.post_json('/', {'name': 'An', 'age': 8}, status=422)
    assert r.json == [
        '8 is less than the minimum of 10',
        "'An' is too short"
    ]
