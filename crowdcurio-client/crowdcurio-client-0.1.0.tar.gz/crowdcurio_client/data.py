import datetime
import requests
import time

from crowdcurio_client.crowdcurio import CrowdCurioObject

class Data(CrowdCurioObject):
    _api_slug = 'data'
    _link_slug = 'data'
    _edit_attributes = (
        'slug',
        'name',
        'url',
        'content',
        {}
    )

    @classmethod
    def find(cls, id='', slug=None):
        if not id and not slug:
            return None
        return cls.where(id=id, slug=slug).next()

    def add(self, curio):
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "Data", "id": self.id, "attributes": {"content": self.content},"relationships": {"dataset":{"data":{"type":"Dataset","id":curio.id}}}}}
        )

    def remove(self, curio):
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "Data", "id": self.id, "attributes": {"content": self.content}, "relationships": {"dataset":{}}}}
        )

    def destroy(self):
        self.delete('{}'.format(self.id), json={'data': {'type':'Data', 'id': self.id}})

class DataSet(CrowdCurioObject):
    _api_slug = 'dataset'
    _link_slug = 'dataset'
    _edit_attributes = (
        'name',
        'is_active',
    )

    @classmethod
    def find(cls, id='', slug=None):
        if not id and not slug:
            return None
        return cls.where(id=id, slug=slug).next()

    def add(self, curio):
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "Dataset", "id": self.id, "relationships": {"curio":{"data":{"type":"Curio","id":curio.id}}}}}
        )

    def remove(self, curio):
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "Dataset", "id": self.id, "relationships": {"curio":{}}}}
        )

    def destroy(self):
        self.delete('{}'.format(self.id), json={'data': {'type':'Dataset', 'id': self.id}})


class DataRecord(CrowdCurioObject):
    _api_slug = 'datarecord'
    _link_slug = 'datarecord'
    _edit_attributes = (
        'seen',
        'order',
        'assigned',
    )

    @classmethod
    def find(cls, id='', slug=None):
        if not id and not slug:
            return None
        return cls.where(id=id, slug=slug).next()

    def add(self, task, data, experiment=None, condition=None):
        if experiment is None and condition is None:
            self.put(
                '{}'.format(self.id),
                json={"data": {"type": "Datarecord", "id": self.id, "relationships": {"task":{"data":{"type":"Task","id":task.id}},"data":{"data":{"type":"Data","id":data.id}}}}}
            )
        else:
            self.put(
                '{}'.format(self.id),
                json={"data": {"type": "Datarecord", "id": self.id, "relationships": {"task":{"data":{"type":"Task","id":task.id}},"data":{"data":{"type":"Data","id":data.id}},"experiment":{"data":{"type":"Experiment","id":experiment.id}},"condition":{"data":{"type":"Condition","id":condition.id}}}}}
            )

    def remove(self, task, data, experiment, condition):
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "Datarecord", "id": self.id, "relationships": {"task":{}, "data":{}, "experiment":{}, "condition":{}}}}
        )

    def destroy(self):
        self.delete('{}'.format(self.id), json={'data': {'type':'Datarecord', 'id': self.id}})