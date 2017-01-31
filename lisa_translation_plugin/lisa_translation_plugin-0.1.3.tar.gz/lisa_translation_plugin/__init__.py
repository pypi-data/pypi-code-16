from lisa_sdk import LisaPlugin


class LisaTranslationPlugin(LisaPlugin):
    def __init__(self):
        super().__init__()
        self.name = "lisa-translation-plugin"
        self.description = "module de traduction linguistique"

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description
