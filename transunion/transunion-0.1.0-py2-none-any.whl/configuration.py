from settings import PROD_URL, STAGE_URL


class Configuration(object):
    def __init__(self, username, password, industry_code, member_code,
                 prefix_code, sub_password, prod=False):
        self.username = username
        self.password = password
        self.industry_code = industry_code
        self.member_code = member_code
        self.prefix_code = prefix_code
        self.sub_password = sub_password
        self.api_url = PROD_URL if prod else STAGE_URL
