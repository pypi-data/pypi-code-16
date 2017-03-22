#!/usr/bin/env python
import dbus  # pip install dbus-python
import re
from getpass import getuser, getpass
from urllib import error
from mpris_scrobbler.services import wiltfm


class Scrobble(object):

    def __init__(self, username=None, password=None, service="wiltfm",
                 device=None):
        self.conf_dir = "/home/{}/.config/mpris-scrobble".format(getuser())

        self.prefix = "org.mpris.MediaPlayer2."

        self.bus = dbus.SessionBus()
        self.bus.request_name("xyz.mashek.mpris.scrobble")

        self.config = {
            "username": username,
            "password": password,
            "service": service,
            "device": device
        }

        self.started = self.start()
        self.device = self.register_device()

    def start(self):
        li = self._login()
        if li is not True:
            return li

        dvc = self.get_device()
        if dvc is not True:
            return dvc

        return True

    def _login(self):
        if not self.config["username"]:
            self.config["username"] = input("username: ")
        if not self.config["password"]:
            self.config["password"] = getpass("password: ")

        try:
            self.wilt = wiltfm.Wilt(self.config["username"],
                                    self.config["password"])
            return True
        except error.HTTPError as e:
            return str(e)

    def get_device(self):
        if not self.config["device"]:
            s = {}
            print("Availble MPRIS devices:")
            for dev in self.bus.list_names():
                if re.match(self.prefix, dev):
                    spl = dev.rsplit(self.prefix)[1]
                    s[spl] = dev
                    print(" " + spl)

            ch = input("Which will you use: ")
            if ch not in s:
                return "Invalid choice"

            self.config["device"] = ch
        return True

    def register_device(self):
        try:
            return dbus.SessionBus().get_object(
               self.prefix + self.config["device"], "/org/mpris/MediaPlayer2"
            )
        except dbus.exceptions.DBusException as e:
            return "scrobble.register_device: " + str(e)
        except TypeError:
            self.get_device()

    def push(self):
        if not self.config["device"]:
            return "Do device to push to."

        try:
            metadata = self.device.Get(
                'org.mpris.MediaPlayer2.Player',
                'Metadata',
                dbus_interface='org.freedesktop.DBus.Properties'
            )

        except AttributeError as e:
            if type(self.device) is str:
                return self.device
            return "push.AttributeError: " + str(e)
        except KeyError as e:
            return "push.KeyError: " + str(e)
        except dbus.exceptions.DBusException as e:
            return "push.dbus.exceptions.DBusException: " + str(e)

        track = metadata['xesam:title']
        artist = metadata['xesam:artist'][0]

        if track is not None and artist is not None:
            result = self.wilt.scrobble({'song': track, 'artist': artist})

            if result:
                return result
