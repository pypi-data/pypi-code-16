import goslate
from lisa_sdk import LisaPlugin


class LisaTranslationPlugin(LisaPlugin):
    def __init__(self):
        super().__init__()
        self.name = "lisa-translation-plugin"
        self.description = "module de traduction linguistique"
        self.listening_language = "default"

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description

    def process_speech(self, speech, language):
        pass

    def get_listening_language(self):
        return self.listening_language

    def get_call_regex(self):
        return {
            "fr-FR": ["traduction"]
        }


def main():
    gs = goslate.Goslate()
    print(gs.translate("hello world", "fr"))


if __name__ == "__main__":
    main()
