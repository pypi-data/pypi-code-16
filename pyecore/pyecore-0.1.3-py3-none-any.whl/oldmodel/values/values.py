from pyecore.ecore import *
import pyecore.ecore as Ecore
from model import ISynchable
from model import Node

name = 'values'
nsURI = 'https://raw.githubusercontent.com/openworm/org.geppetto.model/development/src/main/resources/geppettoModel.ecore#//values'
nsPrefix = 'gep'

eClass = Ecore.EPackage(name=name, nsURI=nsURI, nsPrefix=nsPrefix)

Connectivity = EEnum('Connectivity', literals=['DIRECTIONAL','BIDIRECTIONAL','NON_DIRECTIONAL',])
ImageFormat = EEnum('ImageFormat', literals=['PNG','JPEG','IIP',])


class StringToValueMap(EObject, metaclass=MetaEClass):
    key = EAttribute(eType=EString)
    value = EReference()

    def __init__(self):
        super().__init__()


class PointerElement(EObject, metaclass=MetaEClass):
    index = EAttribute(eType=EInteger)
    variable = EReference()
    type = EReference()

    def __init__(self):
        super().__init__()


class FunctionPlot(EObject, metaclass=MetaEClass):
    title = EAttribute(eType=EString)
    xAxisLabel = EAttribute(eType=EString)
    yAxisLabel = EAttribute(eType=EString)
    initialValue = EAttribute(eType=EInteger)
    finalValue = EAttribute(eType=EInteger)
    stepValue = EAttribute(eType=EInteger)

    def __init__(self):
        super().__init__()


class SkeletonTransformation(EObject, metaclass=MetaEClass):
    skeletonTransformation = EAttribute(eType=EInteger, upper=-1)

    def __init__(self):
        super().__init__()


@abstract
class Value(ISynchable):
    def __init__(self):
        super().__init__()


class Composite(Value):
    value = EReference(upper=-1, containment=True)

    def __init__(self):
        super().__init__()


class Quantity(Value):
    scalingFactor = EAttribute(eType=EInteger)
    value = EAttribute(eType=EDouble)

    def __init__(self):
        super().__init__()


class Unit(Value):
    unit = EAttribute(eType=EString)

    def __init__(self):
        super().__init__()


class TimeSeries(Value):
    scalingFactor = EAttribute(eType=EInteger)
    value = EAttribute(eType=EInteger, upper=-1)
    unit = EReference(containment=True)

    def __init__(self):
        super().__init__()


@abstract
class MetadataValue(Value):
    def __init__(self):
        super().__init__()


class Pointer(Value):
    elements = EReference(upper=-1, containment=True)
    point = EReference(containment=True)

    def __init__(self):
        super().__init__()

    def getInstancePath(self, ):
        raise NotImplementedError('Operation getInstancePath(...) is not yet implemented')


class Point(Value):
    x = EAttribute(eType=EInteger)
    y = EAttribute(eType=EInteger)
    z = EAttribute(eType=EInteger)

    def __init__(self):
        super().__init__()


class Dynamics(Value):
    initialCondition = EReference(containment=True)
    dynamics = EReference(containment=True)

    def __init__(self):
        super().__init__()


class Function(Value):
    arguments = EReference(upper=-1, containment=True)
    expression = EReference(containment=True)
    functionPlot = EReference(containment=True)

    def __init__(self):
        super().__init__()


class Argument(Value):
    argument = EAttribute(eType=EString)

    def __init__(self):
        super().__init__()


class Expression(Value):
    expression = EAttribute(eType=EString)

    def __init__(self):
        super().__init__()


@abstract
class VisualValue(Value):
    groupElements = EReference(upper=-1)
    position = EReference(containment=True)

    def __init__(self):
        super().__init__()


class VisualGroupElement(Node):
    defaultColor = EAttribute(eType=EString)
    parameter = EReference(containment=True)

    def __init__(self):
        super().__init__()


class VisualGroup(Node):
    lowSpectrumColor = EAttribute(eType=EString)
    highSpectrumColor = EAttribute(eType=EString)
    type = EAttribute(eType=EString)
    visualGroupElements = EReference(upper=-1, containment=True)

    def __init__(self):
        super().__init__()


class Connection(Value):
    connectivity = EAttribute(eType=Connectivity)
    a = EReference(containment=True)
    b = EReference(containment=True)

    def __init__(self):
        super().__init__()


class ArrayElement(Value):
    index = EAttribute(eType=EInteger)
    position = EReference(containment=True)
    initialValue = EReference(containment=True)

    def __init__(self):
        super().__init__()


class ArrayValue(Value):
    elements = EReference(upper=-1, containment=True)

    def __init__(self):
        super().__init__()


class Image(Value):
    data = EAttribute(eType=EString)
    name = EAttribute(eType=EString)
    reference = EAttribute(eType=EString)
    format = EAttribute(eType=ImageFormat)

    def __init__(self):
        super().__init__()


class ImportValue(Value):
    modelInterpreterId = EAttribute(eType=EString)

    def __init__(self):
        super().__init__()


class PhysicalQuantity(Quantity):
    unit = EReference(containment=True)

    def __init__(self):
        super().__init__()


class Text(MetadataValue):
    text = EAttribute(eType=EString)

    def __init__(self):
        super().__init__()


class URL(MetadataValue):
    url = EAttribute(eType=EString)

    def __init__(self):
        super().__init__()


class HTML(MetadataValue):
    html = EAttribute(eType=EString)

    def __init__(self):
        super().__init__()


class Collada(VisualValue):
    collada = EAttribute(eType=EString)

    def __init__(self):
        super().__init__()


class OBJ(VisualValue):
    obj = EAttribute(eType=EString)

    def __init__(self):
        super().__init__()


class Sphere(VisualValue):
    radius = EAttribute(eType=EInteger)

    def __init__(self):
        super().__init__()


class Cylinder(VisualValue):
    bottomRadius = EAttribute(eType=EInteger)
    topRadius = EAttribute(eType=EInteger)
    height = EAttribute(eType=EInteger)
    distal = EReference(containment=True)

    def __init__(self):
        super().__init__()


class SkeletonAnimation(VisualValue):
    skeletonTransformationSeries = EReference(upper=-1)

    def __init__(self):
        super().__init__()


class Particle(VisualValue, Point):
    def __init__(self):
        super().__init__()
