
class NoPrivateKeyException(Exception):

    def __init__(self):

        super(NoPrivateKeyException, self).__init__("Please provide an Private-Key before getting contents.")
