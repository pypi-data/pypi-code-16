# coding:utf-8
# Copyright (C) Alibaba Group

"""
Check Points - a collection of defined check points.
"""
import math
import os
import re
import sys
import time
import edsd.hsf
from datetime import datetime

from edsd.envcmd import syscmd, get_server_datetime, test_http, test_socket, \
    tomcat_home, localhost_logpath, cai_server_host_port, resolve_name, \
    config_server_host_port, diamond_server_host, edas_agent_home, \
    notify_console_alive, dauth_diamond_host, get, hasconsumer, hasprovider, \
    agent_pid, tomcat_pid, deploy_dir, services_inside_runtime_info, \
    edas_agent_version, read_services_from_pandora

from edsd.common import isodt2ts
from edsd.facade import check, point
from edsd.err import report_fail, report_info
from . import __version__

__author__ = "Thomas Li <yanliang.lyl@alibaba-inc.com>"
__license__ = "GNU License"


@check(name=u"System Status", strict=False, category="basic")
class CheckSystemStatus(object):
    """系统相关的问题:
    1: 是否是linux CentOS 6.5
    2: Yum source.
    3: ulimit
    4: 内存 磁盘要求
    5: 基础组件要求 -> TSAR, STARAGENT, WPCLIENT
    """

    @point()
    def is_linux(self):
        """
    检测点:
        a) 确认此脚本运行在Linux系统下
        """
        if not sys.platform.startswith('linux'):
            report_fail(u"Linux only")

    @point()
    def is_platform_supported(self):
        """
        a) 目前EDAS仅支持CentOS和AliyunOS系统.
        """
        issue = syscmd('lsb_release -a')
        r = re.compile('(?:centos|aliyun)', re.IGNORECASE | re.MULTILINE)
        m = r.search(issue)
        if not m:
            report_fail(u"CentOS or AliyunOS is recommend, current: %s" % issue)

        report_info(issue)

    @point()
    def ulimit_info(self):
        """检测点:查看 ulimit -a 的信息"""

        v = syscmd('ulimit -a').strip()
        report_info(v.replace('\n', '<br>'))

    @point()
    def disk_info(self):
        """磁盘信息"""
        df = syscmd("df -h")
        report_info(df.replace('\n', '<br>'))

    @point()
    def mem_info(self):
        """内存信息"""
        df = syscmd("free -m")
        report_info(df.replace('\n', '<br>'))


# @check(name="check hsf service")
# class CheckHsfService(object):
#     def check(self, service_name): pass


@check(name="Network Status", category="basic,network")
class NetworkStatus(object):
    """网络状态汇报
    """

    @point()
    def is_taobao_connectable(self):
        """
    检测点:
        a) 尝试解析taobao.com的域名, 并尝试连接, 是否正确.
        """
        thost = resolve_name('www.taobao.com')
        if not thost:
            report_fail("taobao.com resolved failed.")

        if not test_socket(thost, 80):
            report_fail("socket connect failed against socket(%s, 80)" % thost)

    @point()
    def local_hosts_content(self):
        """执行并汇报 cat /etc/hosts 命令的信息"""
        report_info(syscmd('cat /etc/hosts'))

    @point()
    def resolved_hostname(self):
        """执行并汇报 hostname -i 命令的信息"""

        std, stderr = syscmd('hostname -i', readstd=True, readerr=True)
        if not stderr:
            report_info(std)

        report_fail(stderr)

    @point()
    def ifconfig(self):
        """执行并汇报 ifconfig 命令的信息"""
        report_info(syscmd("ifconfig | grep -B 1 'inet addr'"))

    @point()
    def listening_ports(self):
        """执行并汇报 netstat -lntp 命令的信息"""
        report_info(syscmd("netstat -lntp 2>/dev/null | awk '/^tcp/ {print $4, $5}'"))

    @point()
    def tcp_stat_statics(self):
        report_info(syscmd("netstat -ant |awk '/^tcp/ {++SN[$NF]} "
                           "END {for (i in SN) print i, SN[i]}'"))

    @point()
    def iptables(self):
        tables = ['filter', 'nat', 'mangle', 'raw']
        result = {}
        for t in tables:
            r = syscmd('iptables -n -L -t %s | '
                       'grep -v "^Chain\|^target\|^$"' % t)
            if not r.strip():
                continue

            result[t] = r.strip()

        report_info("iptables information.", data=result)


