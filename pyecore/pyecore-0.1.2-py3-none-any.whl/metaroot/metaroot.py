from pyecore.ecore import MetaEClass, abstract, EString, EModelElement
from pyecore.ecore import EAttribute, EObject, EReference


@abstract
class NamedElement(EModelElement, metaclass=MetaEClass):
    name = EAttribute(eType=EString)
    contained = EReference()

    def __init__(self, name=None):
        super().__init__()
        self.name = name


class A(NamedElement):
    def __init___(self, name=None):
        super().__init___(name)
