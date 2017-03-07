# copyright 2015-2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-prov schema"""

from yams.buildobjs import EntityType, RelationType, String, RichString, TZDatetime
from yams.constraints import BoundaryConstraint, Attribute

from cubicweb import _


class Activity(EntityType):
    """An activity is something that occurs over a period of time and acts
    upon or with entities; it may include consuming, processing, transforming,
    modifying, relocating, using, or generating entities.
    """
    # See http://www.w3.org/TR/2013/NOTE-prov-dc-20130430/#prov-refinements
    type = String(internationalizable=True,
                  vocabulary=[_('publish'), _('contribute'), _('create'),
                              _('right_assignement'), _('modify'),
                              _('accept'), _('copyright'), _('submit'),
                              _('replace')])
    description = RichString(fulltextindexed=True)
    start = TZDatetime(constraints=[BoundaryConstraint('<=', Attribute('end'))],
                       description=_('when the activity started'))
    end = TZDatetime(constraints=[BoundaryConstraint('>=', Attribute('start'))],
                     description=_('when the activity ended'))


class associated_with(RelationType):
    """An activity association is an assignment of responsibility to an agent
    for an activity, indicating that the agent had a role in the activity. It
    further allows for a plan to be specified, which is the plan intended by
    the agent to achieve some goals in the context of this activity.
    """
    subject = 'Activity'
    cardinality = '?*'
    description = _('the agent responsible for this activity')


class generated(RelationType):
    """Relate an Activity to an other entity, which is the product of the
    activity.
    """
    subject = 'Activity'
    cardinality = '?*'
    inlined = True
    description = _('completion of production of a new entity by an activity')
    composite = 'object'


class used(RelationType):
    """Relate an Activity to an other entity, which is used as the source of
    the activity (usually for the production of an other entity through the
    `generated` relation).
    """
    subject = 'Activity'
    cardinality = '?*'
    inlined = True
    description = _('beginning of utilizing an entity by an activity')
    composite = 'object'


class derived_from(RelationType):
    """Relate an Entity to an other entity, through a process of derivation
    which can be a transformation of an entity into another, an update of an
    entity resulting in a new one, or the construction of a new entity based
    on a pre-existing entity.
    """
    description = _('entity used in a derivation process resulting in another '
                    'entity or a modification of the entity')
