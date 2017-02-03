from enum import Enum


class LisaPlugin(object):
    def get_name(self):
        raise NotImplementedError

    def get_description(self):
        raise NotImplementedError

    def get_call_keywords(self):
        raise NotImplementedError

    def on_enable(self):
        raise NotImplementedError

    def on_disable(self):
        raise NotImplementedError

    def process_speech(self, speech, language):
        raise NotImplementedError

    def get_listening_language(self):
        raise NotImplementedError


class UserSpeech(object):
    def __init__(self, speeches, language):
        self.speeches = speeches
        self.language = language


class SpeechResponse(object):
    def __init__(self, speech, language=None):
        self.speech = speech
        self.language = language


class LisaLanguageUndefined(Exception):
    pass


class LisaLanguage(Enum):
    ENGLISH = {"name": "english", "prefix": "en", "code": "en-US"}
    FRENCH = {"name": "french", "prefix": "fr", "code": "fr-FR"}
    GERMAN = {"name": "german", "prefix": "de", "code": "de-DE"}
    ITALIAN = {"name": "italian", "prefix": "it", "code": "it-IT"}
    PORTUGUESE = {"name": "portuguese", "prefix": "pt", "code": "pt-PT"}
    SPANISH = {"name": "spanish", "prefix": "es", "code": "es-ES"}

    @staticmethod
    def get_language_by_name(name):
        for language in LisaLanguage:
            if language.name == name:
                return language
        raise LisaLanguageUndefined

    @staticmethod
    def get_language_by_prefix(prefix):
        for language in LisaLanguage:
            if language.prefix == prefix:
                return language
        raise LisaLanguageUndefined

    @staticmethod
    def get_language_by_code(code):
        for language in LisaLanguage:
            if language.code == code:
                return language
        raise LisaLanguageUndefined