@check(name=u"Local Date Time", category="basic")
class CheckLocalDateTime(object):
    """本地时间是否与服务器时间一致
    """
    @point()
    def local_time_ok(self):
        """
    检测点:
        a) 本地时间与淘宝服务器时间前后相差不得超过1分钟.
        """
        stime = get_server_datetime('http://www.taobao.com/')
        ltime = time.time()
        max_allowed = 60  # max 1 minute

        if math.fabs(stime - ltime) < max_allowed:
            return

        report_fail("local date time is faraway from server time")


@check(name=u"Java Status", category="basic,java")
class CheckJavaHome(object):
    """目前Java只支持1.6与1.7"""

    @point()
    def only_support_java6or7(self):
        """
    检测点:
        a) 确认Java已经安装, 且 java -version 打印出来的版本为java7或者java8, 其他版本
           暂时没有经过测试, 不能获得官方支持.
        """
        jpath = syscmd('which java')
        if not jpath:
            report_fail("java is not found")

        jversion = syscmd("java -version 2>&1 | grep 'java version'")
        if '1.7' in jversion or '1.8' in jversion:
            return

        report_fail('Only java 6 and java 7 supported')

    @point()
    def jvms(self):
        """读取 JVM 的信息,包括 Agent 与 TOMCAT"""
        aid = agent_pid()
        if not aid:
            report_fail("EDAS Agent is not found.")

        tid = tomcat_pid()
        if not tid:
            report_fail("Tomcat pid is not found.")

        report_info("EDAS Agent PID: %s \n"
                    "Tomcat PID: %s " % (aid, tid))

    def is_pandora_started(self):
        """判断 Pandora 是否正常启动"""
        p = syscmd("netstat -lntp 2>/dev/null | grep 12201 |awk '{print $NF}'")
        if not p:
            report_fail("Pandora is not started")

        report_info("Pandora started as : %s" % p)


@check(name=u"Authentication", category="advanced,edas,dauth,hsf-precheck")
class CheckAuthentication(object):
    """确保鉴权成功"""

    @point()
    def verify_edas_aksk(self):
        """
    检测点:
        a) 读取 /home/admin/.spas_key/default 中的ak/sk, 然后向console发送 alive 命令
        读取其返回的response是否合法.
        """
        if notify_console_alive():
            return

        report_fail("edas ak/sk verify failed.")


@check(name=u"Agent Status", category="advanced,edas,agent,hsf-precheck")
class CheckAgentStatus():
    """确认Agent运行状态正常,需查看日志确保与Console的通信正常
    """
    @point()
    def is_edas_agent_installed(self):
        """
    检测点:
        a) 确认EDAS的安装目录(/home/admin/edas-agent)是否正确
        """
        edas_home = edas_agent_home()
        if not os.path.isdir(edas_home) or not \
                os.path.isfile('%s/bin/edas-agent' % edas_home):
            report_fail('EDAS Agent is not installed.')

        v = edas_agent_version(edas_home)
        if not v:
            report_fail('agent version not found.')

        configs = syscmd('cat ecs.conf ; cat agent.conf')

        report_info('EDAS AGENT VERSION: %s \n %s' % (v, configs))


    @point()
    def is_console_connectable(self):
        """
    检测点:
        a) 确认EDAS Console是否能连接成功, 确认域名(edas-internal.console.aliyun.com)
           是否能解析, 且http连接是否能成功.
        """
        url = 'http://edas-internal.console.aliyun.com/checkpreload.htm'
        internal_host = syscmd('getent hosts edas-internal.console.aliyun.com')
        if not test_http(url):
            report_fail('EDAS Console is not able to connect, resolved: %s'
                        % internal_host)

        internal_host = syscmd('getent hosts edas-internal.console.aliyun.com')
        report_info(internal_host)

    @point()
    def is_edas_agent_running(self):
        """
    检测点:
        a) 确认 EDAS Agent已经启动(通过 /home/admin/edas-agent/bin/startup.sh启动)
        """
        aid = agent_pid()
        if not aid:
            report_fail('Agent is not started')

    @point()
    def is_heartbeat_success(self):
        """
    检测点:
        a) 20秒之内, EDAS Agent有向Console发起的heartbeat.
        """
        import math
        last_hb_dt = syscmd("tail -n 30 %s/logs/agent.log | "
                            "grep 'ecu.heartbeat] INFO' | tail -n 1 | "
                            "awk '{print $1}'" % edas_agent_home())
        if not last_hb_dt:
            report_fail("Heart beat fail")

        scds = [3600, 60, 1]
        seconds = sum([a * b for a, b in \
                       zip(scds, map(int, last_hb_dt.split(':')))])

        if math.fabs(seconds - now_time_seconds()) < 30:
            return

        report_fail("Last heart beat time is faraway from now.")


