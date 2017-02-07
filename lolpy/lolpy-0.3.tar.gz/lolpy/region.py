from enum import Enum


class Region(Enum):
    BR = ("br", "BR1")
    EUNE = ("eune", "EUN1")
    EUW = ("euw", "EUW1")
    JP = ("jp", "JP1")
    KR = ("kr", "KR")
    LAN = ("lan", "LA1")
    LAS = ("las", "LA2")
    NA = ("na", "NA1")
    OCE = ("oce", "OC1")
    TR = ("tr", "TR1")
    RU = ("ru", "RU")
    PBE = ("pbe", "PBE1")
    GLOBAL = ("global", "")

    def __init__(self, url, platform_id):
        self.url = url
        self.platform_id = platform_id

    @property
    def host_url(self):
        return "https://" + self.url + ".api.pvp.net/"
