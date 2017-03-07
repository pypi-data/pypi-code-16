from yams.buildobjs import EntityType, RelationDefinition, String

from cubicweb.schema import WorkflowableEntityType


# Worklowable entity type to check the container structure ignores
# workflow-related rtypes.
class Agent(WorkflowableEntityType):
    """An agent (eg. person, group, software or physical artifact)."""
    name = String()


class clone_of(RelationDefinition):
    subject = 'Agent'
    object = 'Agent'
    cardinality = '?*'
    inlined = True


class knows(RelationDefinition):
    subject = 'Agent'
    object = 'Agent'
    symmetric = True


class OnlineAccount(EntityType):
    """An online account"""


class account(RelationDefinition):
    """Indicates an account held by an agent"""
    subject = 'Agent'
    object = 'OnlineAccount'
    cardinality = '*1'
    composite = 'subject'


class Biography(EntityType):
    """Biography"""


class biography(RelationDefinition):
    subject = 'Agent'
    object = 'Biography'
    cardinality = '?1'
    composite = 'subject'
    inlined = True


class Event(EntityType):
    """Event in the life of an Agent, gathered in its Biography"""


class Anecdote(EntityType):
    """Short story, not as important as an Event"""


class event(RelationDefinition):
    subject = 'Biography'
    object = ('Event', 'Anecdote')
    cardinality = '*1'
    composite = 'subject'


class narrated_by(RelationDefinition):
    subject = 'Anecdote'
    object = 'Agent'
    cardinality = '?*'
    composite = 'object'


class relates(RelationDefinition):
    subject = 'Anecdote'
    object = 'Event'
    cardinality = '?*'
    composite = 'subject'


class Comment(EntityType):
    """A comment comments things"""


class comments(RelationDefinition):
    subject = 'Comment'
    object = ('Comment', 'Anecdote')
    composite = 'object'
    cardinality = '1*'


class Group(EntityType):
    """A collection of individual agents"""


class member(RelationDefinition):
    """Indicates a member of a Group."""
    subject = 'Group'
    object = 'Agent'
