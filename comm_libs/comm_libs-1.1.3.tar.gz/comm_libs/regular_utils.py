# coding:utf8
import re
import sys

reload(sys)
sys.setdefaultencoding("utf-8")
# 业务配置
REGULAR_MATCH = {
    "user_name": ur'^[\u4E00-\u9FA5\uf900-\ufa2d\·]+$',
    "user_mobile": ur'^1[34578]\d{9}$',
    "community_name": ur'^[\u4E00-\u9FA5\uf900-\ufa2d\#\-\－\_\–\*\#\(\)\＃\—\＊\（\）\w]+$',
    "house_number": ur'^[\u4E00-\u9FA5\uf900-\ufa2d\#\-\－\_\–\*\#\(\)\＃\—\＊\（\）\w]+$',
    "room_number": ur'^[\u4E00-\u9FA5\uf900-\ufa2d\#\-\－\_\–\*\#\(\)\,\＃\—\＊\（\）\，\w]+$',
    "monthly_amount": ur'^[1-9]+(\d)*$',
    "broker_uniq_id": ur'^[\u4E00-\u9FA5\uf900-\ufa2d\#\-\－\_\–\*\#\(\)\＃\—\＊\（\）\s\w]+$',
    "owner_name": ur'^[\u4E00-\u9FA5\uf900-\ufa2d\·]+$',
    "owner_phone": ur'^1[34578]\d{9}$',
    "owner_bank_account": ur'^[\u4E00-\u9FA5\uf900-\ufa2d\·]+$',
    "owner_bank": ur'^[\u4E00-\u9FA5\uf900-\ufa2d]+$',
    "owner_card_no": ur'^\d{16,20}$'
}

def regular_match_params(regular_rule, param):
    """
    正则校验
    :param regular_rule:
    :param param:
    :return:
    """
    pattern = re.compile(regular_rule)
    # 使用Pattern匹配文本，获得匹配结果，无法匹配时将返回None
    match_remark = pattern.match(param)
    return match_remark