import json

import diax.errors
import ramlfications
import requests

def _to_resource_name(uri):
    "Convert a resource uri like '/foo/bar/' to a name like foo.bar"
    if uri[0] == '/':
        uri = uri[1:]
    if uri[-1] == '/':
        uri = uri[:-1]
    parts = uri.split('/')
    valid = [p for p in parts if p != '{uuid}']
    return '.'.join(valid)

class Service():
    def __init__(self, client, name):
        self.baseUri        = None
        self.client         = client
        self.documentation  = None
        self.media_type     = None
        self.name           = name
        self.options        = None
        self.resources      = {}
        self.title          = None

    def load(self):
        response = self.client.options(self.name, '/')
        raml = ramlfications.loads(response)
        for k in ('baseUri', 'documentation', 'mediaType', 'title', 'version'):
            setattr(self, k, raml.pop(k, None))
        for relativeUri, resource in raml.items():
            resource_name = _to_resource_name(relativeUri)
            if resource_name not in self.resources:
                self.resources[resource_name] = Resource(self, relativeUri)
            self.resources[resource_name].add(resource)

    def __getitem__(self, name):
        return self.resources[name]

class Resource():
    def __init__(self, service, uri):
        self.methods = {}
        self.service = service
        self.uri     = uri

    def add(self, schema):
        for k, v in schema.items():
            if k not in ('delete', 'get', 'options', 'patch', 'post', 'put'):
                continue
            self.methods[k] = Method(v)

    def post(self, payload):
        self.methods['post'].validate(payload)
        _, headers = self.service.client.post(self.service.name, self.uri, payload)
        return headers['Location']

class Method():
    def __init__(self, schema):
        self.schema = None
        for content_type, descriptor in schema.get('body', {}).items():
            if not (content_type == 'application/json' and 'schema' in descriptor):
                continue
            self.schema = json.loads(descriptor['schema'])

    def validate(self, payload):
        errors = []
        for k in self.schema['required']:
            if k not in payload:
                errors.append("The parameter '{}' is required".format(k))
        if errors:
            raise diax.errors.ValidationError("\n".join(errors))

def connect(client, name):
    "Connect to the given service, pull down the definition of its endpoints"
    service = Service(client, name)
    service.load()
    return service
