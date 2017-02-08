class Resource(object):
    """
    Base class for all v3 REST Services
    """
    def __init__(self, attributes=None, api=None):
        self.__dict__['api'] = api
        self.__dict__['__data__'] = dict()
        self.merge_attributes(attributes)

    def merge_attributes(self, attributes):
        for (k, v) in attributes.items():
            setattr(self, k, v)
            self.__data__[k] = v

    def to_dict(self):
        return self.__data__

    def __setattr__(self, key, value):
        super(Resource, self).__setattr__(key, value)
        self.__data__[key] = value

    def __setitem__(self, key, value):
        self.__data__[key] = value

    def __getitem__(self, item):
        return self.__data__.get(item, None)


class Find(Resource):

    @classmethod
    def find(cls, resource_id, api=None):
        assert api is not None
        url = "{0}/{1}".format(cls.path, resource_id)
        return cls(attributes=api.get_request(url).json(), api=api)


class List(Resource):
    pass


class Create(Resource):
    def create(self):
        response = self.api.post_request(self.path, self.to_dict())
        self.merge_attributes(response.json())


class Update(Resource):
    def update(self):
        response = self.api.put_request("{0}/{1}".format(self.path, self['ID']), self.to_dict())
        self.merge_attributes(response.json())


class Delete(Resource):
    def delete(self):
        response = self.api.delete_request("{0}/{1}".format(self.path, self['ID']))
        self.merge_attributes(response.json())
