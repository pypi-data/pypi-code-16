class LisaPlugin(object):
    def get_name(self):
        raise NotImplementedError

    def get_description(self):
        raise NotImplementedError


class SpeechResponse(object):
    def __init__(self, speech, language="fr-FR"):
        self.speech = speech
        self.language = language
