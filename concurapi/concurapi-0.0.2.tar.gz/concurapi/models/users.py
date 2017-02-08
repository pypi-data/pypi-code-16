from xml.etree.ElementTree import Element, SubElement, tostring
from collections import Iterable


class XMLMixin(object):
    def __init__(self, *args,**kwargs):
        for field in self.REQUIRED_FIELDS:
            assert field in kwargs
        self.attributes = {}
        self.attributes.update(kwargs)

    def to_xml_fragment(self):
        root = Element(self.ROOT_ELEMENT)
        for (k,v) in self.attributes.items():
            child = SubElement(root, k)
            child.text = v
        return root

    def to_xml(self):
        return str(tostring(self.to_xml_fragment(), encoding='utf8'))


class XMLBatchMixin(object):
    def __init__(self, user_profiles):
        assert isinstance(user_profiles, Iterable)
        for element in user_profiles:
            assert isinstance(element, self.USER_PROFILE_CLASS)
        self.profiles = user_profiles

    def to_xml_fragment(self):
        root = Element("UserBatch", xmlns="http://www.concursolutions.com/api/user/2011/02")
        for profile in self.profiles:
            root.append(profile.to_xml_fragment())
        return root

    def to_xml(self):
        return str(tostring(self.to_xml_fragment(), encoding='utf8'))


class UserProfile(XMLMixin):
    REQUIRED_FIELDS = ['EmpId', 'FeedRecordNumber', 'LoginId', 'Password']
    ROOT_ELEMENT = 'UserProfile'


class UserProfileBatch(XMLBatchMixin):
    USER_PROFILE_CLASS = UserProfile


class UserPasswordProfile(XMLMixin):
    REQUIRED_FIELDS = ['LoginID', 'Password']
    ROOT_ELEMENT = 'UserProfile'


class UserPasswordProfileBatch(XMLBatchMixin):
    USER_PROFILE_CLASS = UserPasswordProfile


def create_users(access_token=None, login_id=None):
    assert access_token is not None
    assert login_id is not None
