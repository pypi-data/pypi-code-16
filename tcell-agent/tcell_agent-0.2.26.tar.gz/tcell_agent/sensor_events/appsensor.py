# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.config import CONFIGURATION
from tcell_agent.sanitize import SanitizeUtils

from . import SensorEvent


class AppSensorEvent(SensorEvent):
    def __init__(self,
                 detection_point,
                 parameter,
                 location,
                 remote_address,
                 route_id,
                 meta,
                 method,
                 session_id=None,
                 user_id=None,
                 count=None,
                 payload=None,
                 pattern=None):
        super(AppSensorEvent, self).__init__("as")
        self["dp"] = detection_point
        self._raw_location = location

        if parameter is not None:
            self["param"] = parameter
        if remote_address is not None:
            self["remote_addr"] = remote_address
        if method is not None:
            self["m"] = method
        if meta is not None:
            self["meta"] = meta
        if route_id is not None:
            self["rid"] = str(route_id)
        if session_id is not None:
            self["sid"] = session_id
        if count is not None:
            self["count"] = count
        if payload is not None:
            self["payload"] = payload[:150]
        if pattern is not None:
            self["pattern"] = pattern

        if user_id is not None:
            if CONFIGURATION.hipaa_safe_mode:
                self["uid"] = SanitizeUtils.hmac(str(user_id))
            else:
                self["uid"] = str(user_id)

    def post_process(self):
        if "payload" in self:
            self["payload"] = self["payload"][:150]
        if self._raw_location is not None:
            self["uri"] = SanitizeUtils.strip_uri(self._raw_location)
