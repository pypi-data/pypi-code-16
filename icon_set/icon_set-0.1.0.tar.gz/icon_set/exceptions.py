class IconSetError(Exception):
    pass


class FileLengthTooLargeError(IconSetError):
    pass


class InvalidIconTypeError(IconSetError):
    pass
