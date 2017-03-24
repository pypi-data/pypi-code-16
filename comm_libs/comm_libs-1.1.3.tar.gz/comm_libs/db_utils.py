# coding=utf8
from django.db import connection
from libs.log_tool import write_info_log


def execute_sql(sql):
    """直接执行sql语句

    :param sql:
    :return:
    """

    cursor = connection.cursor()
    write_info_log(sql)
    cursor.execute(sql)
    return cursor
