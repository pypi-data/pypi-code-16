from NucleusUtils.singleton import Singleton

from . import Translator
from .advanced import AdvancedTranslator


class SingleTranslator(Translator, metaclass=Singleton):
    pass


class SingleAdvancedTranslator(AdvancedTranslator, metaclass=Singleton):
    pass
