from cubicweb.predicates import has_related_entities, is_instance

from cubicweb_compound import structure_def
from cubicweb_compound.entities import IClonableAdapter, IContained, IContainer
from cubicweb_compound.views import CloneAction


def agent_structure_def(schema):
    return structure_def(schema, 'Agent').items()


class AgentIClonableAdapter(IClonableAdapter):
    rtype = 'clone_of'


class AgentInGroupIClonableAdapter(IClonableAdapter):
    """IClonable for Agent member of a Group, following `member` relation for
    cloning.
    """
    __select__ = (IClonableAdapter.__select__
                  & has_related_entities('member', role='object'))
    rtype = 'clone_of'
    follow_relations = [('member', 'object')]


class AgentCloneAction(CloneAction):
    __select__ = CloneAction.__select__ & is_instance('Agent')


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__)
    vreg.register(IContainer.build_class('Agent'))
    for etype, parent_relations in agent_structure_def(vreg.schema):
        IContained.register_class(vreg, etype, parent_relations)
