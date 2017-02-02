import datetime
import requests
import time

from crowdcurio_client.crowdcurio import (
    CrowdCurioAPIException, CrowdCurioObject
)

class Curio(CrowdCurioObject):
    _api_slug = 'curio'
    _link_slug = 'curio'
    _edit_attributes = (
        'slug',
        'title',
        'question'
        'description',
        'motivation',
        'data_type',
        'question',
    )

    @classmethod
    def find(cls, id='', slug=None):
        if not id and not slug:
            return None
        return cls.where(id=id, slug=slug).next()

    def add(self, project):
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "Curio", "id": self.id, "relationships": {"project":{"data":{"type":"Project","id":project.id}}}}}
        )

    def remove(self, project):
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "Curio", "id": self.id, "relationships": {"project":{}}}}
        )

    def destroy(self):
        self.delete('{}'.format(self.id), json={'data': {'type':'Curio', 'id': self.id}})