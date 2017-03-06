# encoding: utf-8
# Copyright 2012–2017 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Bespoke page.'''

from Acquisition import aq_inner
from edrnsite.vanity import MESSAGE_FACTORY as _
from eke.biomarker.interfaces import IBiomarker
from eke.ecas.interfaces import IDataset
from eke.site.interfaces import IPerson
from eke.study.interfaces import IProtocol
from five import grok
from plone.directives import dexterity, form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.memoize import view
from plone.namedfile.field import NamedImage
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.component import getMultiAdapter
import re, plone.api


_mboxRE = re.compile(r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$', re.IGNORECASE)


def _checkEmail(value):
    '''Check if the given value is an email address.'''
    return _mboxRE.match(value) is not None


class IBespokePage(form.Schema):
    '''A bespoke page.'''
    title = schema.TextLine(
        title=_(u'Name'),
        description=_(u"Enter your name, as you'd like it to appear."),
        required=True,
    )
    description = schema.Text(
        title=_(u'Description'),
        description=_(u'Type up a short summary. You might include research interests, personal background, funny quirks, etc.'),
        required=False,
    )
    showMbox = schema.Bool(
        title=_(u'Show My Email'),
        description=_(u'Check the box if you want your email address displayed publicly. Leave it unchecked to keep it hidden.'),
        required=False,
    )
    edrnTitle = schema.TextLine(
        title=_(u'EDRN Title'),
        description=_(u'Title or honorific given by the Early Detection Research Network'),
        required=False,
    )
    specialty = schema.TextLine(
        title=_(u'Specialty'),
        description=_(u'Your area of specialization.'),
        required=False,
    )
    photograph = NamedImage(
        title=_(u'Photograph'),
        description=_(u'Upload a photograph of yourself. Please, keep it tasteful.'),
        required=False,
    )
    dexterity.write_permission(memberType='cmf.ManagePortal')
    memberType = schema.TextLine(
        title=_(u'Member Type'),
        description=_(u'What particular kind of member site this.'),
        required=False,
    )
    dexterity.write_permission(piUID='cmf.ManagePortal')
    piUID = schema.TextLine(
        title=_(u'PI UID'),
        description=_(u'Unique identifier of the principal investigator of the site where this person works.'),
        required=False,
    )
    dexterity.write_permission(person='cmf.ManagePortal')
    person = RelationChoice(
        title=_(u'Person'),
        description=_(u'The DMCC-generated "Person" page within the portal that matches this bespoke page.'),
        required=False,
        source=ObjPathSourceBinder(object_provides=IPerson.__identifier__)
    )


class View(grok.View):
    '''View for a bespoke page.'''
    grok.context(IBespokePage)
    grok.require('zope2.View')
    def isMine(self):
        context = aq_inner(self.context)
        state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        if state.anonymous():
            return False
        userID = state.member().getUser().getId()
        pageOwnerID = context.getOwner().getId()
        if userID != pageOwnerID:
            return False
        contextState = getMultiAdapter((context, self.request), name=u'plone_context_state')
        return contextState.is_editable()
    def _getWorkflowState(self):
        context = aq_inner(self.context)
        contextState = getMultiAdapter((context, self.request), name=u'plone_context_state')
        return contextState.workflow_state()
    def isPublic(self):
        return self._getWorkflowState() in ('public', 'visible')
    def isPrivate(self):
        return self._getWorkflowState() == 'private'
    def _getCanonicalURL(self):
        context = aq_inner(self.context)
        contextState = getMultiAdapter((context, self.request), name=u'plone_context_state')
        return contextState.canonical_object_url()
    def editURL(self):
        return self._getCanonicalURL() + '/edit'
    def publishURL(self):
        return self._getCanonicalURL() + '/content_status_modify?workflow_action=show'
    def privateURL(self):
        return self._getCanonicalURL() + '/content_status_modify?workflow_action=hide'
    @view.memoize
    def protocols(self):
        context = aq_inner(self.context)
        catalog = plone.api.portal.get_tool('portal_catalog')
        results = catalog(
            object_provides=IProtocol.__identifier__,
            sort_on='sortable_title',
            piUID=context.piUID
        )
        actives, inactives = [], []
        for i in results:
            protocol = i.getObject()
            if protocol.finishDate:
                inactives.append(protocol)
            else:
                actives.append(protocol)
        return actives, inactives
    @view.memoize
    def biomarkers(self):
        context = aq_inner(self.context)
        catalog = plone.api.portal.get_tool('portal_catalog')
        results = catalog(
            object_provides=IBiomarker.__identifier__,
            sort_on='sortable_title',
            piUIDs=[context.piUID]
        )
        return [{
            'title': i['Title'].decode('utf-8'),
            'description': i['Description'].decode('utf-8'),
            'url': i.getURL()
        } for i in results]
    @view.memoize
    def datasets(self):
        context = aq_inner(self.context)
        piUID = context.piUID
        catalog = plone.api.portal.get_tool('portal_catalog')
        results = catalog(object_provides=IDataset.__identifier__, sort_on='sortable_title')
        # Sadly we have to wake each dataset since the 'piUIDs' field isn't getting indexed, possibly
        # because it's a computed field.
        return [{
            'title': i['Title'].decode('utf-8'),
            'description': i['Description'].decode('utf-8'),
            'url': i.getURL()
        } for i in results if piUID in i.getObject().piUIDs]
