# coding:utf-8
# Copyright (C) Alibaba Group

"""
edas-detector.parser : Parse hsf xml files to get consumer and provider
"""


import os
import re
import shutil

import edsd.envcmd
import edsd.common
import edsd.logpeeker
import edsd.err

from xml.etree import ElementTree
from edsd import __version__, DEBUG

__license__ = "GNU License"
__author__ = "Thomas Li <yanliang.lyl@alibaba-inc.com>"


beans_schema = 'http://www.springframework.org/schema/beans'


class HSF(object):
    """Represents an HSF object inside xml definitions.
    """
    id = None
    interface = None
    group = None
    version = "1.0.0"

    def __init__(self, _id, interface, group, version='1.0.0'):
        self.id = _id
        self.interface = interface
        self.group = group
        self.version = version

    def check(self): pass

    def collect(self, path): pass

    def snapshot_path(self):
        return '/home/admin/configclient/snapshot/DEFAULT_ENV/%s:%s/%s*.dat' % \
               (self.interface, self.version, self.group)

    @classmethod
    def parsed_from_xml(cls, xml):
        """An mapper method, parsed an xml dom into an HSF Object, details should
        see the implementations.
        """
        raise "Not Supported"

    def __str__(self):
        return '%s:%s:%s' % (self.interface, self.version, self.group)

    @classmethod
    def parse_from_xml_with_beans(cls, bean_xml):
        props = bean_xml.findall('{%s}property' % beans_schema)
        if not props:
            return None

        props = dict([(x.get('name'), value(x)) for x in props])

        return cls(bean_xml.get('id'),
                   interface=props.get('interfaceName'),
                   group=props.get('group'),
                   version=props.get('version'))


    @classmethod
    def from_string(clz, service_name):
        ss = service_name.split(':')

        l = len(ss)
        if l == 1 or l > 3:
            raise Exception('invalid service name')
        if l == 2:
            return clz('', *ss)

        c = clz('', ss[0], ss[2])
        c.version = ss[1]

        return c


def value(p):
    """Grep value from a constructured xml payload.
    """
    v = p.get('value')
    if v:
        return v.strip()

    v = p.findall('{%s}value' % beans_schema)
    if v:
        return v[0].text.strip()

    return None


class Consumer(HSF):
    """An HSF Provider object defined inside xml."""

    def __init__(self, _id, interface, group, version='1.0.0'):
        super(Consumer, self).__init__(_id, interface, group, version)
        self.ok_pattern = re.compile('\[Register-ok\].*?%s' % self.interface)

    def check(self):
        with open(HSFactory.instance().cc_logpath) as f:
            for l in f.xreadlines():
                if self.ok_pattern.search(l):
                    return

        edsd.err.report_fail("subscriber '%s' registered failed." % self.interface)

    def collect(self, path):
        sp = edsd.envcmd.configclient_snapshot_path()
        if sp is None:
            return

        srcs = [os.path.join(sp, x, '%s.dat' % self.group)
                for x in os.listdir(sp) if self.interface in x]

        if len(srcs) == 0:
            return

        dst = '%s/configclient/%s/' % (path, self.interface)
        edsd.common.ensure_dir(dst)

        for src in srcs:
            if not os.path.isfile(src):
                continue
            shutil.copy(src, dst)

    @classmethod
    def parsed_from_xml(cls, xml):
        if xml is None:
            return

        return Consumer(xml.get('id'),
                        xml.get('interface'),
                        xml.get('group'))

    def __eq__(self, other):
        if other is None or not isinstance(other, Provider):
            return False

        return self.interface == other.interface \
               and self.group == other.group


