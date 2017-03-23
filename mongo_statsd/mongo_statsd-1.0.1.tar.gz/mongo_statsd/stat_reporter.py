# -*- coding: utf-8 -*-

"""
读取gateway统计数据，并上报数据至statsd
"""

from stat_reader import StatReader
from . import constants


class StatReporter(object):

    # 标识的名字
    name = None
    stat_reader = None
    statsd_client = None

    def __init__(self, statsd_client, name, host=None, port=None, username=None, password=None):
        """
        :param cmd: 命令
        :param statsd_client: statsd_client
        :param name: 名字
        :return:
        """

        cmd = constants.CMD_TPL
        if host is not None:
            cmd += ' -h %s' % host

        if port is not None:
            cmd += ' --port %s' % port

        if username is not None:
            cmd += ' -u %s' % username

        if password is not None:
            cmd += ' -p %s' % password

        self.stat_reader = StatReader(cmd, constants.HEADER_DICT.keys())
        self.statsd_client = statsd_client
        self.name = name

    def report(self):
        """
        上报
        :return:
        """

        result = self.stat_reader.read()

        if not result:
            return False

        for local_stat_name, local_value in result.items():
            header_config = constants.HEADER_DICT.get(local_stat_name)
            if not header_config:
                continue

            report_type = header_config[1]

            if report_type is None:
                continue

            value_trans_func = header_config[2]

            remote_value = value_trans_func(local_value)

            if not isinstance(remote_value, (tuple, list)):
                remote_stat_name = self.statsd_name_converter(local_stat_name)
                # 说明可以直接上报
                if report_type == 'i':
                    self.statsd_client.incr(remote_stat_name, remote_value)
                elif report_type == 'g':
                    self.statsd_client.gauge(remote_stat_name, remote_value)
            else:
                if '|' in local_stat_name:
                    sub_local_stat_name_list = local_stat_name.split('|')
                else:
                    sub_local_stat_name_list = ['%s_%s' % (local_stat_name, it) for it in len(remote_value)]

                # 说明直接拆分就好
                # 并且索引位置一致
                for idx, sub_local_stat_name in enumerate(sub_local_stat_name_list):
                    sub_remote_stat_name = self.statsd_name_converter(sub_local_stat_name)
                    if report_type == 'i':
                        self.statsd_client.incr(sub_remote_stat_name, remote_value[idx])
                    elif report_type == 'g':
                        self.statsd_client.gauge(sub_remote_stat_name, remote_value[idx])

        return True

    def statsd_name_converter(self, stat_name):
        return '%s.%s.%s' % (constants.PREFIX, self.name, stat_name)

