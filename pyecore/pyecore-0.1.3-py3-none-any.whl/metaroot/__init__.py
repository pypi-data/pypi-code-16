import pyecore.ecore as Ecore
from .metaroot import NamedElement, A
from .metaroot import getEClassifier, eClassifiers
from .innerpack import B
from . import metaroot
from . import innerpack

__all__ = ['NamedElement', 'A']

nsURI = 'http://metaroot/1.0'
nsPrefix = 'metaroot'
name = 'metaroot'

eClass = Ecore.EPackage(name=name, nsURI=nsURI, nsPrefix=nsPrefix)

eSubpackages = [innerpack]

NamedElement.contained.eType = B
B.inner.eType = NamedElement
B.inner.eOpposite = NamedElement.contained


eURIFragment = Ecore.default_eURIFragment

# for other classifiers (EDataType and EEnum)
otherClassifiers = []
for classif in otherClassifiers:
    eClassifiers[classif.name] = classif
    classif._container = metaroot

for classif in eClassifiers.values():
    eClass.eClassifiers.append(classif.eClass)

for subpack in eSubpackages:
    eClass.eSubpackages.append(subpack.eClass)
