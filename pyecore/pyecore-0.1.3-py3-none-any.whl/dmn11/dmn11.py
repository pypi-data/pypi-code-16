from pyecore.ecore import *
import pyecore.ecore as Ecore

name = 'dmn11'
nsURI = 'http://www.omg.org/spec/DMN/20151101/dmn.xmi'
nsPrefix = 'dmn11'

eClass = Ecore.EPackage(name=name, nsURI=nsURI, nsPrefix=nsPrefix)

eSubpackages = []
eSuperPackage = None


HitPolicy = EEnum('HitPolicy', literals=['UNIQUE',
                                         'FIRST',
                                         'PRIORITY',
                                         'ANY',
                                         'COLLECT',
                                         'RULEORDER',
                                         'OUTPUTORDER'])

BuiltinAggregator = EEnum('BuiltinAggregator', literals=['SUM',
                                                         'COUNT',
                                                         'MIN',
                                                         'MAX'])

DecisionTableOrientation = EEnum('DecisionTableOrientation',
                                 literals=['RuleasRow',
                                           'RuleasColumn',
                                           'CrossTable'])
                                       
AssociationDirection = EEnum('AssociationDirection',
                             literals=['None',
                                       'One',
                                       'Both'])


class AuthorityRequirement(EModelElement, metaclass=MetaEClass):
    requiredAuthority = EReference(ordered=False)
    decision = EReference(ordered=False)
    bkm = EReference(ordered=False)
    knowledgeSource = EReference(ordered=False)
    requiredDecision = EReference(ordered=False)
    requiredInput = EReference(ordered=False)

    def __init__(self):
        super().__init__()


@abstract
class DMNElement(EModelElement, metaclass=MetaEClass):
    id = EAttribute(eType=EString)
    description = EAttribute(eType=EString)
    label = EAttribute(eType=EString)
    extensionAttribute = EReference(upper=-1, ordered=False, containment=True)
    extensionElements = EReference(upper=-1, ordered=False, containment=True)

    def __init__(self):
        super().__init__()


class ExtensionAttribute(EModelElement, metaclass=MetaEClass):
    value = EAttribute(eType=EStringToStringMapEntry, upper=-1)
    name = EAttribute(eType=EString)
    valueRef = EReference(ordered=False)
    element = EReference(ordered=False)

    def __init__(self):
        super().__init__()


@abstract
class Element(EModelElement, metaclass=MetaEClass):
    elements = EReference(ordered=False)
    extensionAttribute = EReference(ordered=False)

    def __init__(self):
        super().__init__()


class ExtensionElements(EModelElement, metaclass=MetaEClass):
    element = EReference(ordered=False)
    extensionElement = EReference(upper=-1, ordered=False, containment=True)

    def __init__(self):
        super().__init__()


class Import(EModelElement, metaclass=MetaEClass):
    importType = EAttribute(eType=EString)
    locationURI = EAttribute(eType=EString)
    namespace = EAttribute(eType=EString)
    definitions = EReference(ordered=False)

    def __init__(self):
        super().__init__()


class Binding(EModelElement, metaclass=MetaEClass):
    parameter = EReference(ordered=False, containment=True)
    bindingFormula = EReference(ordered=False, containment=True)
    invocation = EReference()

    def __init__(self):
        super().__init__()


class InformationRequirement(EModelElement, metaclass=MetaEClass):
    requiredInput = EReference(ordered=False)
    requiredDecision = EReference(ordered=False)
    decision = EReference(ordered=False)

    def __init__(self):
        super().__init__()


class KnowledgeRequirement(EModelElement, metaclass=MetaEClass):
    requiredKnowledge = EReference(ordered=False)
    bkm = EReference(ordered=False)
    decision = EReference(ordered=False)

    def __init__(self):
        super().__init__()


class ContextEntry(EModelElement, metaclass=MetaEClass):
    value = EReference(ordered=False, containment=True)
    context = EReference(ordered=False)
    variable = EReference(ordered=False, containment=True)

    def __init__(self):
        super().__init__()


@abstract
class NamedElement(DMNElement):
    name = EAttribute(eType=EString)

    def __init__(self):
        super().__init__()


class UnaryTests(DMNElement):
    expressionLanguage = EAttribute(eType=EString)
    text = EAttribute(eType=EString)
    ruleInput = EReference(ordered=False)
    output = EReference(ordered=False)
    input = EReference(ordered=False)
    allowedInItemDefinition = EReference(ordered=False)

    def __init__(self):
        super().__init__()