def now_time_seconds():
    t = datetime.now().time()
    return t.hour * 3600 + t.minute * 60 + t.second


@check(name=u"EDAS Status", category="advanced,edas")
class CheckEdasContainer(object):
    """确保tomcat已经启动,且服务运行正常"""

    sts = None

    @point()
    def check_tomcat_pid(self):
        """
    检测点:
        a) AliTomcat已经启动, 并且是以admin用户运行
        """
        tpid = self.pid()
        if tpid:
            report_info('tomcat running as pid: %s' % tpid)

        report_fail("AliTomcat is not running.")

    def pid(self):
        from edsd.envcmd import tomcat_pid
        return tomcat_pid()


    @point()
    def catalina_out_ok(self):
        """
    检测点:
        a) 从AliTomcat的启动日志里, 从开始创建进程到正式启动(RUNNING)的时间不能超过1分钟.
        b) 确认启动时间之内没有异常产生.
        """
        startuptime = self.read_startuptime()

        self.sts = startuptime
        if not self.within_startup_timespan(startuptime):
            report_fail(
                "Catalina is not found started(startup duration too long)")

        fpath = self.log_path
        tpath = '/tmp/.catalina.exception.log'

        self.failed_if_haskeyword(fpath, tpath, 'Exception')

    def read_startuptime(self):
        fname = self.log_path

        if not os.path.isfile(fname):
            report_fail("Catalina stdout is not found.")

        startuptime = read_startup_timestamp(fname)
        if not startuptime:
            report_fail("Catalina is not found started in log file")

        return startuptime

    @property
    def log_path(self):
        pth = self.log_home

        if not pth:
            report_fail("Get catalina path log failed.")

        return '%s/catalina.out' % pth

    @property
    def log_home(self):
        return '%s/logs' % tomcat_home()

    @point()
    def spas_authentication_ok(self):
        """
    检测点:
        a) 查看AliTomcat的catalina.out日志,确保在启动前后的一分钟之内没有'authentication failed'出现
        """
        # self.catalina_out_ok()
        fpath = self.log_path
        tpath = '/tmp/.catalina_auth.exception.log'
        self.failed_if_haskeyword(fpath, tpath, 'authentication failed')

    @point()
    def localhost_log_ok(self):
        """
    检测点:
        a) 查看AliTomcat的localhost log,确认前后启动时间的1分钟之内没有异常产生
        """

        # ensure startup time read
        # self.catalina_out_ok()

        fromfile = localhost_logpath(self.log_home)
        tofile = '/tmp/.localhost.exception.log'
        self.failed_if_haskeyword(fromfile, tofile, 'Exception')

    def failed_if_haskeyword(self, fromfile, tofile, keyword):
        try:
            syscmd('egrep -C 3 -B 3 "%s" %s > %s' % (keyword, fromfile, tofile))

            if self.failed_in_startup(tofile):
                report_fail("'%s' found in '%s'" % (keyword, fromfile))

            return True
        finally:
            try:
                os.unlink(tofile)
            except:
                pass

    def failed_in_startup(self, lpath):
        sts = self.read_startuptime()

        rt = re.compile('\d{1,2}:\d{1,2}:\d{1,2}')
        f = file(lpath)
        for l in f.readlines():
            g = rt.search(l)
            if g is None:
                continue

            ts = isodt2ts(l[:g.end()])
            if self.within_startup_timespan(ts, start=sts):
                return True

        return False

    def within_startup_timespan(self, ts, start=None):
        """前后60秒为敏感区"""
        start = start or self.read_startuptime()
        return math.fabs(ts - start) < 60


def read_startup_timestamp(fname):
    f = file(fname)
    stp = ' org.apache.catalina.startup.Catalina start'
    line, found = None, False
    lines = reversed(f.readlines())
    for l in lines:
        if 'INFO: Server startup in' in l:
            found = True
            continue

        if found and stp in l:
            line = l
            break

    if not line:
        return None

    return isodt2ts(line[0:-len(stp)])


