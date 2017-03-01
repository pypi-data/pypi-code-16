from fdscli.model.base_model import BaseModel
import re

class Zone(BaseModel):
    '''
    Created on Sep 8, 2016

    @author: chaithra, Neil
    '''

    def __init__(self, zid=-1, name=None, ztype=None, zvip=0, iface=None, **kwargs):
        BaseModel.__init__(self, zid, name)
        self.zid = zid
        self.ztype = ztype
        self.name = name
        self.state = 0
        self.zvip = zvip
        self.iface = iface
        self.amList = []
        for key in kwargs:
            if re.search("am[0-9]+", key):
                amList.append(kwargs[key])

    @property
    def zone_id(self):
        return self.__zid

    @zone_id.setter
    def zone_id(self, zid):
        self.__zid = zid

    @property
    def zone_type(self):
        return self.__ztype

    @zone_type.setter
    def zone_type(self, ztype):
        self.__ztype = ztype

    @property
    def zone_name(self):
        return self.__zone_name

    @zone_name.setter
    def zone_name(self, name):
        self.__zone_name = name

    @property
    def zone_state(self):
        return self.__zone_state

    @zone_state.setter
    def zone_state(self, state):
        self.__zone_state = state

    @property
    def zone_vip(self):
        return self.__zone_vip

    @zone_vip.setter
    def zone_vip(self, zvip):
        self.__zone_vip = zvip

    @property
    def zone_iface(self):
        return self.__zone_iface

    @zone_iface.setter
    def zone_iface(self, iface):
        self.__zone_iface = iface

    @property
    def zone_amList(self):
        return self.__zone_amList

    @zone_amList.setter
    def amList(self, amList):
        self.__zone_amList = amList
