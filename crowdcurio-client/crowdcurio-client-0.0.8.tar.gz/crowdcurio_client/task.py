import datetime
import requests
import time

from crowdcurio_client.crowdcurio import (
    CrowdCurioAPIException, CrowdCurioObject
)

class Task(CrowdCurioObject):
    _api_slug = 'task'
    _link_slug = 'task'
    _edit_attributes = (
        'slug',
        'name',
        'type',
        'labels',
    )

    @classmethod
    def find(cls, id='', slug=None):
        if not id and not slug:
            return None
        return cls.where(id=id, slug=slug).next()

    def add(self, curio):
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "Task", "id": self.id, "relationships": {"curio":{"data":{"type":"Curio","id":curio.id}}}}}
        )

    def remove(self, curio):
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "Task", "id": self.id, "relationships": {"curio":{}}}}
        )

    def destroy(self):
        self.delete('{}'.format(self.id), json={'data': {'type':'Task', 'id': self.id}})