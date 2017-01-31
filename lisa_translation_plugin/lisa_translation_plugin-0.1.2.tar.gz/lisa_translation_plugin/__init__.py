from lisa_sdk import LisaPlugin


class LisaTranslationPlugin(LisaPlugin):
    def __init__(self):
        super().__init__()
        self.name = "lisa-translation-plugin"

    def get_name(self):
        return self.name

