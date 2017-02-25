from NucleusUtils.singleton import Singleton

from . import Translator
from .advanced import AdvancedTranslator


class SingleTranslator(Translator, Singleton):
    pass


class SingleAdvancedTranslator(AdvancedTranslator, Singleton):
    pass
