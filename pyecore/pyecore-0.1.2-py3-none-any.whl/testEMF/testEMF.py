from pyecore.ecore import *
import pyecore.ecore as Ecore

Stuffs = EEnum('Stuffs', literals=['FIRST','SECOND',])


@abstract
class NamedElement(EObject, metaclass=MetaEClass):
    name = EAttribute(eType=EString)

    def __init__(self):
        super().__init__()

    def eOperation(self, p1, p2):
        raise NotImplementedError('Operation eOperation(...) is not yet implemented')

    def eOperation2(self, p1, p2):
        raise NotImplementedError('Operation eOperation2(...) is not yet implemented')


class TClass(NamedElement):
    abstract = EAttribute(eType=EBoolean)
    _isAbs = EAttribute(name='isAbs', eType=EBoolean, derived=True)
    namedelement = EReference(upper=-1)

    def __init__(self):
        super().__init__()

    @property
    def isAbs(self):
        return self._isAbs

    @isAbs.setter
    def isAbs(self, value):
        self._isAbs = value


class TInterface(NamedElement):
    def __init__(self):
        super().__init__()


class B(NamedElement):
    c = EReference(upper=-1, containment=True)

    def __init__(self):
        super().__init__()


class A(TClass, TInterface):
    name = EAttribute(eType=EInteger)
    b = EReference()

    def __init__(self):
        super().__init__()

    @property
    def isAbs(self):
        return self._isAbs

    @isAbs.setter
    def isAbs(self, value):
        self._isAbs = value
