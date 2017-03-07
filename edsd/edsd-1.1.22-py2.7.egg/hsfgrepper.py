# coding:utf-8
# Copyright (C) Alibaba Group

"""
edas-detector.hsfgrepper : 
"""

__author__ = "Thomas Li <yanliang.lyl@alibaba-inc.com>"
__license__ = "GNU License"

import json, re
import edsd.hsf

from . import __version__
from .envcmd import deploy_dir, services_inside_runtime_info, syscmd, \
    test_socket, read_services_from_pandora, tomcat_params, edas_agent_home, \
    tomcat_pid, read_setenv_info, parse_from_cmdline
from edsd.err import report_fail
from edsd.hsf.parser import Consumer, Provider
from edsd.common import Result, DefaultEncoder


check_sequence = []


def add_report(msg, success=True):
    d = dict(message=msg)
    d['success'] = success

    check_sequence.append(d)


def ping(service_name, consumer=True):

    try:
        (consumer_ping if consumer else provider_ping)(service_name)
    except Exception as e:
        add_report(e.message, success=False)

    success = all([d.get('success', True) for d in check_sequence])
    result = Result(success=success, data=check_sequence)

    print DefaultEncoder.instance().encode(result)


def provider_ping(service_name):
    if not service_name:
        report_fail("service name is empty.")

    try:
        hsf = Provider.from_string(service_name)
    except Exception as e:
        report_fail("service_name must consist of: 'interface:version:group'")

    d = deploy_dir()

    add_report('Grepping providers inside xml files...')

    hsf_factory = edsd.hsf.HSFactory.instance(d)

    matcher = lambda x: x.interface == hsf.interface
    providers = filter(matcher, hsf_factory.providers)

    # 与pandora比对
    _, lsproviders = read_services_from_pandora()
    if len(providers) == 0 and service_name not in lsproviders:
        report_fail("provider not configured")

    add_report('found %d configured hsf(s) has same interface.'
               % len(providers))

    strict_matcher = lambda x: \
        x.interface == hsf.interface and \
        x.group == hsf.group and \
        x.version == hsf.version

    providers = filter(strict_matcher, providers)

    if len(providers) == 0:
        report_fail("provider not found after strict matching")

    add_report('found %d configured hsf(s) after strict matching.'
               % len(providers))

    _, rproviders = services_inside_runtime_info()
    rproviders = map(Provider.from_string, rproviders)

    add_report('Searching services inside runtime log...')
    rproviders = filter(matcher, rproviders)

    if len(rproviders) == 0:
        report_fail("providers not configured inside runtime log")

    add_report('found %d configured hsf(s) has same interface '
               'inside runtime log.' % len(rproviders))

    rconsumers = filter(strict_matcher, rproviders)
    if len(rconsumers) == 0:
        report_fail(
            "providers not found inside runtime log after strict matching")

    add_report('Check pandora is started')
    p = syscmd('netstat -lntp 2>/dev/null | grep 12201')
    if not p:
        report_fail("Pandora is not started")

    add_report('Pandora started Ok.')


def consumer_ping(service_name):
    if not service_name:
        report_fail("service name is empty.")

    try:
        hsf = Consumer.from_string(service_name)
    except Exception as e:
        report_fail("service_name must consist of: 'interface:version:group'")

    d = deploy_dir()

    add_report('Grepping consumers inside xml files...')

    hsf_factory = edsd.hsf.HSFactory.instance(d)

    matcher = lambda x: x.interface == hsf.interface
    consumers = filter(matcher, hsf_factory.consumers)

    lsconsumers, _ = read_services_from_pandora()
    if len(consumers) == 0 and service_name not in lsconsumers:
        report_fail("cusumer not configured")

    add_report('found %d configured hsf(s) has same interface.'
               % len(consumers))

    strict_matcher = lambda x: \
        x.interface == hsf.interface and \
        x.group == hsf.group and \
        x.version == hsf.version

    consumers = filter(strict_matcher, consumers)

    if len(consumers) == 0:
        report_fail("cusumer not found after strict matching")

    add_report('found %d configured hsf(s) after strict matching.'
               % len(consumers))

    rconsumers, _ = services_inside_runtime_info()
    rconsumers = map(Consumer.from_string, rconsumers)

    add_report('Searching services inside runtime log...')
    rconsumers = filter(matcher, rconsumers)

    if len(rconsumers) == 0:
        report_fail("cusumer not configured inside runtime log")

    add_report('found %d configured hsf(s) has same interface '
               'inside runtime log.' % len(rconsumers))

    rconsumers = filter(strict_matcher, rconsumers)
    if len(rconsumers) == 0:
        report_fail("cusumer not found inside runtime log after strict matching")

    add_report('Check pandora is started')
    p = syscmd('netstat -lntp 2>/dev/null | grep 12201')
    if not p:
        report_fail("Pandora is not started")

    c = syscmd('curl -v  http://localhost:12201/hsf/ls?k=%s:%s 2> /dev/null '
               '| grep %s' % (hsf.interface, hsf.version, hsf.group))
    if not c:
        report_fail("Pandora is not found registered service.")

    data = syscmd('F=%s; test -f $F && cat $F' % hsf.snapshot_path())
    if not data:
        report_fail("Snapshot data inside configclient is empty.")

    add_report('snapshot data: %s' % data)
    try:
        addresses = json.loads(data)
    except:
        report_fail("json parsed failed with snapshot data")

    for ip in addresses:
        ping_address(ip)

    # call hsf-check
    add_report('Execute service call...')
    call_service(service_name)


    add_report('consumer done with sanity check.')

R = re.compile('^([^:]+):([^\?]+)\?.*')


def ping_address(address):
    m = R.search(address)
    if not m:
        report_fail("address info not found in string: '%s'." % address)

    host, port = str(m.group(1)), str(m.group(2))

    if not test_socket(host, port):
        add_report('%s:%s connect failed' % (host, port), success=False)
        return

    add_report('%s:%s connected ok' % (host, port))

def call_service(service_name):
    tpid = tomcat_pid()

    # get care params
    envinfo = read_setenv_info()
    tenant = envinfo['tenant.id']
    spas = envinfo['spas.identity']
    as_domain = envinfo['address.server.domain']
    as_port = envinfo['address.server.port']
    cs_port = envinfo['configserver.client.port']

    catalina_home = parse_from_cmdline(tpid)
    pandora = catalina_home + '/deploy/taobao-hsf.sar'

    agent_home = edas_agent_home()
    agent_tool_dir = agent_home + '/.edsd'
    # exec call
    syscmd('java -jar -Dtenant.id=%s'
           ' -Dspas.identity=%s'
           ' -Daddress.server.domain=%s'
           ' -Daddress.server.port=%s'
           ' -Dconfigserver.client.port=%s'
           ' -Dpandora.location=%s'
           ' %s/hsf-check.jar %s &>/dev/null' % (tenant, spas, as_domain, as_port, cs_port, pandora,
                       agent_tool_dir, service_name))

    # parse_result
    data = syscmd('cat %s/hsfcheck.log' % agent_tool_dir)

    if data is None:
        report_fail("call Fail, cause: No hsf-check result")

    try:
        check_infos = json.loads(data)
    except:
        report_fail("json parsed failed with hsf-check data")

    for chkinf in check_infos:
        service = chkinf['service']
        status = chkinf['status']
        msg = chkinf['msg']
        if status:
            add_report('%s call Success' % service)
        else:
            report_fail("%s call Fail, cause: %s" % (service, msg))
    return




