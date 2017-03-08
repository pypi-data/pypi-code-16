import logging
import os

from .engines import default
from .engines.base import BaseLoader

log = logging.getLogger(__package__)


class Config:
    def __init__(self, filename, encoding='utf8', engine=None, defaults=None, default_none=None,
                 settings=None):
        if settings is None:
            settings = {}
        if defaults is None:
            defaults = {}

        if not os.path.isfile(filename):
            raise FileNotFoundError(filename)

        self.file = filename
        self.filename = os.path.split(filename)[1]
        self.encoding = encoding
        self.engine_settings = settings
        self._engine: BaseLoader = engine
        self._defaults = defaults
        self._default_none = default_none

        self._data = {}

        self._loaded = False

    def update_defaults(self, data: dict):
        self._defaults.update(data)
        return self

    def setup_defaults(self, data: dict):
        self._defaults = data
        return self

    def set_default(self, value):
        self._default_none = value
        return self

    def get_engine(self) -> BaseLoader:
        if self._engine is None:
            file_extension = self.filename.split('.')[-1]
            for engine in default:
                if file_extension == engine[0]:
                    self._engine = engine[1]
                    break
        return self._engine

    def load(self):
        engine = self.get_engine()

        if engine is not None:
            eng = engine(self.encoding, self.engine_settings)
            log.debug(f'Load configs file "{self.file}"')
            self._data = eng.load_data(self.file)

        self._loaded = True
        return self

    def as_dict(self) -> dict:
        return self._data

    def __getitem__(self, item):
        if not self._loaded:
            self.load()
        if item in self._data:
            return self._data.get(item)
        if item in self._defaults:
            return self._defaults.get(item)
        return self._default_none

    def __str__(self):
        return self.file
