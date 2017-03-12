class FastStartError(Exception):
    """ Standard exception """
    pass

class AlreadyMoved(FastStartError):
    """ Raised when the input's moov atom is already in the correct place. """
    pass

class FileIsCorrupt(FastStartError):
    """ Raised when the input has a perceived corruption. For example,
        unreadable atoms
    """
    pass

class FileIsUnsupported(FastStartError):
    """ Raised when the moov atom is compressed. """
    pass
