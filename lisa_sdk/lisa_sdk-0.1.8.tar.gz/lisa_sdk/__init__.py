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


class LisaLanguage(object):
    languages = {
        "english": {"prefix": "en", "code": "en-US"},
        "spanish": {"prefix": "es", "code": "es-ES"},
        "french": {"prefix": "fr", "code": "fr-FR"},
        "german": {"prefix": "de", "code": "de-DE"},
        "italian": {"prefix": "it", "code": "it-IT"},
        "portuguese": {"prefix": "pt", "code": "pt-PT"}
    }

    def is_language_defined(self, language_requested):
        for language, identifier in self.languages:
            if language == language_requested:
                return True

        return False

    def get_language_prefix(self, language):
        if self.is_language_defined(language) is False:
            raise LisaLanguageUndefined

        return self.languages[language]["prefix"]

    def get_language_code(self, language):
        if self.is_language_defined(language) is False:
            raise LisaLanguageUndefined

        return self.languages[language]["code"]