class Provider(HSF):

    def __init__(self, _id, interface, group, version='1.0.0'):
        super(Provider, self).__init__(_id, interface, group, version)
        self.ok_pattern = re.compile('\[Publish-ok\].*?%s' % self.interface)

    def check(self):
        with open(HSFactory.instance().cc_logpath) as f:
            for l in f.xreadlines():
                if self.ok_pattern.search(l):
                    return
        edsd.err.report_fail("service '%s' publish failed." % self.interface)

    def collect(self, path):
        src = HSFactory.instance().cc_logpath
        shutil.copy(src, path)

    @classmethod
    def parsed_from_xml(cls, xml):
        if xml is None:
            return

        return Provider(xml.get('id'),
                        xml.get('interface'),
                        xml.get('group'),
                        xml.get('version'))

    @classmethod
    def parse_from_xml_with_beans(cls, bean_xml):
        props = bean_xml.findall('{%s}property' % beans_schema)
        if not props:
            return None

        props = dict([(x.get('name'), value(x)) for x in props])

        return cls(bean_xml.get('id'),
                   interface=props.get('serviceInterface'),
                   group=props.get('group'),
                   version=props.get('serviceVersion'))

    def __eq__(self, other):
        if other is None or not isinstance(other, Consumer):
            return False

        return self.interface == other.interface \
               and self.version == other.version \
               and self.group == other.group


class HSFactory(object):
    """An HSF Factory class for loading and parsing HSF object based on the
    configured xml files.
    """

    _consumers = set()
    _providers = set()

    consumers = property(lambda self: HSFactory._consumers)
    providers = property(lambda self: HSFactory._providers)

    # config client log path.
    _cc_logpath = None

    @property
    def cc_logpath(self):
        if self._cc_logpath is not None:
            return self._cc_logpath

        created = edsd.envcmd.tomcat_process_createtime()
        log_path = edsd.envcmd.configclient_logpath()

        if log_path is None:
            edsd.err.report_fail('Config client log path is not found')

        self._cc_logpath = edsd.logpeeker.move_patial_log(
            log_path, created)

        return self._cc_logpath

    @classmethod
    def instance(cls, dir):
        inst = getattr(cls, '_instance', None)
        if inst:
            return inst

        inst = HSFactory()
        if not cls._consumers and not cls._providers:
            cls.parse_hsf_object(dir)

        setattr(cls, '_instance', inst)
        return inst

    @classmethod
    def parse_hsf_object(cls, dir):
        providerfiles = edsd.envcmd.providerxml_files(dir)
        consumerfiles = edsd.envcmd.consumerxml_files(dir)

        parsed = providerfiles + consumerfiles
        for f in set(parsed):
            cls.feed_file(f)

    def check(self):
        for p in self.providers:
            p.check()

        for c in self.consumers:
            c.check()

    def collect(self, path):
        clc_path = edsd.envcmd.collect_path()
        path = os.path.join(path, clc_path)
        edsd.common.ensure_dir(path)

        for p in self.providers:
            p.collect(path)

        for c in self.consumers:
            c.collect(path)

    @classmethod
    def feed_file(cls, f):
        if not os.path.isfile((f)):
            return

        try:
            xml = ElementTree.parse(f)
            root = xml.getroot()

            cls.parse_hsfns_services(root)
            cls.parse_beanns_services(root)
        except Exception as _:
            if DEBUG:
                import traceback
                traceback.print_exc()

    @classmethod
    def parse_hsfns_services(cls, root):
        consumers = root.findall('{http://www.taobao.com/hsf}consumer')
        providers = root.findall('{http://www.taobao.com/hsf}provider')

        consumers = filter(bool, map(Consumer.parsed_from_xml, consumers))
        providers = filter(bool, map(Provider.parsed_from_xml, providers))

        cls._providers.update(providers)
        cls._consumers.update(consumers)

    @classmethod
    def parse_beanns_services(cls, root):
        beans = root.findall('{%s}bean' % beans_schema)

        providers = filter(
            lambda b:'com.taobao.hsf.app.spring.util.HSFSpringProviderBean'
                     == b.get('class'),
            beans)
        consumers = filter(
            lambda b:'com.taobao.hsf.app.spring.util.HSFSpringConsumerBean'
                     == b.get('class'),
            beans)

        consumers = filter(bool, map(Consumer.parse_from_xml_with_beans,
                                     consumers))
        providers = filter(bool, map(Provider.parse_from_xml_with_beans,
                                     providers))

        cls._providers.update(providers)
        cls._consumers.update(consumers)

