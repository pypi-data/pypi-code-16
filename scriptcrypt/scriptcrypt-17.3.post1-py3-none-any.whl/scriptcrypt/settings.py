import json
import os.path
from os import environ, makedirs


class Settigns(object):
    fpath = environ["HOME"] + "/.config/scriptcrypt" + "/settings.json"

    def __init__(self):
        pass

    def writeSettings(self, settings):
        with open(self.fpath, "w") as f:
            f.write(json.dumps(settings,
                               sort_keys=True,
                               indent=4,
                               separators=(',', ': ')))

    def readSettings(self):
        with open(self.fpath, "r") as f:
            dump = f.read()

        return json.loads(dump)

    def writeSettingsDefault(self):
        home = environ["HOME"]
        settings = {"editor": "nano",
                    "viewer": "less",
                    "shell": "sh",
                    "appdir": home + "/Applications",
                    "db": home + "/.scriptcrypt.db"}
        self.writeSettings(settings)

    def getSettings(self):
        if not os.path.isfile(self.fpath):
            try:
                makedirs(os.path.dirname(self.fpath))
            except FileExistsError:
                pass
            self.writeSettingsDefault()
        return self.readSettings()