class DecisionRule(DMNElement):
    decisionTable = EReference(ordered=False)
    outputEntry = EReference(upper=-1, containment=True)
    inputEntry = EReference(upper=-1, containment=True)

    def __init__(self):
        super().__init__()


@abstract
class Expression(DMNElement):
    typeRef = EAttribute(eType=EString)
    formulaBinding = EReference(ordered=False)
    decision = EReference(ordered=False)
    functionDefinition = EReference(ordered=False)
    contextEntry = EReference(ordered=False)
    list = EReference(ordered=False)
    caller = EReference(ordered=False)
    type = EReference(ordered=False)

    def __init__(self):
        super().__init__()


class InputClause(DMNElement):
    inputExpression = EReference(ordered=False, containment=True)
    inputValues = EReference(ordered=False, containment=True)
    decisionTable = EReference(ordered=False)

    def __init__(self):
        super().__init__()


class OutputClause(DMNElement):
    name = EAttribute(eType=EString)
    typeRef = EAttribute(eType=EString)
    decisionTable = EReference(ordered=False)
    outputValues = EReference(ordered=False, containment=True)
    outputDefinition = EReference(ordered=False)
    defaultOutputEntry = EReference(ordered=False, containment=True)

    def __init__(self):
        super().__init__()


class ImportedValues(Import):
    expressionLanguage = EAttribute(eType=EString)
    importedElement = EAttribute(eType=EString)
    _ = EReference(ordered=False)

    def __init__(self):
        super().__init__()


@abstract
class Artifact(DMNElement):
    definitions = EReference(ordered=False)

    def __init__(self):
        super().__init__()


@abstract
class DRGElement(NamedElement):
    definitions = EReference(ordered=False)

    def __init__(self):
        super().__init__()


class Definitions(NamedElement):
    namespace = EAttribute(eType=EString)
    expressionLanguage = EAttribute(eType=EString)
    typeLanguage = EAttribute(eType=EString)
    exporter = EAttribute(eType=EString)
    exporterVersion = EAttribute(eType=EString)
    _import = EReference(upper=-1, ordered=False, containment=True)
    collection = EReference(upper=-1, ordered=False, containment=True)
    businessContextElement = EReference(upper=-1, ordered=False, containment=True)
    itemDefinition = EReference(upper=-1, ordered=False, containment=True)
    decisionService = EReference(upper=-1, ordered=False, containment=True)
    artifact = EReference(upper=-1, ordered=False, containment=True)
    drgElement = EReference(upper=-1, ordered=False, containment=True)

    def __init__(self):
        super().__init__()


class ElementCollection(NamedElement):
    drgElement = EReference(upper=-1, ordered=False)
    definitions = EReference(ordered=False)

    def __init__(self):
        super().__init__()


@abstract
class BusinessContextElement(NamedElement):
    URI = EAttribute(eType=EString)
    definitions = EReference(ordered=False)

    def __init__(self):
        super().__init__()


class ItemDefinition(NamedElement):
    typeLanguage = EAttribute(eType=EString)
    typeRef = EAttribute(eType=EString)
    isCollection = EAttribute(eType=EBoolean)
    allowedValues = EReference(ordered=False, containment=True)
    itemComponents = EReference(upper=-1, ordered=False, containment=True)
    containingDefinition = EReference(ordered=False)
    definitions = EReference(ordered=False)

    def __init__(self):
        super().__init__()


class DecisionTable(Expression):
    hitPolicy = EAttribute(eType=HitPolicy)
    aggregation = EAttribute(eType=BuiltinAggregator)
    preferredOrientation = EAttribute(eType=DecisionTableOrientation)
    outputLabel = EAttribute(eType=EString)
    input = EReference(upper=-1, containment=True)
    output = EReference(upper=-1, containment=True)
    rule = EReference(upper=-1, containment=True)

    def __init__(self):
        super().__init__()

    def __repr__(self):
        old = super().__repr__()
        # header = f'{self.hitPolicy} [{self.label}]'
        # rows = '|'
        # for i in self.input:
        #     rows += f' {i.inputValues} |'
        return old


class InformationItem(NamedElement):
    typeRef = EAttribute(eType=EString)
    decisionOutput = EReference(ordered=False)
    inputData = EReference(ordered=False)
    bkm = EReference(ordered=False)
    functionDefinition = EReference(ordered=False)
    contextEntry = EReference(ordered=False)
    relation = EReference(ordered=False)
    valueExpression = EReference(ordered=False)
    type = EReference(ordered=False)
    binding = EReference(ordered=False)

    def __init__(self):
        super().__init__()


