from ..singleton import SingletonMetaClass

from . import Translator
from .advanced import AdvancedTranslator


class SingleTranslator(Translator, metaclass=SingletonMetaClass):
    pass


class SingleAdvancedTranslator(AdvancedTranslator, metaclass=SingletonMetaClass):
    pass
