from ..metaroot import NamedElement
from pyecore.ecore import EReference

nsURI = 'http://metaroot/1.0/innerpack'
nsPrefix = 'innerpack'
name = 'innerpack'

class B(NamedElement):
    inner = EReference(containment=True, upper=-1)

    def __init__(self, name=None):
        super().__init__(name)
