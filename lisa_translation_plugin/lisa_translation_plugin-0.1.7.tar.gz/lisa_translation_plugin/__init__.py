from goslate import Goslate
from lisa_sdk import LisaPlugin, SpeechResponse, LisaLanguageUndefined, LisaLanguages


class TranslationRequest(object):
    def __init__(self):
        self.sourceLanguage = None
        self.outcomeLanguage = None
        self.input = None
        self.output = None


class LisaTranslationPlugin(LisaPlugin):
    def __init__(self):
        self.goslate = Goslate()
        self.name = "lisa-translation-plugin"
        self.description = "module de traduction linguistique"
        self.listening_language = "default"
        self.request = TranslationRequest()

        self.call_keywords = {
            "fr-FR": ["traduction"]
        }

    def init_config(self):
        self.listening_language = "default"
        self.request = TranslationRequest()

    def on_enable(self):
        self.init_config()
        return SpeechResponse("Quelle est la langue du texte à traduire ?")

    def on_disable(self):
        return SpeechResponse("")

    def process_speech(self, speech, language):
        response = "Je n'ai pas compris, veuillez réesayer"
        response_language = None

        if self.request.sourceLanguage is None:
            try:
                language = LisaLanguages.get_language_by_name(self.goslate.translate(speech, "en").lower())
                self.request.outcomeLanguage = language
                response = "En quel langue le texte doit-il être traduit ?"
            except LisaLanguageUndefined:
                response = "Le language demandé n'est pas supporté"
        elif self.request.outcomeLanguage is None:
            try:
                language = LisaLanguages.get_language_by_name(self.goslate.translate(speech, "en").lower())
                self.request.outcomeLanguage = language
                self.listening_language = self.request.sourceLanguage
                response = "Quel est le texte à traduire"
            except LisaLanguageUndefined:
                response = "Le language demandé n'est pas supporté"
        elif self.request.input is None:
            self.init_config()
            self.request.input = speech
            response = self.goslate.translate(speech, self.request.outcomeLanguage.value.prefix)
            response_language = self.request.outcomeLanguage

        return SpeechResponse(response, response_language)

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description

    def get_listening_language(self):
        return self.listening_language

    def get_call_keywords(self):
        return self.call_keywords
