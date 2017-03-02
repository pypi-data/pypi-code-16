#!/usr/bin/env python
# -*- coding: utf-8 -*-

from autocompvar.base import Base

class HouseTypeCollection(Base):
    __attrs__ = []
    __keys__ = []

    def __init__(self):
        pass
        self._collection = list()

class HouseType(Base):
    __attrs__ = ['id', 'name']
    __keys__ = ['id', 'name']

    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name
        self._collection = list()


house_type_collection = HouseTypeCollection()

house_type_id_1 = HouseType(id=1, name='Single House')
house_type_collection.id____1 = house_type_id_1
house_type_collection.name____Single_House = house_type_id_1
house_type_collection._collection.append(house_type_id_1)

house_type_id_2 = HouseType(id=2, name='Condo')
house_type_collection.id____2 = house_type_id_2
house_type_collection.name____Condo = house_type_id_2
house_type_collection._collection.append(house_type_id_2)

house_type_id_3 = HouseType(id=3, name='Town House')
house_type_collection.id____3 = house_type_id_3
house_type_collection.name____Town_House = house_type_id_3
house_type_collection._collection.append(house_type_id_3)

house_type_id_4 = HouseType(id=4, name='Multi Family')
house_type_collection.id____4 = house_type_id_4
house_type_collection.name____Multi_Family = house_type_id_4
house_type_collection._collection.append(house_type_id_4)

house_type_id_5 = HouseType(id=5, name='Land')
house_type_collection.id____5 = house_type_id_5
house_type_collection.name____Land = house_type_id_5
house_type_collection._collection.append(house_type_id_5)

house_type_id_6 = HouseType(id=6, name='Other Type')
house_type_collection.id____6 = house_type_id_6
house_type_collection.name____Other_Type = house_type_id_6
house_type_collection._collection.append(house_type_id_6)