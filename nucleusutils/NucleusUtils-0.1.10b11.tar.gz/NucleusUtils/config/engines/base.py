class BaseLoader:
    """
    Base of configs loader
    Use this abstract class for making new configs loaders
    """

    def __init__(self, encoding='utf8', settings=None):
        if settings is None:
            settings = {}
        self.encoding = encoding
        self.settings = settings

    def load_data(self, filename: str) -> open:
        with open(filename, 'r', encoding=self.encoding) as file:
            return self.parse(file)

    def parse(self, file: open) -> dict:
        raise NotImplementedError
