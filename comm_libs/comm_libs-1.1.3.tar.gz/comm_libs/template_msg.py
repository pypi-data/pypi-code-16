# coding:utf8
import json

import requests
from libs.log_tool import write_info_log


class TemplateMsg:
    __mq_url = "http://www.huifenqi.com/mq/sendtemplatemsg/"

    def __init__(self, template_id="", user_type=1):
        self.template_id = template_id
        self.user_type = user_type
        self.to_users = []
        self.properties = {}
        self.wx_properties = {}
        self.transmission = {}

    def set_template_id(self, template_id):
        """
        设置模板id
        :param template_id:
        :return:
        """
        self.template_id = template_id

    def set_to_users(self, to_users):
        """
        设置接收消息手机号,数组
        :param to_users:
        :return:
        """
        self.to_users = to_users

    def add_to_users(self, phone):
        """
        添加接收消息手机号,数组
        :param phone:
        :return:
        """
        self.to_users.append(phone)

    def set_user_type(self, user_type):
        """
        设置接受者用户类型 0：租客 1：经纪人
        :param to_users:
        :return:
        """
        self.user_type = user_type

    def set_transmission(self, transmission):
        """
        设置短信透传内容
        :param transmission:
        :return:
        """
        self.transmission = transmission

    def add_transmission_param(self, key, value):
        """
        添加透传 transmission 参数
        :param key:
        :param value:
        :return:
        """
        self.transmission[key] = value

    def set_properties(self, properties):
        """
        设置接受者用户类型 0：租客 1：经纪人
        :param to_users:
        :return:
        """
        self.properties = properties

    def add_properties_param(self, key, value):
        """
        添加 properties 参数
        :param key:
        :param value:
        :return:
        """
        self.properties[key] = value

    def add_wx_properties_param(self, key, value):
        """
        添加 properties 参数
        :param key:
        :param value:
        :return:
        """
        self.wx_properties[key] = value


    def send_mq(self):
        msg = {"msg": json.dumps({
            "template_id": self.template_id,
            "to_users": self.to_users,
            "user_type": self.user_type,
            "transmission": self.transmission,
            "properties": self.properties,
            "wx_properties": self.wx_properties,
        })}
        response = requests.post(self.__mq_url, msg)
        # print "send_template_msg[%s] response[%s]" % (msg, response.text)
        write_info_log("send_template_msg[%s] response[%s]" % (msg, response.text))


if __name__ == '__main__':
    # properties = {
    #     "first": "您好，您申请的分期未通过审核",
    #     "keyword1": "未通过",
    #     "keyword2": "信息录入错误需修改",
    #     "remark": "您的分期合同信息录入时出现错误，现经纪人已经帮您修改完成，请您再次确认!",
    #     "url": "http://www.huifenqi.com/c/scansinged/?cno=2016195222&phone=15652486096&platform=inner"
    # }
    template_msg = TemplateMsg('0001NMC14gy2KOe1B2a820160928171352', 0)
    template_msg.add_to_users(15311432059)

    template_msg.add_properties_param("k1", "1")
    template_msg.add_wx_properties_param("first", "本月还款提醒")
    template_msg.add_wx_properties_param("keyword1", "亲爱的会分期用户，10月1号是您的分期还款日，请在9月30号之前保证绑定的银行卡内余额充足，避免国庆期间因银行放假导致延迟到账或者扣款失败而产生逾期滞纳金，提前祝您国庆节快乐！")
    template_msg.add_wx_properties_param("keyword2", "每月1号")
    template_msg.add_wx_properties_param("keyword3", "2期")
    template_msg.add_properties_param("url", "http://www.huifenqi.com/wx/repayment/html/select.html")
    template_msg.send_mq()
