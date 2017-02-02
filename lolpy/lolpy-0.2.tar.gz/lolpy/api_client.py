

import json
import re
import requests
import time
from .region import Region


class APIClient:

    version_champion = "v1.2"
    version_game = "v1.3"
    version_summoner = "v1.4"
    version_stats = "v1.3"

    def __init__(self, string="", region=Region.NA):
        assert type(string) == str, "Argument must be str"
        self.apiKey = string
        self.region = region
        self.tenSecCalls = 0
        self.tenMinCalls = 0

    def assert_key_defined(self):
        assert self.apiKey != "", "The api key is not defined"
        return True

    def api_key_url_string(self):
        self.assert_key_defined()
        return "api_key=" + self.apiKey

    @staticmethod
    def format_parameter(name, value):
        assert type(name) == str, "Parameter Name must be a string"
        return name + "=" + str(value).lower()

    def host_url(self):
        return "https://" + self.region.host + "/"

    def _call_api(self, api_url):
        response = requests.get(self.host_url() + api_url)
        if response.status_code == requests.codes.too_many_requests:
            time.sleep(int(response.headers.get('Retry-After', 0)))
            return self._call_api(api_url)
        else:
            response.raise_for_status()
            return response

    @staticmethod
    def validate_summoner_name(summoner_name):
        assert re.match(r"^[\w _.]+$", summoner_name, re.UNICODE) is not None, \
            "Invalid Summoner Name: " + summoner_name
        return True

    # champion v1.2
    def champion_list(self, free_to_play=False):
        api_url = "api/lol/" + str(
            self.region.url) + "/" + self.version_champion + "/champion?" + self.format_parameter(
            "freeToPlay", free_to_play) \
                  + "&" + self.api_key_url_string()
        response = self._call_api(api_url)
        return json.loads(response.content.decode('utf-8'))

    def champion_by_id(self, champion_id):
        api_url = "api/lol/" + str(self.region.url) + "/" + self.version_champion + "/champion/" + str(champion_id) \
                  + "?" + self.api_key_url_string()
        response = self._call_api(api_url)
        return json.loads(response.content.decode('utf-8'))

    # game v1.3
    def recent_game_by_id(self, summoner_id):
        api_url = "api/lol/" + str(self.region.url) + "" + self.version_game + "/game/by-summoner/" + \
                  str(summoner_id) + "/recent?" + self.api_key_url_string()
        response = self._call_api(api_url)
        return json.loads(response.content.decode('utf-8'))

    # summoner v1.4
    def summoner_profile_by_name(self, summoner_name):
        if type(summoner_name) == list:
            summoner_name = ','.join(
                requests.utils.quote(str(x)) for x in summoner_name if self.validate_summoner_name(x))
        elif self.validate_summoner_name(summoner_name):
            summoner_name = requests.utils.quote(str(summoner_name))
        api_url = "/api/lol/" + str(self.region.url) + "/" + self.version_summoner + "/summoner/by-name/" \
            + summoner_name + "?" + self.api_key_url_string()
        response = self._call_api(api_url)
        return json.loads(response.content.decode('utf-8'))

    def summoner_profile_by_id(self, summoner_id):
        if type(summoner_id) == list:
            summoner_id = ','.join(requests.utils.quote(str(x)) for x in summoner_id)
        else:
            summoner_id = requests.utils.quote(str(summoner_id))
        api_url = "/api/lol/" + str(self.region.url) + "/" + self.version_summoner + "/summoner/" \
            + str(summoner_id) + "?" + self.api_key_url_string()
        response = self._call_api(api_url)
        return json.loads(response.content.decode('utf-8'))

    def summoner_name_by_id(self, summoner_id):
        if type(summoner_id) == list:
            summoner_id = ','.join(requests.utils.quote(str(x)) for x in summoner_id if self.validate_summoner_name(x))
        else:
            summoner_id = requests.utils.quote(str(summoner_id))
        api_url = "/api/lol/" + str(self.region.url) + "/" + self.version_summoner + "/summoner/" \
            + str(summoner_id) + "/name?" + self.api_key_url_string()
        response = self._call_api(api_url)
        return json.loads(response.content.decode('utf-8'))

    def masteries_by_id(self, summoner_id):
        if type(summoner_id) == list:
            summoner_id = ','.join(requests.utils.quote(str(x)) for x in summoner_id)
        else:
            summoner_id = requests.utils.quote(str(summoner_id))
        api_url = "api/lol/" + str(self.region.url) + "/" + self.version_summoner + "/summoner/" + \
            summoner_id + "/masteries?" + self.api_key_url_string()
        response = self._call_api(api_url)
        return json.loads(response.content.decode('utf-8'))

    def runes_by_id(self, summoner_id):
        if type(summoner_id) == list:
            summoner_id = ','.join(requests.utils.quote(str(x)) for x in summoner_id)
        else:
            summoner_id = requests.utils.quote(str(summoner_id))
        api_url = "api/lol/" + str(self.region.url) + "/" + self.version_summoner + "/summoner/" + \
            summoner_id + "/runes?" + self.api_key_url_string()
        response = self._call_api(api_url)
        return json.loads(response.content.decode('utf-8'))

    # stats v1.3
    def ranked_stats_by_id(self, summoner_id):
        api_url = "api/lol/" + str(self.region.url) + "/" + self.version_stats + "/stats/by-summoner/" + \
                  str(summoner_id) + "/ranked?" + self.api_key_url_string()
        response = self._call_api(api_url)
        return json.loads(response.content.decode('utf-8'))

    def stats_summary_by_id(self, summoner_id):
        api_url = "api/lol/" + str(self.region.url) + "" + self.version_stats + "/stats/by-summoner/" + \
                  str(summoner_id) + "/summary?" + self.api_key_url_string()
        response = self._call_api(api_url)
        return json.loads(response.content.decode('utf-8'))
