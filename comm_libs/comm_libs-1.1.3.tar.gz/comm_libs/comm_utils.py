# coding:utf-8
from time import gmtime

from libs import sendmail
from libs.log_tool import write_error_log
from project.confs import MAIL_SERVER, SENDER_USER, SENDER_PASSWORD

try:
    from huizhaofang import settings
except:
    from project import settings


def is_test_env():
    try:
        return settings.TESTENV
    except:
        return False


def check_user_id_no(id_str):
    """
    copy from xiaochun's script
    检查身份证号是否合法
    """
    try:
        weight_num = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        tail_char = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

        id_len = len(id_str)

        if id_len != 15 and id_len != 18:
            return False

        sum_num = 0
        for p in zip([int(i) for i in id_str[:-1]], weight_num):
            sum_num += p[0] * p[1]

        if tail_char[sum_num % 11] != id_str[-1]:
            return False
    except Exception, e:
        return False
    return True


def get_age(y, m, d):
    """
    根据时间得到年龄
    :param y:
    :param m:
    :param d:
    :return:
    """
    # get the current time in tuple format
    a = gmtime()
    # difference in day
    dd = a[2] - d
    # difference in month
    dm = a[1] - m
    # difference in year
    dy = a[0] - y
    # checks if difference in day is negative
    if dd < 0:
        dd = dd + 30
        dm = dm - 1
        # checks if difference in month is negative when difference in day is also negative
        if dm < 0:
            dm = dm + 12
            dy = dy - 1
    # checks if difference in month is negative when difference in day is positive
    if dm < 0:
        dm = dm + 12
        dy = dy - 1
    return (dy, dm, dd)


def get_ip_address(request):
    """
    获取ip地址
    :param request:
    :return:
    """
    ip = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if not ip:
        ip = request.META.get('REMOTE_ADDR', "")
    return ip


def get_http_referer(request):
    """
    获取referer
    :param request:
    :return:
    """
    return request.META.get("HTTP_REFERER", "")


def send_mail_notify(receiver_list, title, content):
    """
    发送通知邮件
    :param receiver_list:
    :param title:
    :param content:
    :return:
    """
    title = "【CRM】" + title
    try:
        mail_client = sendmail.MailSender(MAIL_SERVER, SENDER_USER, SENDER_PASSWORD, 25)
        mail_client.set_subject(u"%s" % title)
        mail_client.add_content(content, "utf8")
        mail_client.set_sender(SENDER_USER)
        mail_client.set_receiver(receiver_list)
        mail_client.sendmail()
    except:
        write_error_log("%s邮件发送失败" % title)
