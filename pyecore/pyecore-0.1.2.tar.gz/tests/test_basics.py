import pytest
from pyecore.ecore import *
import pyecore.ecore as Ecore

def test_ecore_URI():
    assert Ecore.nsURI == 'http://www.eclipse.org/emf/2002/Ecore'


def test_get_existing_EClassifier():
    assert Ecore.getEClassifier('EClass')


def test_get_nonexisting_EClassifier():
    assert not Ecore.getEClassifier('EEClass')


def test_ecoreutil_isinstance_none():
    assert EcoreUtils.isinstance(None, EClass)


def test_ecoreutil_isinstance_integer():
    assert EcoreUtils.isinstance(100, EInteger)


def test_ecoreutil_isinstance_string():
    assert EcoreUtils.isinstance('test', EString)


def test_ecoreutil_isinstance_boolean():
    assert EcoreUtils.isinstance(True, EBoolean)


def test_ecoreutil_isinstance_estringtostringmap():
    assert EcoreUtils.isinstance({3: '3'}, EStringToStringMapEntry)


def test_eenum_empty_instance():
    MyEnum = EEnum('MyEnum')
    assert not MyEnum.default_value
    assert not MyEnum.eLiterals


def test_eenum_simple_instance():
    MyEnum = EEnum('MyEnum', literals=['A', 'B', 'C'])
    assert MyEnum.default_value
    assert MyEnum.default_value is MyEnum.A


def test_eenum_simple_instance_with_defaultvalue():
    MyEnum = EEnum('MyEnum', literals=['A', 'B', 'C'], default_value='B')
    assert MyEnum.default_value
    assert MyEnum.default_value is MyEnum.B


def test_eenum_simple_instance_with_defaultvalue():
    with pytest.raises(AttributeError):
        MyEnum = EEnum('MyEnum', literals=['A', 'B', 'C'], default_value='D')


def test_eenum_simple_instance():
    MyEnum = EEnum('MyEnum', literals=['A', 'B', 'C'])
    assert EcoreUtils.isinstance(MyEnum.A, EEnumLiteral)


def test_eenum_simple_search():
    MyEnum = EEnum('MyEnum', literals=['A', 'B', 'C'])
    assert MyEnum.A in MyEnum
    assert 'A' in MyEnum


def test_eenum_geteenum():
    MyEnum = EEnum('MyEnum', literals=['A', 'B', 'C'])
    assert MyEnum.getEEnumLiteral(name='A') is MyEnum.A
    assert MyEnum.getEEnumLiteral(value=1) is MyEnum.B
    assert MyEnum.getEEnumLiteral('F') is None


def test_eenum_geteenum_print():
    MyEnum = EEnum('MyEnum', literals=['A', 'B', 'C'])
    print(MyEnum)


def test_eattribute_etype():
    eattribute = EAttribute('test')
    assert ETypedElement.eClass in eattribute.eClass.eAllSuperTypes()
    assert eattribute.eClass.findEStructuralFeature('eType')


def test_eobject_egetset_badtype():
    eattribute = EAttribute('eatt')
    with pytest.raises(TypeError):
        eattribute.eGet(4)
    with pytest.raises(TypeError):
        eattribute.eSet(4, 4)


def test_eobject_eget_simple():
    eattribute = EAttribute('eatt')
    assert eattribute.eGet('name') == 'eatt'
    name = eattribute.eClass.findEStructuralFeature('name')
    assert eattribute.eGet(name) == 'eatt'


def test_eobject_eget_many():
    A = EClass('A')
    assert A.eGet('eAttributes') == []
    eattributes = A.eClass.findEStructuralFeature('eAttributes')
    assert A.eGet(eattributes) == []
    a_name = EAttribute('a_name')
    A.eGet('eStructuralFeatures').append(a_name)
    assert A.eGet('eStructuralFeatures') != [] and A.eGet('eStructuralFeatures')[0] is a_name


def test_eobject_eset_simple():
    eattribute = EAttribute()
    assert eattribute.name is None
    eattribute.eSet('name', 'test')
    assert eattribute.name == 'test'
    name = eattribute.eClass.findEStructuralFeature('name')
    eattribute.eSet(name, 'test2')
    assert eattribute.name == 'test2'


def test_estructuralfeature_repr():
    eattribute = EAttribute()
    assert eattribute.__repr__() is not None


def test_urifragment_default():
    assert Ecore.default_eURIFragment() == '/'


def test_urifragment_ecore():
    assert Ecore.eURIFragment() == '#/'


def test_urifragment_static_ecore():
    assert EClass.eClass.eURIFragment() == '#//EClass'
    assert EPackage.eClass.eURIFragment() == '#//EPackage'
    assert EDataType.eClass.eURIFragment() == '#//EDataType'
