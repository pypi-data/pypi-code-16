import json
import re
import requests
import time
from .region import Region
from .queue_type import QueueType


class APIClient:
    @staticmethod
    def assert_queue_for_league(queue_type):
        assert type(queue_type) is QueueType, "Parameter must be a QueueType"
        valid_types = [QueueType.RANKED_FLEX_SR,
                       QueueType.RANKED_FLEX_TT,
                       QueueType.RANKED_SOLO_5x5,
                       QueueType.RANKED_TEAM_3x3,
                       QueueType.RANKED_TEAM_5x5
                       ]
        assert queue_type in valid_types, "This api call does not support " + \
                                          queue_type.name + " queues"
        return True

    @staticmethod
    def assert_queue_for_match_list(queue_type):
        valid_types = [
            QueueType.RANKED_FLEX_SR,
            QueueType.RANKED_SOLO_5x5,
            QueueType.RANKED_TEAM_3x3,
            QueueType.RANKED_TEAM_5x5,
            QueueType.TEAM_BUILDER_DRAFT_RANKED_5x5,
            QueueType.TEAM_BUILDER_RANKED_SOLO
        ]

        assert queue_type in valid_types, "This api call does not support " + \
                                      queue_type.name + " queues"
    @staticmethod
    def format_parameter(name, value):
        assert type(name) == str, "Parameter Name must be a string"
        return name + "=" + str(value)

    @staticmethod
    def assert_seasons(seasons):
        valid_values = ["PRESEASON3",
                        "SEASON3",
                        "PRESEASON2014",
                        "SEASON2014",
                        "PRESEASON2015",
                        "SEASON2015",
                        "PRESEASON2016",
                        "SEASON2016",
                        "PRESEASON2017",
                        "SEASON2017",
                        ]
        for season in seasons:
            assert season in valid_values, "Invalid Season " + season
        return True

    @staticmethod
    def assert_summoner_name(summoner_name):
        assert re.match(r"^[\w _.]+$", summoner_name, re.UNICODE) is not None, \
            "Invalid Summoner Name: " + summoner_name
        return True

    @staticmethod
    def assert_static_champ_data_param(champ_data):
        valid_values = ["all",
                        "allytips",
                        "altimages",
                        "blurb",
                        "enemytips",
                        "image",
                        "info",
                        "lore",
                        "partype",
                        "passive",
                        "recommended",
                        "skins",
                        "spells",
                        "stats",
                        "tags"
                        ]
        assert champ_data in valid_values, "Champ Data Param " + champ_data + \
                                           " is invalid"
        return True

    @staticmethod
    def assert_static_item_list_data_param(item_list_data):
        valid_values = ["all",
                        "colloq",
                        "consumeOnFull",
                        "consumed",
                        "depth",
                        "effect",
                        "from",
                        "gold",
                        "groups",
                        "hideFromAll",
                        "image",
                        "inStore",
                        "into",
                        "maps",
                        "requiredChampion",
                        "sanitizedDescription",
                        "specialRecipe",
                        "stacks",
                        "stats",
                        "tags",
                        "tree"
                        ]
        assert item_list_data in valid_values, "Item Data Param " + \
                                               item_list_data + " is invalid"
        return True

    @staticmethod
    def assert_static_mastery_list_data_param(mastery_list_data):
        valid_values = ["all",
                        "image",
                        "masteryTree",
                        "prereq",
                        "ranks",
                        "sanitizedDescription",
                        "tree",
                        ]
        assert mastery_list_data in valid_values, "Mastery Data Param " + \
                                                  mastery_list_data + " is invalid"
        return True

    @staticmethod
    def assert_static_rune_list_data_param(rune_list_data):
        valid_values = ["all",
                        "basic",
                        "colloq",
                        "consumeOnFull",
                        "consumed",
                        "depth",
                        "from",
                        "gold",
                        "hideFromAll",
                        "image",
                        "inStore",
                        "into",
                        "maps",
                        "requiredChampion",
                        "sanitizedDescription",
                        "specialRecipe",
                        "stacks",
                        "stats",
                        "tags",
                        ]
        assert rune_list_data in valid_values, "Rune Data Param " + \
                                               rune_list_data + " is invalid"
        return True

    @staticmethod
    def assert_static_spell_data_param(spell_data):
        valid_values = ["all",
                        "cooldown",
                        "cost",
                        "costBurn",
                        "costType",
                        "effect",
                        "effectBurn",
                        "image",
                        "key",
                        "leveltip",
                        "maxrank",
                        "modes",
                        "range",
                        "rangeBurn",
                        "resource",
                        "sanitizedDescription",
                        "sanitizedTooltip",
                        "vars",
                        ]
        assert spell_data in valid_values, "Spell Data Param " + \
                                           spell_data + " is invalid"
        return True

    version_champion = "v1.2"
    version_game = "v1.3"
    version_league = "v2.5"
    version_static_data = "v1.2"
    version_status = "v1.0"
    version_match = "v2.2"
    version_match_list = "v2.2"
    version_summoner = "v1.4"
    version_stats = "v1.3"

    def __init__(self, string="RGAPI-80b016df-e1ba-4f88-9264-9d5c782c0729", region=Region.NA, handle_limits=True):
        assert type(string) == str, "Argument must be str"
        self.apiKey = string
        self.region = region
        self.handle_limits = handle_limits
        self.versions = []
        self.languages = []

    def api_key_url_string(self):
        self.assert_key_defined()
        return "api_key=" + self.apiKey

    def assert_key_defined(self):
        assert self.apiKey != "", "The api key is not defined"
        return True

    def assert_version(self, version):
        if not self.versions:
            self.static_versions()
        assert version in self.versions, version + " is not a valid version"
        return True

    def assert_language_locale(self, locale):
        if not self.languages:
            self.static_languages()
        assert locale in self.languages, locale + " is not a valid locale language"
        return True

    def _call_api(self, api_url, global_host=False, prepend_host=True):
        if prepend_host:
            if global_host:
                response = requests.get(Region.GLOBAL.host_url + api_url)
            else:
                response = requests.get(self.region.host_url + api_url)
        else:
            response = requests.get(api_url)
        if self.handle_limits and response.status_code == requests.codes.too_many_requests:
            time.sleep(int(response.headers.get('Retry-After', 0)))
            return self._call_api(api_url)
        elif response.status_code == requests.codes.no_content:
            return {}
        else:
            response.raise_for_status()
            return json.loads(response.content.decode('utf-8'))

    # champion v1.2
    def champion_list(self, free_to_play=False):
        api_url = "api/lol/" + str(
            self.region.url) + "/" + self.version_champion + "/champion?" + APIClient.format_parameter(
            "freeToPlay", free_to_play) \
                  + "&" + self.api_key_url_string()
        return self._call_api(api_url)

    def champion_by_id(self, champion_id):
        api_url = "api/lol/" + str(self.region.url) + "/" + self.version_champion + "/champion/" + str(champion_id) \
                  + "?" + self.api_key_url_string()
        return self._call_api(api_url)

    # championmastery
    def champion_mastery_by_ids(self, summoner_id, champion_id):
        api_url = "championmastery/location/" + self.region.platform_id + \
                  "/player/" + str(summoner_id) + "/champion/" + str(champion_id) + \
                  "?" + self.api_key_url_string()
        return self._call_api(api_url)

    def champion_masteries_by_id(self, summoner_id):
        api_url = "championmastery/location/" + self.region.platform_id + \
                  "/player/" + str(summoner_id) + "/champions?" + \
                  self.api_key_url_string()
        return self._call_api(api_url)

    def champion_mastery_score_by_id(self, summoner_id):
        api_url = "championmastery/location/" + self.region.platform_id + \
                  "/player/" + str(summoner_id) + "/score?" + \
                  self.api_key_url_string()
        return self._call_api(api_url)

    def top_champion_masteries_by_id(self, summoner_id, count=3):
        api_url = "championmastery/location/" + self.region.platform_id + \
                  "/player/" + str(summoner_id) + "/topchampions?" + \
                  APIClient.format_parameter("count", count) + "&" + self.api_key_url_string()
        return self._call_api(api_url)

    # current-game v1.0
    def current_game_by_id(self, summoner_id):
        api_url = "observer-mode/rest/consumer/getSpectatorGameInfo/" + \
                  self.region.platform_id + "/" + str(summoner_id) + "?" + \
                  self.api_key_url_string()
        return self._call_api(api_url)

    # featured-games v1.0
    def featured_games(self):
        api_url = "observer-mode/rest/featured?" + self.api_key_url_string()
        return self._call_api(api_url)

    # game v1.3
    def recent_game_by_id(self, summoner_id):
        api_url = "api/lol/" + str(self.region.url) + "" + self.version_game + "/game/by-summoner/" + \
                  str(summoner_id) + "/recent?" + self.api_key_url_string()
        return self._call_api(api_url)

    # league v2.5
    def leagues_by_id(self, summoner_id):
        if type(summoner_id) == list:
            summoner_id = ','.join(requests.utils.quote(str(x)) for x in summoner_id)
        else:
            summoner_id = requests.utils.quote(str(summoner_id))
        api_url = "api/lol/" + self.region.url + "/" + self.version_league + \
                  "/league/by-summoner/" + summoner_id + "?" + self.api_key_url_string()
        return self._call_api(api_url)

    def league_entries_by_id(self, summoner_id):
        if type(summoner_id) == list:
            summoner_id = ','.join(requests.utils.quote(str(x)) for x in summoner_id)
        else:
            summoner_id = requests.utils.quote(str(summoner_id))
        api_url = "api/lol/" + self.region.url + "/" + self.version_league + \
                  "/league/by-summoner/" + summoner_id + "/entry?" + self.api_key_url_string()
        return self._call_api(api_url)

    def challenger_league(self, queue_type: QueueType):
        APIClient.assert_queue_for_league(queue_type)
        api_url = "api/lol/" + self.region.url + "/" + self.version_league + \
                  "/league/challenger?" + \
                  APIClient.format_parameter("type", queue_type.name) + "&" + \
                  self.api_key_url_string()
        return self._call_api(api_url)

    def master_league(self, queue_type: QueueType):
        APIClient.assert_queue_for_league(queue_type)
        api_url = "api/lol/" + self.region.url + "/" + self.version_league + \
                  "/league/master?" + \
                  APIClient.format_parameter("type", queue_type.name) + "&" + \
                  self.api_key_url_string()
        return self._call_api(api_url)

    # lol-static-data v1.2
    def static_champion_list(self, locale="", version="", data_by_id=False, champ_data=""):
        api_url = "api/lol/static-data/" + self.region.url + "/" + \
                  self.version_static_data + "/champion?" + self.api_key_url_string()
        if locale != "" and self.assert_language_locale(locale):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("locale", locale)
        if version != "" and self.assert_version(version):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("version", version)
        if data_by_id:
            api_url = api_url + "&" + \
                      APIClient.format_parameter("dataById", data_by_id)
        if champ_data != "" and APIClient.assert_static_champ_data_param(champ_data):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("champData", champ_data)
        return self._call_api(api_url, global_host=True)

    def static_champion_by_id(self, champion_id, locale="", version="", data_by_id=False, champ_data=""):
        api_url = "api/lol/static-data/" + self.region.url + "/" + \
                  self.version_static_data + "/champion/" + str(champion_id) + \
                  "?" + self.api_key_url_string()
        if locale != "" and self.assert_language_locale(locale):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("locale", locale)
        if version != "" and self.assert_version(version):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("version", version)
        if data_by_id:
            api_url = api_url + "&" + \
                      APIClient.format_parameter("dataById", data_by_id)
        if champ_data != "" and APIClient.assert_static_champ_data_param(champ_data):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("champData", champ_data)
        return self._call_api(api_url, global_host=True)

    def static_item_list(self, locale="", version="", item_list_data=""):
        api_url = "api/lol/static-data/" + self.region.url + "/" + \
                  self.version_static_data + "/item?" + \
                  self.api_key_url_string()
        if locale != "" and self.assert_language_locale(locale):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("locale", locale)
        if version != "" and self.assert_version(version):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("version", version)
        if item_list_data != "" and \
                APIClient.assert_static_item_list_data_param(item_list_data):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("itemListData", item_list_data)
        return self._call_api(api_url, global_host=True)

    def static_item_by_id(self, item_id, locale="", version="", item_list_data=""):
        api_url = "api/lol/static-data/" + self.region.url + "/" + \
                  self.version_static_data + "/item/" + item_id + "?" + \
                  self.api_key_url_string()
        if locale != "" and self.assert_language_locale(locale):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("locale", locale)
        if version != "" and self.assert_version(version):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("version", version)
        if item_list_data != "" and \
                APIClient.assert_static_item_list_data_param(item_list_data):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("itemListData", item_list_data)
        return self._call_api(api_url, global_host=True)

    def static_language_strings(self, locale="", version=""):
        api_url = "api/lol/static-data/" + self.region.url + "/" + \
                  self.version_static_data + "/language-strings?" + \
                  self.api_key_url_string()
        if locale != "" and self.assert_language_locale(locale):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("locale", locale)
        if version != "" and self.assert_version(version):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("version", version)
        return self._call_api(api_url, global_host=True)

    def static_languages(self):
        api_url = "api/lol/static-data/" + self.region.url + "/" + \
                  self.version_static_data + "/languages?" + \
                  self.api_key_url_string()
        self.languages = self._call_api(api_url, global_host=True)
        return self.languages

    def static_map(self, locale="", version=""):
        api_url = "api/lol/static-data/" + self.region.url + "/" + \
                  self.version_static_data + "/map?" + \
                  self.api_key_url_string()
        if locale != "" and self.assert_language_locale(locale):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("locale", locale)
        if version != "" and self.assert_version(version):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("version", version)
        return self._call_api(api_url, global_host=True)

    def static_mastery_list(self, locale="", version="", mastery_list_data=""):
        api_url = "api/lol/static-data/" + self.region.url + "/" + \
                  self.version_static_data + "/mastery?" + \
                  self.api_key_url_string()
        if locale != "" and self.assert_language_locale(locale):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("locale", locale)
        if version != "" and self.assert_version(version):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("version", version)
        if mastery_list_data != "" and \
                APIClient.assert_static_mastery_list_data_param(mastery_list_data):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("masteryListData", mastery_list_data)
        return self._call_api(api_url, global_host=True)

    def static_mastery_by_id(self, mastery_id, locale="", version="", mastery_list_data=""):
        api_url = "api/lol/static-data/" + self.region.url + "/" + \
                  self.version_static_data + "/mastery/" + mastery_id + "?" + \
                  self.api_key_url_string()
        if locale != "" and self.assert_language_locale(locale):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("locale", locale)
        if version != "" and self.assert_version(version):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("version", version)
        if mastery_list_data != "" and \
                APIClient.assert_static_mastery_list_data_param(mastery_list_data):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("masteryListData", mastery_list_data)
        return self._call_api(api_url, global_host=True)

    def static_realm(self):
        api_url = "api/lol/static-data/" + self.region.url + "/" + \
                  self.version_static_data + "/realm?" + \
                  self.api_key_url_string()
        return self._call_api(api_url, global_host=True)

    def static_rune_list(self, locale="", version="", rune_list_data=""):
        api_url = "api/lol/static-data/" + self.region.url + "/" + \
                  self.version_static_data + "/rune?" + \
                  self.api_key_url_string()
        if locale != "" and self.assert_language_locale(locale):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("locale", locale)
        if version != "" and self.assert_version(version):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("version", version)
        if rune_list_data != "" and \
                APIClient.assert_static_rune_list_data_param(rune_list_data):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("runeListData", rune_list_data)
        return self._call_api(api_url, global_host=True)

    def static_rune_by_id(self, rune_id, locale="", version="", rune_list_data=""):
        api_url = "api/lol/static-data/" + self.region.url + "/" + \
                  self.version_static_data + "/rune/" + rune_id + "?" + \
                  self.api_key_url_string()
        if locale != "" and self.assert_language_locale(locale):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("locale", locale)
        if version != "" and self.assert_version(version):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("version", version)
        if rune_list_data != "" and \
                APIClient.assert_static_rune_list_data_param(rune_list_data):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("runeListData", rune_list_data)
        return self._call_api(api_url, global_host=True)

    def static_summoner_spell_list(self, locale="", version="", spell_data=""):
        api_url = "api/lol/static-data/" + self.region.url + "/" + \
                  self.version_static_data + "/summoner-spell?" + \
                  self.api_key_url_string()
        if locale != "" and self.assert_language_locale(locale):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("locale", locale)
        if version != "" and self.assert_version(version):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("version", version)
        if spell_data != "" and \
                APIClient.assert_static_spell_data_param(spell_data):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("spellData", spell_data)
        return self._call_api(api_url, global_host=True)

    def static_summoner_spell_by_id(self, spell_id, locale="", version="", spell_data=""):
        api_url = "api/lol/static-data/" + self.region.url + "/" + \
                  self.version_static_data + "/summoner-spell/" + spell_id + "?" + \
                  self.api_key_url_string()
        if locale != "" and self.assert_language_locale(locale):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("locale", locale)
        if version != "" and self.assert_version(version):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("version", version)
        if spell_data != "" and \
                APIClient.assert_static_spell_data_param(spell_data):
            api_url = api_url + "&" + \
                      APIClient.format_parameter("spellData", spell_data)
        return self._call_api(api_url, global_host=True)

    def static_versions(self):
        api_url = "api/lol/static-data/" + self.region.url + "/" + \
                  self.version_static_data + "/versions?" + \
                  self.api_key_url_string()
        self.versions = self._call_api(api_url, global_host=True)
        return self.versions

    # lol-status v1.0
    def status_shard(self, region=Region.GLOBAL):
        api_url = "lol/status/" + self.version_status + "/shard?" + \
                  self.api_key_url_string()
        if region == Region.GLOBAL:
            return self._call_api(api_url)
        else:
            return self._call_api(region.host_url + api_url, prepend_host=False)

    def status_shard_list(self):
        api_url = "lol/status/" + self.version_status + "/shards?" + \
                  self.api_key_url_string()
        return self._call_api(api_url)

    # match v2.2
    def match_info(self, match_id, include_timeline=False, region=Region.GLOBAL):
        api_url = "/" + self.version_match + \
                  "/match/" + str(match_id) + "?" + self.api_key_url_string()
        if include_timeline:
            api_url = api_url + "&" + \
                      APIClient.format_parameter("includeTimeline", include_timeline)
        if region == Region.GLOBAL:
            api_url = "api/lol/" + self.region.url + api_url
            return self._call_api(api_url)
        else:
            api_url = "api/lol/" + region.url + api_url
            return self._call_api(region.host_url + api_url, prepend_host=False)

    # matchlist v2.2
    def math_list_by_id(self, summoner_id, region=Region.GLOBAL, champion_ids="", ranked_queues="", seasons="",
                        begin_time="", end_time="", begin_index="", end_index=""):
        api_url = "/" + self.version_match_list + "/matchlist/by-summoner/" \
                  + str(summoner_id) + "?" + self.api_key_url_string()
        if champion_ids:
            api_url = api_url + "&" + APIClient.format_parameter("championIds",
                                                                 ','.join(str(x) for x in champion_ids))
        if ranked_queues:
            api_url = api_url + "&" + APIClient.format_parameter("rankedQueues",
                                                                 ','.join(
                                                                     str(x) for x in ranked_queues if QueueType.is_ranked(x)))
        if APIClient.assert_seasons(seasons):
            api_url = api_url + "&" + APIClient.format_parameter("seasons", ','.join(seasons))
        if begin_time:
            api_url = api_url + "&" + APIClient.format_parameter("beginTime", begin_time)
        if end_time:
            api_url = api_url + "&" + APIClient.format_parameter("endTime", end_time)
        if begin_index and end_index:
            api_url = api_url + "&" + APIClient.format_parameter("beginIndex", begin_index) + \
                      "&" + APIClient.format_parameter("endIndex", end_index)
        if region == Region.GLOBAL:
            api_url = "api/lol/" + self.region.url + api_url
            return self._call_api(api_url)
        else:
            api_url = "api/lol/" + region.url + api_url
            return self._call_api(region.host_url + api_url, prepend_host=False)

    # stats v1.3
    def ranked_stats_by_id(self, summoner_id):
        api_url = "api/lol/" + str(self.region.url) + "/" + self.version_stats + "/stats/by-summoner/" + \
                  str(summoner_id) + "/ranked?" + self.api_key_url_string()
        return self._call_api(api_url)

    def stats_summary_by_id(self, summoner_id):
        api_url = "api/lol/" + str(self.region.url) + "" + self.version_stats + "/stats/by-summoner/" + \
                  str(summoner_id) + "/summary?" + self.api_key_url_string()
        return self._call_api(api_url)

    # summoner v1.4
    def summoner_profile_by_name(self, summoner_name):
        if type(summoner_name) == list:
            summoner_name = ','.join(
                requests.utils.quote(str(x)) for x in summoner_name if self.assert_summoner_name(x))
        elif self.assert_summoner_name(summoner_name):
            summoner_name = requests.utils.quote(str(summoner_name))
        api_url = "/api/lol/" + str(self.region.url) + "/" + self.version_summoner + "/summoner/by-name/" \
                  + summoner_name + "?" + self.api_key_url_string()
        return self._call_api(api_url)

    def summoner_profile_by_id(self, summoner_id):
        if type(summoner_id) == list:
            summoner_id = ','.join(requests.utils.quote(str(x)) for x in summoner_id)
        else:
            summoner_id = requests.utils.quote(str(summoner_id))
        api_url = "/api/lol/" + str(self.region.url) + "/" + self.version_summoner + "/summoner/" \
                  + str(summoner_id) + "?" + self.api_key_url_string()
        return self._call_api(api_url)

    def summoner_name_by_id(self, summoner_id):
        if type(summoner_id) == list:
            summoner_id = ','.join(requests.utils.quote(str(x)) for x in summoner_id if self.assert_summoner_name(x))
        else:
            summoner_id = requests.utils.quote(str(summoner_id))
        api_url = "/api/lol/" + str(self.region.url) + "/" + self.version_summoner + "/summoner/" \
                  + str(summoner_id) + "/name?" + self.api_key_url_string()
        return self._call_api(api_url)

    def masteries_by_id(self, summoner_id):
        if type(summoner_id) == list:
            summoner_id = ','.join(requests.utils.quote(str(x)) for x in summoner_id)
        else:
            summoner_id = requests.utils.quote(str(summoner_id))
        api_url = "api/lol/" + str(self.region.url) + "/" + self.version_summoner + "/summoner/" + \
                  summoner_id + "/masteries?" + self.api_key_url_string()
        return self._call_api(api_url)

    def runes_by_id(self, summoner_id):
        if type(summoner_id) == list:
            summoner_id = ','.join(requests.utils.quote(str(x)) for x in summoner_id)
        else:
            summoner_id = requests.utils.quote(str(summoner_id))
        api_url = "api/lol/" + str(self.region.url) + "/" + self.version_summoner + "/summoner/" + \
                  summoner_id + "/runes?" + self.api_key_url_string()
        return self._call_api(api_url)
