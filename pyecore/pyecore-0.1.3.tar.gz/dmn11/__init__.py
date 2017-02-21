import pyecore.ecore as Ecore
from pyecore.ecore import EObject
from .dmn11 import getEClassifier, eClassifiers
from .dmn11 import name, nsURI, nsPrefix, eClass, eSubpackages, eSuperPackage
from .dmn11 import AuthorityRequirement, KnowledgeSource, DRGElement, NamedElement, DMNElement, ExtensionAttribute, Element, ExtensionElements, Definitions, Import, ElementCollection, BusinessContextElement, ItemDefinition, UnaryTests, DecisionRule, DecisionTable, Expression, Binding, InformationItem, Decision, OrganisationalUnit, PerformanceIndicator, InformationRequirement, InputData, KnowledgeRequirement, BusinessKnowledgeModel, FunctionDefinition, ContextEntry, Context, Relation, List, Invocation, HitPolicy, InputClause, LiteralExpression, OutputClause, ImportedValues, BuiltinAggregator, DecisionTableOrientation, DecisionService, Artifact, Association, AssociationDirection, TextAnnotation
from . import dmn11

__all__ = ['AuthorityRequirement', 'KnowledgeSource', 'DRGElement', 'NamedElement', 'DMNElement', 'ExtensionAttribute', 'Element', 'ExtensionElements', 'Definitions', 'Import', 'ElementCollection', 'BusinessContextElement', 'ItemDefinition', 'UnaryTests', 'DecisionRule', 'DecisionTable', 'Expression', 'Binding', 'InformationItem', 'Decision', 'OrganisationalUnit', 'PerformanceIndicator', 'InformationRequirement', 'InputData', 'KnowledgeRequirement', 'BusinessKnowledgeModel', 'FunctionDefinition', 'ContextEntry', 'Context', 'Relation', 'List', 'Invocation', 'HitPolicy', 'InputClause', 'LiteralExpression', 'OutputClause', 'ImportedValues', 'BuiltinAggregator', 'DecisionTableOrientation', 'DecisionService', 'Artifact', 'Association', 'AssociationDirection', 'TextAnnotation']

# Non opposite EReferences
AuthorityRequirement.requiredAuthority.eType = KnowledgeSource
AuthorityRequirement.requiredDecision.eType = Decision
AuthorityRequirement.requiredInput.eType = InputData
KnowledgeSource.owner.eType = OrganisationalUnit
ExtensionAttribute.valueRef.eType = EObject
Element.elements.eType = ExtensionElements
Element.extensionAttribute.eType = ExtensionAttribute
ExtensionElements.extensionElement.eType = EObject
ElementCollection.drgElement.eType = DRGElement
Expression.type.eType = ItemDefinition
InformationItem.valueExpression.eType = Expression
InformationItem.type.eType = ItemDefinition
Decision.usingProcess.eType = EObject
Decision.usingTask.eType = EObject
KnowledgeRequirement.requiredKnowledge.eType = BusinessKnowledgeModel
BusinessKnowledgeModel.encapsulatedDecisions.eType = ElementCollection
BusinessKnowledgeModel.variable.eType = InformationItem
OutputClause.outputDefinition.eType = ItemDefinition
DecisionService.outputDecision.eType = Decision
DecisionService.encapsulatedDecision.eType = Decision
DecisionService.inputDecision.eType = Decision
DecisionService.inputData.eType = InputData
Association.sourceRef.eType = DMNElement
Association.targetRef.eType = DMNElement

