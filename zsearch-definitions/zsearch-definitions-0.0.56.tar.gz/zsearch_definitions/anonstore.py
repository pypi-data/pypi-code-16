import sys
import zsearch_definitions.anonstore_pb2

class CertificateSource(object):

    _by_pretty_name = {}
    _by_name = {}
    _by_value = {}

    def __init__(self, value, name, pretty_name):
        self.value, self.name, self.pretty_name = value, name, pretty_name

    @classmethod
    def from_value(cls, value):
        return cls._by_value[value]

    @classmethod
    def from_name(cls, name):
        return cls._by_name[name]

    @classmethod
    def from_pretty_name(cls, name):
        return cls._by_pretty_name[name]

    def __hash__(self):
        return self.value.__hash__()

    def __cmp__(self, other):
        return self.value.__cmp__(other.value)


for _spid in zsearch_definitions.anonstore_pb2.CertificateSource.values():
    enum_name = zsearch_definitions.anonstore_pb2.CertificateSource.Name(_spid)
    simple_name = enum_name[len("CERTIFICATE_SOURCE_"):]
    pretty_name = simple_name.lower()
    object_ = CertificateSource(_spid, enum_name, pretty_name)
    CertificateSource._by_name[enum_name] = object_
    CertificateSource._by_value[_spid] = object_
    CertificateSource._by_pretty_name[pretty_name] = object_
    setattr(CertificateSource, simple_name, object_)


class CTPushStatus(object):

    _by_pretty_name = {}
    _by_name = {}
    _by_value = {}

    def __init__(self, value, name, pretty_name):
        self.value, self.name, self.pretty_name = value, name, pretty_name

    @classmethod
    def from_value(cls, value):
        return cls._by_value[value]

    @classmethod
    def from_name(cls, name):
        return cls._by_name[name]

    @classmethod
    def from_pretty_name(cls, name):
        return cls._by_pretty_name[name]

    def __hash__(self):
        return self.value.__hash__()

    def __cmp__(self, other):
        return self.value.__cmp__(other.value)


for _spid in zsearch_definitions.anonstore_pb2.CTPushStatus.values():
    enum_name = zsearch_definitions.anonstore_pb2.CTPushStatus.Name(_spid)
    simple_name = enum_name[len("CT_PUSH_STATUS_"):]
    pretty_name = simple_name.lower()
    object_ = CTPushStatus(_spid, enum_name, pretty_name)
    CTPushStatus._by_name[enum_name] = object_
    CTPushStatus._by_value[_spid] = object_
    CTPushStatus._by_pretty_name[pretty_name] = object_
    setattr(CTPushStatus, simple_name, object_)

