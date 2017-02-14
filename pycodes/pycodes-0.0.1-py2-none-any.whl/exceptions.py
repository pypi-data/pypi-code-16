class PyCodesError(Exception):
    """ Class for all the errors raised from the library. """
    pass


class WrongCode(PyCodesError):
    """ When a code is wrong for any reason. """
    pass


class BadCodeLength(WrongCode):
    """ When the code doesn't have the correct number of characters. """

    def __init__(self, curr: int, exp: int):
        super().__init__(f'Bad code length: {curr} (expected {exp})')


class CharacterNotAllowed(WrongCode):
    """ When the code cannot contain this particular character. """

    def __init__(self, character: str):
        super().__init__(f'Bad character: "{character}"')


class EmptyCode(WrongCode):
    """ When the code is None or empty. """

    def __init__(self):
        super().__init__('Code cannot be None nor empty')


class WrongChecksum(WrongCode):
    """ When the provided checksum iof a code isn't valid. """

    def __init__(self, fmt: str, chk: str, code: str):
        super().__init__(f'Wrong {fmt} checksum "{chk}" for code "{code}"')