class FunctionDefinition(Expression):
    formalParameter = EReference(upper=-1, ordered=False, containment=True)
    body = EReference(ordered=False, containment=True)
    bkm = EReference(ordered=False)

    def __init__(self):
        super().__init__()


class Context(Expression):
    contextEnrty = EReference(upper=-1, ordered=False, containment=True)

    def __init__(self):
        super().__init__()


class Relation(Expression):
    row = EReference(upper=-1, ordered=False, containment=True)
    column = EReference(upper=-1, ordered=False, containment=True)

    def __init__(self):
        super().__init__()


class List(Expression):
    element = EReference(upper=-1, ordered=False, containment=True)
    relation = EReference(ordered=False)

    def __init__(self):
        super().__init__()


class Invocation(Expression):
    calledFunction = EReference(ordered=False, containment=True)
    binding = EReference(upper=-1, containment=True)

    def __init__(self):
        super().__init__()


class LiteralExpression(Expression):
    expressionLanguage = EAttribute(eType=EString)
    text = EAttribute(eType=EString)
    ruleOutput = EReference(ordered=False)
    output = EReference(ordered=False)
    importedValues = EReference(ordered=False, containment=True)
    expressionInput = EReference(ordered=False)

    def __init__(self):
        super().__init__()


class DecisionService(NamedElement):
    outputDecision = EReference(upper=-1, ordered=False)
    encapsulatedDecision = EReference(upper=-1, ordered=False)
    inputDecision = EReference(upper=-1, ordered=False)
    inputData = EReference(upper=-1, ordered=False)
    definitions = EReference(ordered=False)

    def __init__(self):
        super().__init__()


class Association(Artifact):
    associationDirection = EAttribute(eType=AssociationDirection)
    sourceRef = EReference(ordered=False)
    targetRef = EReference(ordered=False)

    def __init__(self):
        super().__init__()


class TextAnnotation(Artifact):
    text = EAttribute(eType=EString)
    textFormat = EAttribute(eType=EString)

    def __init__(self):
        super().__init__()


class KnowledgeSource(DRGElement):
    type = EAttribute(eType=EString)
    locationURI = EAttribute(eType=EString)
    owner = EReference(ordered=False)
    authorityRequirement = EReference(upper=-1, ordered=False, containment=True)

    def __init__(self):
        super().__init__()


class Decision(DRGElement):
    question = EAttribute(eType=EString)
    allowedAnswers = EAttribute(eType=EString)
    supportedObjective = EAttribute(eType=EString, upper=-1)
    decisionLogic = EReference(ordered=False, containment=True)
    decisionMaker = EReference(upper=-1, ordered=False)
    decisionOwner = EReference(upper=-1, ordered=False)
    impactedPerformanceIndicator = EReference(upper=-1, ordered=False)
    authorityRequirement = EReference(upper=-1, ordered=False, containment=True)
    informationRequirement = EReference(upper=-1, ordered=False, containment=True)
    requiresInformation = EReference(upper=-1, ordered=False)
    knowledgeRequirement = EReference(upper=-1, ordered=False, containment=True)
    usingProcess = EReference(upper=-1, ordered=False)
    usingTask = EReference(upper=-1, ordered=False)
    variable = EReference(ordered=False, containment=True)

    def __init__(self):
        super().__init__()


class OrganisationalUnit(BusinessContextElement):
    decisionOwned = EReference(upper=-1, ordered=False)
    decisionMade = EReference(upper=-1, ordered=False)

    def __init__(self):
        super().__init__()


class PerformanceIndicator(BusinessContextElement):
    impactingDecision = EReference(upper=-1, ordered=False)

    def __init__(self):
        super().__init__()


class InputData(DRGElement):
    variable = EReference(ordered=False, containment=True)
    requiresInformation = EReference(upper=-1, ordered=False)

    def __init__(self):
        super().__init__()


class BusinessKnowledgeModel(DRGElement):
    authorityRequirement = EReference(upper=-1, ordered=False, containment=True)
    knowledgeRequirement = EReference(upper=-1, ordered=False, containment=True)
    parameter = EReference(upper=-1, ordered=False, containment=True)
    encapsulatedLogic = EReference(ordered=False, containment=True)
    encapsulatedDecisions = EReference(ordered=False)
    variable = EReference(ordered=False, containment=True)

    def __init__(self):
        super().__init__()
