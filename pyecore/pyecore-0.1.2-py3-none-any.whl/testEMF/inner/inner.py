from pyecore.ecore import *
import pyecore.ecore as Ecore

from testEMF import NamedElement
from testEMF import Stuffs


class C(NamedElement):
    mystuff = EAttribute(eType=Stuffs)
    b = EReference()

    def __init__(self):
        super().__init__()
