import pyecore.ecore as Ecore
from .innerpack import B, getEClassifier, eClassifiers
from .innerpack import name, nsURI, nsPrefix
from .. import metaroot

__all__ = ['B']

eClass = Ecore.EPackage(name=name, nsURI=nsURI, nsPrefix=nsPrefix)

eSuperPackage = metaroot

eURIFragment = Ecore.default_eURIFragment

# for other classifiers
otherClassifiers = []
for classif in otherClassifiers:
    eClassifiers[classif.name] = classif
    classif._container = metaroot

for classif in eClassifiers.values():
    eClass.eClassifiers.append(classif.eClass)
