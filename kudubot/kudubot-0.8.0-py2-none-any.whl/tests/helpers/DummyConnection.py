u"""
LICENSE:
Copyright 2015-2017 Hermann Krumrey

This file is part of kudubot.

    kudubot is a chat bot framework. It allows developers to write
    services for arbitrary chat services.

    kudubot is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    kudubot is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with kudubot.  If not, see <http://www.gnu.org/licenses/>.
LICENSE
"""

from __future__ import absolute_import
from typing import Dict
from kudubot.users.Contact import Contact
from kudubot.connections.Message import Message
from kudubot.connections.Connection import Connection


class DummyConnection(Connection):
    u"""
    A class that implements a Connection for use in unit tests
    """

    identifier = u"dummyconnection"

    def listen(self):
        pass

    def define_user_contact(self):
        pass

    def load_config(self):
        pass

    def send_message(self, message):
        pass

    def generate_configuration(self):
        pass

    def send_image_message(self, receiver, image_file, caption = u""):
        pass

    def send_video_message(self, receiver, video_file, caption = u""):
        pass

    def send_audio_message(self, receiver, audio_file, caption = u""):
        pass
