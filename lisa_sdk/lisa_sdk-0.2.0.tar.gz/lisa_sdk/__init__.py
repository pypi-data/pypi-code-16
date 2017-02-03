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


class Language(object):
    def __init__(self, name, prefix, code):
        self.name = name
        self.prefix = prefix
        self.code = code


class LisaLanguages(Enum):
    ENGLISH = Language("english", "en", "en-US")
    FRENCH = Language("french", "fr", "fr-FR")
    GERMAN = Language("german", "de", "de-DE")
    ITALIAN = Language("italian", "it", "it-IT")
    PORTUGUESE = Language("portuguese", "pt", "pt-PT")
    SPANISH = Language("spanish", "es", "es-ES")

    @staticmethod
    def get_language_by_name(name):
        for language in LisaLanguages:
            if language.name == name:
                return language
        raise LisaLanguageUndefined

    @staticmethod
    def get_language_by_prefix(prefix):
        for language in LisaLanguages:
            if language.prefix == prefix:
                return language
        raise LisaLanguageUndefined

    @staticmethod
    def get_language_by_code(code):
        for language in LisaLanguages:
            if language.code == code:
                return language
        raise LisaLanguageUndefined
