# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function

import re

from future.backports.urllib.parse import urlsplit

from tcell_agent.policies import TCellPolicy
from tcell_agent.sensor_events.http_redirect import RedirectSensorEvent


def wildcard_re(item):
    return re.compile("^" + re.escape(item).replace("\*", ".*") + "$")


def get_location_host(url):
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    return netloc


class HttpRedirectPolicy(TCellPolicy):
    def __init__(self, policy_json=None):
        super(HttpRedirectPolicy, self).__init__()
        self.enabled = False
        self.block = False
        self.whitelist = []
        if policy_json is not None:
            self.loadFromJson(policy_json)

    def loadFromJson(self, policy_json):
        if "policy_id" in policy_json:
            self.policy_id = policy_json["policy_id"]
        else:
            raise Exception("Policy Id Not Found")

        policy_data_json = policy_json.get("data")
        if policy_data_json:
            self.enabled = policy_data_json.get("enabled", False)
            self.block = policy_data_json.get("block", False)
            whitelist = policy_data_json.get("whitelist", [])
            self.whitelist = [wildcard_re(item) for item in whitelist]

    def process_location(self,
                         remote_addr,
                         method,
                         from_domain,
                         from_full_path,
                         status_code,
                         redirect_url,
                         user_id=None,
                         session_id=None,
                         route_id=None):
        if not self.enabled:
            return redirect_url

        from tcell_agent.agent import TCellAgent

        location_host = get_location_host(redirect_url)

        if location_host == "":
            return redirect_url

        if location_host == from_domain:
            return redirect_url

        for item in self.whitelist:
            if item.match(location_host):
                return redirect_url

        event = RedirectSensorEvent(
            remote_addr,
            method,
            from_domain,
            from_full_path,
            status_code,
            location_host,
            user_id,
            session_id,
            route_id)

        TCellAgent.send(event)

        if self.block:
            return "/"

        return redirect_url
