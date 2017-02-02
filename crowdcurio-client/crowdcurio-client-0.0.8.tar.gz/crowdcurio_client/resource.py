import datetime
import requests
import time

from crowdcurio_client.crowdcurio import CrowdCurioObject

class Resource(CrowdCurioObject):
    _api_slug = 'resource'
    _link_slug = 'resource'
    _edit_attributes = (
        'slug',
        'name',
        'url',
        'class_label',
    )

    @classmethod
    def find(cls, id='', slug=None):
        if not id and not slug:
            return None
        return cls.where(id=id, slug=slug).next()

    def add(self, task):
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "Resource", "id": self.id, "relationships": {"task":{"data":{"type":"Task","id":task.id}}}}}
        )

    def remove(self, task):
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "Resource", "id": self.id, "relationships": {"task":{}}}})

    def destroy(self):
        self.delete('{}'.format(self.id), json={'data': {'type':'Resource', 'id': self.id}})