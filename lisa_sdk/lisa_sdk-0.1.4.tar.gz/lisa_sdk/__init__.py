class LisaPlugin(object):
    def get_name(self):
        raise NotImplementedError

    def get_description(self):
        raise NotImplementedError

    def get_call_regex(self):
        raise NotImplementedError

    def process_speech(self, speech, language):
        raise NotImplementedError

    def get_listening_language(self):
        raise NotImplementedError


class UserSpeech(object):
    def __init__(self, speech, language):
        self.speech = speech
        self.language = language


class SpeechResponse(object):
    def __init__(self, speech, language=None):
        self.speech = speech
        self.language = language
