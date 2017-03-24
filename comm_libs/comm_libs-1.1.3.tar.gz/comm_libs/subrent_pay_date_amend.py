# coding:utf8
import datetime

from db_models.tables.agency import Agency
from libs.log_tool import write_error_log

__author__ = 'zeqiang'


def amend_subrent_pay_date(subrent, agency_id):
    """
    修正打款时间
    :return:
    """
    pay_date = subrent.pay_date
    if not agency_id:
        agency_id = 10000
    write_error_log(agency_id)
    today = datetime.date.today()
    # today = datetime.date(2015, 11, 30)
    agency = Agency.objects.get(agencyid=agency_id)

    if agency.agency_type in [2, 3]:  # 中介或公寓延后1天打款
        pay_date = pay_date + datetime.timedelta(days=1)
    elif agency.agency_type == 1:  # 如果是C端，打款天数减1
        pay_date = pay_date + datetime.timedelta(days=-1)

    diff_month = pay_date.year * 12 + pay_date.month - (today.year * 12 + today.month)

    if agency.agency_type == 2 and pay_date.day <= 6 and diff_month > 0:  # 普通中介，提前打至下个月5号，含5号。
        pay_date = pay_date - datetime.timedelta(days=pay_date.day)
    elif agency_id in [1717, 1472] and diff_month > 0:  # 如果是天地昊和中润，打款时间为上月最后一天
        pay_date = pay_date - datetime.timedelta(days=pay_date.day)

    if today >= pay_date:
        if agency.agency_type in [2, 3]:
            pay_date = today + datetime.timedelta(days=1)
        else:
            pay_date = today

    subrent.pay_date = pay_date


def amend_subrent_pay_date_for_subrent_list(subrent_list, agency_id):
    """
    修正打款时间
    :return:
    """
    if len(subrent_list) > 0:
        if not agency_id:
            agency_id = 10000

        agency = Agency.objects.get(agencyid=agency_id)

        today = datetime.date.today()
        subrent = subrent_list[0]
        pay_date = datetime.datetime.strptime(subrent["pay_date"], "%Y-%m-%d").date()
        diff_month = pay_date.year * 12 + pay_date.month - (today.year * 12 + today.month)

        if agency.agency_type == 2 and pay_date.day <= 6 and diff_month > 0:  # 普通中介，提前打至下个月5号，含5号。
            pay_date = pay_date - datetime.timedelta(days=pay_date.day)
        elif agency_id in [1717, 1472, 1000000004] and diff_month > 0:  # 如果是天地昊和中润，打款时间为上月最后一天
            pay_date = pay_date - datetime.timedelta(days=pay_date.day)

        subrent["pay_date"] = datetime.datetime.strftime(pay_date, '%Y-%m-%d')

    return subrent_list
