class Bytes(int):
    def to_megabytes(self):
        return Megabyte(int(self.real / 1024 ** 2))

    def to_gigabytes(self):
        return Gigabyte(int(self.real / 1024 ** 3))


class Megabyte(int):
    def to_bytes(self):
        return Bytes(self.real * 1024 ** 2)

    def to_gigabytes(self):
        return Gigabyte(int(self.real / 1024 ** 1))


class Gigabyte(int):
    def to_bytes(self):
        return Bytes(self.real * 1024 ** 3)

    def to_megabytes(self):
        return Megabyte(self.real * 1024 ** 1)
