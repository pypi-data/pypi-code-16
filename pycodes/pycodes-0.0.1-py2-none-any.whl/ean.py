from pycodes.exceptions import CharacterNotAllowed, BadCodeLength, WrongChecksum, \
    EmptyCode


class Ean13:
    def __init__(self, code: str, checksum: bool = True):
        """ Creates a new Ean13 instance from the given code.

        :param code: The str vale of the code. It is expected to have ONLY
            digits (i.e. no spaces, etc..).
        :param checksum: If the parameter `code` contains or not the checksum
            digit. If True (the default) it'll be checked (thus, that's the way
            to check if the barcode is valid or not). If False, a new checksum
            value will be computed and added to the ean.
        :raise BadCodeLength: If the code string hasn't a 12 length (with no
            checksum) or a 13 length (with checksum).
        :raise CharacterNotAllowed: If the code contains at least a non-digit
            character.
        :raise WrongChecksum: If the code has checksum but is incorrect
        :raise EmptyCode: When the code isNone or empty.
        """
        super().__init__()

        # First, check the code is not None not empty
        if code is None or not code.strip():
            raise EmptyCode()
        else:
            code = code.strip()
        # Next, check if all the characters of the code are digits
        if not code.isdigit():
            for c in code:
                if not c.isdigit():
                    raise CharacterNotAllowed(c)

        if not checksum:
            if len(code) != 12:
                raise BadCodeLength(len(code), 12)

            self.code = code
            self.checksum = self.calculate_checksum(self.code)
        else:
            if len(code) != 13:
                raise BadCodeLength(len(code), 13)
            if code[-1:] != self.calculate_checksum(code[:-1]):
                raise WrongChecksum(
                    self.__class__.__name__,
                    self.calculate_checksum(code[:-1]),
                    code[:-1],
                )

            self.code = code[:-1]
            self.checksum = code[-1:]

    @staticmethod
    def calculate_checksum(code: str) -> str:
        """ Given a 12-digit code, returns the ean-13 checksum for it.

        :param code: A ean-13 code with no checksum (i.e. a 12 digits string)
        :return: A character with a valid checksum for the specified code.
        """
        summation = sum(
            int(digit) * 3 if (i % 2 == 0) else int(digit)
            for i, digit in enumerate(reversed(code))
        )

        return str((10 - (summation % 10)) % 10)

    def __str__(self):
        """ A ean13 as string is the full code (code plus checksum)"""
        return f'{self.code}{self.checksum}'
