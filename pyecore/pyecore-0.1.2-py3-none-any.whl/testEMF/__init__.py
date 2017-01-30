import pyecore.ecore as Ecore
from .testEMF import getEClassifier, eClassifiers
from .testEMF import NamedElement, TClass, A, TInterface, B, Stuffs
from .inner import C
from . import testEMF
from . import inner

__all__ = ['TClass', 'A', 'TInterface', 'NamedElement', 'B', 'Stuffs']

name = 'testEMF'
nsURI = 'http://testEMF/1.0'
nsPrefix = 'testemf'

eClass = Ecore.EPackage(name=name, nsURI=nsURI, nsPrefix=nsPrefix)

eSubpackages = [inner]
eSuperPackage = None


# Non opposite EReferences
TClass.namedelement.eType = NamedElement
A.b.eType = B

# opposite EReferences
B.c.eType = C
C.b.eType = B
C.b.eOpposite = B.c


# Manage all other EClassifiers (EEnum, EDatatypes...)
otherClassifiers = [Stuffs]
for classif in otherClassifiers:
    eClassifiers[classif.name] = classif
    classif._container = testEMF

for classif in eClassifiers.values():
    eClass.eClassifiers.append(classif.eClass)

for subpack in eSubpackages:
    eClass.eSubpackages.append(subpack.eClass)
