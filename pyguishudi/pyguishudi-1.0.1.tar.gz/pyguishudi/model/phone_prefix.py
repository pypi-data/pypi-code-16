# -*- coding:utf-8 -*-

class PhonePrefix(object):

    PHONE_PREFIX = {
        #移动
        '10086': ['134', '135', '136', '137', '138', '139', '140', '150', '151', '152', '157', '158', '159', '182', '183', '184', '187', '178', '188', '147', '1705'],
        #联通
        '10010': ['130', '131', '132', '145', '155', '156', '171','175', '176', '185', '186', '1709'],
        #电信
        '10000': ['133', '142', '144', '146', '148', '149', '153', '177', '180', '181', '189', '1349', '1700', '173'],
    }

    @classmethod
    def search(cls, phone):
        """ 根据手机号，获得手机归属
        """
        phone_type = 'unknown'
        phone = str(phone)
        if len(phone) != 11:
            return phone_type
        if not phone.isdigit():
            return phone_type
        for prefix in cls.PHONE_PREFIX:
            # 识别 3位 或者 4位
            if phone[:3] in cls.PHONE_PREFIX[prefix] or phone[:4] in cls.PHONE_PREFIX[prefix]:
                return prefix
        return phone_type