@check(name=u"Name Server Status", category="advanced,cai,hsf-precheck")
class CheckNameServer(object):
    '''Name Server(CAI/Diamond/CS)等服务访问正常
    '''

    @point()
    def is_address_server_connectable(self):
        """
    检测点:
        a) 从AliTomcat中读取地址服务器(address server) 的配置, 并尝试读取diamond server配置.
        """
        th = tomcat_home()
        if not th:
            report_fail("Tomcat is not deployed.")

        host, port = cai_server_host_port()
        ip = resolve_name(host)

        if not ip:
            report_fail("cai server host resolved failed.")

        diamond_url = 'http://%s:%s/diamond-server/diamond' % (host, port)
        hi = syscmd('getent hosts %s' % host)

        if test_http(diamond_url):
            report_info("%s with port %s connected ok." % (hi, port))

        report_fail("Cai server('%s') is not able to connect, resolved: %s" %
                    (diamond_url, hi))

    @point()
    def is_config_server_connectable(self):
        """
    检测点:
        a) Get a config server address from cai
        b) Test the socket connection.
        """
        h = config_server_host_port()
        if not h:
            report_fail("config server is not found.")

        host, port = h
        if test_socket(host, port):
            report_info('config server is connectable via: %s:%s' % (host, port))

        report_fail("socket connect to config server(%s, %s) is failed"
                    % (host, port))

    @point()
    def is_diamond_connectable(self):
        """
    检测点:
        a) Get a diamond server address from cai.
        b) Test the socket connection.
        """
        h = diamond_server_host()
        if not h:
            report_fail("diamond server is not found on address server.")

        if test_socket(h, 8080):
            report_info('diamond host is connected via: %s:8080' % h)

        report_fail("socket connect to diamond server(%s) failed." % h)

    @point()
    def is_dauth_diamond_connectable(self):
        """
    检测点:
        a) 从address server获取spas diamond地址.
        b) 从spas diamond地址获取spas spec的地址,并测试连接
        """
        h = dauth_diamond_host()
        if not h:
            report_fail("spas diamond is not found on address server")

        url = 'http://%s:8080/diamond-server/config.do?group=spas_info&' \
              'dataId=spas_authentication_url' % h

        spas_spec_link = get(url)
        if not spas_spec_link:
            report_fail("spas spec failed to fetch: %s" % url)

        if test_http(spas_spec_link, expected=405):
            m = re.compile('https?://([^/]+)(/.*)').search(spas_spec_link)
            host = m.group(1).split(':')[0]
            report_info('diamond server: %s' % syscmd('getent hosts %s' % host))
            return

        report_fail("spas spec link failed to connect: %s" % spas_spec_link)


@check(name=u"HSF Status", category="advanced,hsf,hsf-services")
class CheckHsfStatus(object):
    """确保HSF服务注册/发布成功"""

    hasconsumer = property(hasconsumer)
    hasprovider = property(hasprovider)

    # @point()
    def hsf_service_status(self):
        """
    检测点:
        a) 先确认检查此服务是服务提供者还是服务调用者.
        b) 检查hsf服务的日志,是否注册成功或者发布
        c) 如果是consumer, 查询改服务是否存在于snapshots中.
        """
        has = self.hasprovider or self.hasconsumer
        if not has:
            report_fail(u"没有发现有HSF的provider或consumer")

        edsd.hsf.HSFactory.instance().check()

    @point()
    def hsf_services(self):
        th = tomcat_home()
        dir = deploy_dir(home=th)
        if not dir:
            report_fail("Application not deployed.")

        hsf = edsd.hsf.HSFactory.instance(dir)
        # xml配置解析
        xmlconsumers = [str(c) for c in hsf.consumers]
        xmlproviders = [str(p) for p in hsf.providers]

        # pandora中获取的服务名和分组
        lsconsumers, lsproviders = read_services_from_pandora()
        lsconsumers.update(xmlconsumers)
        lsproviders.update(xmlproviders)

        # RuntimeInfo中获取的provider和consumer
        rconsumers, rproviders = services_inside_runtime_info(th)
        lsconsumers.update(rconsumers)
        lsproviders.update(rproviders)

        lsconsumers, lsproviders = filter(bool, lsconsumers), \
                                   filter(bool, lsproviders)
        report_info("xml defined consumers count: %d, providers count: %d" %
                    (len(lsconsumers),
                     len(lsproviders)),
            data=dict(consumers={'xml': lsconsumers},
                      providers={'xml': lsproviders}))

def install():
    pass