import pyecore.ecore as Ecore
from .inner import getEClassifier, eClassifiers
from .inner import C
from . import inner
from .. import testEMF

__all__ = ['C']

name = 'inner'
nsURI = ''
nsPrefix = ''

eClass = Ecore.EPackage(name=name, nsURI=nsURI, nsPrefix=nsPrefix)

eSubpackages = []
eSuperPackage = testEMF



# Manage all other EClassifiers (EEnum, EDatatypes...)
otherClassifiers = []
for classif in otherClassifiers:
    eClassifiers[classif.name] = classif
    classif._container = inner

for classif in eClassifiers.values():
    eClass.eClassifiers.append(classif.eClass)

for subpack in eSubpackages:
    eClass.eSubpackages.append(subpack.eClass)

