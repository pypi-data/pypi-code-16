
class NoApiKeyException(Exception):

    def __init__(self):

        super(NoApiKeyException, self).__init__("Please provide an API-Key before getting contents.")