# opposite EReferences
AuthorityRequirement.decision.eType = Decision
AuthorityRequirement.bkm.eType = BusinessKnowledgeModel
AuthorityRequirement.knowledgeSource.eType = KnowledgeSource
KnowledgeSource.authorityRequirement.eType = AuthorityRequirement
KnowledgeSource.authorityRequirement.eOpposite = AuthorityRequirement.knowledgeSource
DRGElement.definitions.eType = Definitions
DMNElement.extensionAttribute.eType = ExtensionAttribute
DMNElement.extensionElements.eType = ExtensionElements
ExtensionAttribute.element.eType = DMNElement
ExtensionAttribute.element.eOpposite = DMNElement.extensionAttribute
ExtensionElements.element.eType = DMNElement
ExtensionElements.element.eOpposite = DMNElement.extensionElements
Definitions._import.eType = Import
Definitions.collection.eType = ElementCollection
Definitions.businessContextElement.eType = BusinessContextElement
Definitions.itemDefinition.eType = ItemDefinition
Definitions.decisionService.eType = DecisionService
Definitions.artifact.eType = Artifact
Definitions.drgElement.eType = DRGElement
Definitions.drgElement.eOpposite = DRGElement.definitions
Import.definitions.eType = Definitions
Import.definitions.eOpposite = Definitions._import
ElementCollection.definitions.eType = Definitions
ElementCollection.definitions.eOpposite = Definitions.collection
BusinessContextElement.definitions.eType = Definitions
BusinessContextElement.definitions.eOpposite = Definitions.businessContextElement
ItemDefinition.allowedValues.eType = UnaryTests
ItemDefinition.itemComponents.eType = ItemDefinition
ItemDefinition.containingDefinition.eType = ItemDefinition
ItemDefinition.containingDefinition.eOpposite = ItemDefinition.itemComponents
ItemDefinition.definitions.eType = Definitions
ItemDefinition.definitions.eOpposite = Definitions.itemDefinition
UnaryTests.ruleInput.eType = DecisionRule
UnaryTests.output.eType = OutputClause
UnaryTests.input.eType = InputClause
UnaryTests.allowedInItemDefinition.eType = ItemDefinition
UnaryTests.allowedInItemDefinition.eOpposite = ItemDefinition.allowedValues
DecisionRule.decisionTable.eType = DecisionTable
DecisionRule.outputEntry.eType = LiteralExpression
DecisionRule.inputEntry.eType = UnaryTests
DecisionRule.inputEntry.eOpposite = UnaryTests.ruleInput
DecisionTable.input.eType = InputClause
DecisionTable.output.eType = OutputClause
DecisionTable.rule.eType = DecisionRule
DecisionTable.rule.eOpposite = DecisionRule.decisionTable
Expression.formulaBinding.eType = Binding
Expression.decision.eType = Decision
Expression.functionDefinition.eType = FunctionDefinition
Expression.contextEntry.eType = ContextEntry
Expression.list.eType = List
Expression.caller.eType = Invocation
Binding.parameter.eType = InformationItem
Binding.bindingFormula.eType = Expression
Binding.bindingFormula.eOpposite = Expression.formulaBinding
Binding.invocation.eType = Invocation
InformationItem.decisionOutput.eType = Decision
InformationItem.inputData.eType = InputData
InformationItem.bkm.eType = BusinessKnowledgeModel
InformationItem.functionDefinition.eType = FunctionDefinition
InformationItem.contextEntry.eType = ContextEntry
InformationItem.relation.eType = Relation
InformationItem.binding.eType = Binding
InformationItem.binding.eOpposite = Binding.parameter
Decision.decisionLogic.eType = Expression
Decision.decisionLogic.eOpposite = Expression.decision
Decision.decisionMaker.eType = OrganisationalUnit
Decision.decisionOwner.eType = OrganisationalUnit
Decision.impactedPerformanceIndicator.eType = PerformanceIndicator
Decision.authorityRequirement.eType = AuthorityRequirement
Decision.authorityRequirement.eOpposite = AuthorityRequirement.decision
Decision.informationRequirement.eType = InformationRequirement
Decision.requiresInformation.eType = InformationRequirement
Decision.knowledgeRequirement.eType = KnowledgeRequirement
Decision.variable.eType = InformationItem
Decision.variable.eOpposite = InformationItem.decisionOutput
OrganisationalUnit.decisionOwned.eType = Decision
OrganisationalUnit.decisionOwned.eOpposite = Decision.decisionOwner
OrganisationalUnit.decisionMade.eType = Decision
OrganisationalUnit.decisionMade.eOpposite = Decision.decisionMaker
PerformanceIndicator.impactingDecision.eType = Decision
PerformanceIndicator.impactingDecision.eOpposite = Decision.impactedPerformanceIndicator
InformationRequirement.requiredInput.eType = InputData
InformationRequirement.requiredDecision.eType = Decision
InformationRequirement.requiredDecision.eOpposite = Decision.requiresInformation
InformationRequirement.decision.eType = Decision
InformationRequirement.decision.eOpposite = Decision.informationRequirement
InputData.variable.eType = InformationItem
InputData.variable.eOpposite = InformationItem.inputData
InputData.requiresInformation.eType = InformationRequirement
InputData.requiresInformation.eOpposite = InformationRequirement.requiredInput
KnowledgeRequirement.bkm.eType = BusinessKnowledgeModel
KnowledgeRequirement.decision.eType = Decision
KnowledgeRequirement.decision.eOpposite = Decision.knowledgeRequirement
BusinessKnowledgeModel.authorityRequirement.eType = AuthorityRequirement
BusinessKnowledgeModel.authorityRequirement.eOpposite = AuthorityRequirement.bkm
BusinessKnowledgeModel.knowledgeRequirement.eType = KnowledgeRequirement
BusinessKnowledgeModel.knowledgeRequirement.eOpposite = KnowledgeRequirement.bkm
BusinessKnowledgeModel.parameter.eType = InformationItem
BusinessKnowledgeModel.parameter.eOpposite = InformationItem.bkm
BusinessKnowledgeModel.encapsulatedLogic.eType = FunctionDefinition
FunctionDefinition.formalParameter.eType = InformationItem
FunctionDefinition.formalParameter.eOpposite = InformationItem.functionDefinition
FunctionDefinition.body.eType = Expression
FunctionDefinition.body.eOpposite = Expression.functionDefinition
FunctionDefinition.bkm.eType = BusinessKnowledgeModel
FunctionDefinition.bkm.eOpposite = BusinessKnowledgeModel.encapsulatedLogic
ContextEntry.value.eType = Expression
ContextEntry.value.eOpposite = Expression.contextEntry
ContextEntry.context.eType = Context
ContextEntry.variable.eType = InformationItem
ContextEntry.variable.eOpposite = InformationItem.contextEntry
Context.contextEnrty.eType = ContextEntry
Context.contextEnrty.eOpposite = ContextEntry.context
Relation.row.eType = List
Relation.column.eType = InformationItem
Relation.column.eOpposite = InformationItem.relation
List.element.eType = Expression
List.element.eOpposite = Expression.list
List.relation.eType = Relation
List.relation.eOpposite = Relation.row
Invocation.calledFunction.eType = Expression
Invocation.calledFunction.eOpposite = Expression.caller
Invocation.binding.eType = Binding
Invocation.binding.eOpposite = Binding.invocation
InputClause.inputExpression.eType = LiteralExpression
InputClause.inputValues.eType = UnaryTests
InputClause.inputValues.eOpposite = UnaryTests.input
InputClause.decisionTable.eType = DecisionTable
InputClause.decisionTable.eOpposite = DecisionTable.input
LiteralExpression.ruleOutput.eType = DecisionRule
LiteralExpression.ruleOutput.eOpposite = DecisionRule.outputEntry
LiteralExpression.output.eType = OutputClause
LiteralExpression.importedValues.eType = ImportedValues
LiteralExpression.expressionInput.eType = InputClause
LiteralExpression.expressionInput.eOpposite = InputClause.inputExpression
OutputClause.decisionTable.eType = DecisionTable
OutputClause.decisionTable.eOpposite = DecisionTable.output
OutputClause.outputValues.eType = UnaryTests
OutputClause.outputValues.eOpposite = UnaryTests.output
OutputClause.defaultOutputEntry.eType = LiteralExpression
OutputClause.defaultOutputEntry.eOpposite = LiteralExpression.output
ImportedValues._.eType = LiteralExpression
ImportedValues._.eOpposite = LiteralExpression.importedValues
DecisionService.definitions.eType = Definitions
DecisionService.definitions.eOpposite = Definitions.decisionService
Artifact.definitions.eType = Definitions
Artifact.definitions.eOpposite = Definitions.artifact


# Manage all other EClassifiers (EEnum, EDatatypes...)
otherClassifiers = [HitPolicy, BuiltinAggregator, DecisionTableOrientation, AssociationDirection]
for classif in otherClassifiers:
    eClassifiers[classif.name] = classif
    classif._container = dmn11

for classif in eClassifiers.values():
    eClass.eClassifiers.append(classif.eClass)

for subpack in eSubpackages:
    eClass.eSubpackages.append(subpack.eClass)
