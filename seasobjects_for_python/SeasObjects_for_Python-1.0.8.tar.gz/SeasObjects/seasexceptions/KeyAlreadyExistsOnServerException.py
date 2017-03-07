class KeyAlreadyExistsOnServerException(Exception):
    def __init__(self, message):
        super(KeyAlreadyExistsOnServerException, self).__init__(message)
        