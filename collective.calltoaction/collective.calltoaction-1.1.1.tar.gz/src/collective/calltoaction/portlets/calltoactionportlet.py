# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from collective.calltoaction import _
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.portlets.interfaces import IPortletDataProvider
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.formlib import form
from zope.interface import implements

import random
import re
import string


try:
    # On Plone 4 we need special widgets
    from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget
    from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
except ImportError:
    # On Plone 5 not.
    WYSIWYGWidget = None
    UberSelectionWidget = None

# List of interfaces of image types.
IMAGE_IFACES = []
try:
    # Archetypes
    from Products.ATContentTypes.interfaces.image import IImageContent
    IMAGE_IFACES.append(IImageContent.__identifier__)
except ImportError:
    pass
try:
    # Dexterity.  Note: this only works when the type has an image as primary
    # field.
    from plone.namedfile.interfaces import IImageScaleTraversable
    IMAGE_IFACES.append(IImageScaleTraversable.__identifier__)
except ImportError:
    pass


def random_version():
    return ''.join(random.sample(string.ascii_letters, 16))


class ICallToActionPortlet(IPortletDataProvider):
    """A schema for the call to action portlet.
    """

    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"Title of the rendered portlet"),
        constraint=re.compile("[^\s]").match,
        required=False)

    image_ref = schema.Choice(
        title=_(u"Image"),
        required=False,
        source=SearchableTextSourceBinder(
            {'object_provides': IMAGE_IFACES},
            default_query='path:'))

    image_size = schema.Int(
        title=_(u'Image size'),
        description=_(
            u'The height and width in pixels. The image will be scaled '
            u'to fit within the given height and width.'),
        default=200,
        required=True)

    form_ref = schema.Choice(
        title=_(u"Form"),
        required=False,
        source=SearchableTextSourceBinder(
            {'portal_type': 'FormFolder'},
            default_query='path:'))

    text = schema.Text(
        title=_(u"Text"),
        description=_(u"The text to render"),
        required=True)

    milli_seconds_until_overlay = schema.Int(
        title=_(u'Milliseconds until overlay'),
        description=_(
            u'The number of milliseconds we wait before showing the overlay.'),
        default=0,
        required=True)

    new_version = schema.Bool(
        title=_(u'This is a new call to action'),
        description=_(
            u'Checking this option means everyone will get to see the new '
            u'overlay. When not checked, visitors who have already seen '
            u'the overlay will not see it again.'),
        default=False,
        required=False)


class Assignment(base.Assignment):
    """Portlet assignment.
    """

    implements(ICallToActionPortlet)

    header = _(u'title_call_to_action_portlet',
               default=u'Call to action portlet')
    image_ref = ''
    image_size = 200
    form_ref = ''
    text = u""
    milli_seconds_until_overlay = 0
    new_version = False
    version = ''

    def __init__(
            self,
            header=u"",
            image_ref='',
            image_size=200,
            form_ref='',
            text=u"",
            milli_seconds_until_overlay=0,
            new_version=False,
            ):
        self.header = header
        self.image_ref = image_ref
        self.image_size = image_size
        self.form_ref = form_ref
        self.text = text
        self.milli_seconds_until_overlay = milli_seconds_until_overlay
        self.new_version = new_version
        self.version = random_version()

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        'manage portlets' screen. Here, we use the title that the user gave or
        static string if title not defined.
        """
        return self.header or _(
            u'title_call_to_action_portlet',
            default=u'Call to action portlet')


class Renderer(base.Renderer):
    """Portlet renderer.

    We want to show nothing here by default.  The rendering should be
    handled by a viewlet.  Reason: if this is the only available
    portlet, then a portlet column will be shown even though we do not
    want to show anything initially.  Our content is only meant to be
    shown in a overlay.

    We do keep the 'render' method, so the viewlet can call this.
    """

    index = ViewPageTemplateFile('calltoactionportlet.pt')

    # If we reference a form, and we *are* on that form,
    # then we don't need to show anything.
    form_is_context = False

    @property
    def available(self):
        return 'debug_calltoaction' in self.request

    def render(self, orig_context=None):
        # Get the embedded form, if any.
        self.embedded_form = self.get_embedded_form(orig_context=orig_context)
        # The above call may have set self.form_is_context to True.
        # We do not want to show the portlet then.  Biggest reason is:
        # when we show the viewlet/portlet on say the homepage, and
        # the user submits the form and gets a validation error,
        # then the we update the contents of the homepage portlet to show
        # the form as we find it in the resulting page.  But the form may then
        # be there twice: once in the content area, and once in the portlet
        # that we see on that form page.  A bit hard to wrap your head around.
        if self.form_is_context:
            return u''
        return self.index()

    def css_class(self):
        """Generate a CSS class from the portlet header
        """
        header = self.data.header
        if header:
            normalizer = getUtility(IIDNormalizer)
            return "portlet-calltoaction-%s" % normalizer.normalize(header)
        return "portlet-calltoaction"

    def transformed(self, mt='text/x-html-safe'):
        """Use the safe_html transform to protect text output. This also
        ensures that resolve UID links are transformed into real links.
        """
        orig = self.data.text
        context = aq_inner(self.context)
        # Portal transforms needs encoded strings
        orig = orig.encode('utf-8')

        transformer = getToolByName(context, 'portal_transforms')
        transformer_context = context
        if hasattr(self, '__portlet_metadata__'):
            if ('category' in self.__portlet_metadata__ and
                    self.__portlet_metadata__['category'] == 'context'):
                assignment_context_path = self.__portlet_metadata__['key']
                assignment_context = context.unrestrictedTraverse(
                    assignment_context_path)
                transformer_context = assignment_context
        data = transformer.convertTo(
            mt, orig, context=transformer_context, mimetype='text/html')
        result = data.getData()
        if result:
            if isinstance(result, str):
                return unicode(result, 'utf-8')
            return result
        return None

    def get_image_tag(self):
        """
        return the image tag
        """
        image = self._get_reference_object(self.data.image_ref)
        if image:
            size = self.data.image_size
            try:
                scales = image.restrictedTraverse('@@images')
                scale = scales.scale('image', height=size*2, width=size*2)
                tag = scale.tag(height=size, width=size)
                return tag
            except AttributeError:
                tag = image.tag(height=size, width=size)
                if image.getField('image').get_size(image) > 0:
                    return tag
                else:
                    return ""
        else:
            return ""

    def get_embedded_form(self, orig_context=None):
        """Return the embedded view of the FormFolder."""
        form = self._get_reference_object(self.data.form_ref)
        if form is None:
            return u""
        # Check if the form and the context are the same.
        if orig_context is None:
            orig_context = self.context
        if form == orig_context:
            self.form_is_context = True
            return u""
        if form.portal_type != 'FormFolder':
            # Form got removed and something else added with the same id?
            return u""
        view = form.restrictedTraverse('fg_embedded_view_p3', None)
        if view is None:
            return u""
        return view()

    def _get_reference_object(self, path):
        """Get the referenced object.

        This is an image or a FormFolder.
        """
        if not path:
            return None
        pps = getMultiAdapter(
            (self.context, self.request), name='plone_portal_state')
        root = pps.portal()
        return root.restrictedTraverse(path.strip('/'), None)


class AddForm(base.AddForm):
    """Portlet add form."""
    form_fields = form.Fields(ICallToActionPortlet)
    form_fields['image_ref'].custom_widget = UberSelectionWidget
    form_fields['form_ref'].custom_widget = UberSelectionWidget
    if WYSIWYGWidget is not None:
        form_fields['text'].custom_widget = WYSIWYGWidget
    form_fields = form_fields.omit('new_version')
    label = _(
        u'title_add_calltoaction_portlet',
        default=u'Add call to action portlet')
    description = _(
        u'description_calltoaction_portlet',
        default=u'A portlet which displays a call to action overlay '
        'after waiting for some seconds.')

    def create(self, data):
        path = '/'.join(self.context.getPhysicalPath())
        if not ('plone.leftcolumn' in path or 'plone.rightcolumn' in path):
            raise ValueError('Sorry, this portlet is only supported '
                             'in left and right columns.')
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.
    """
    form_fields = form.Fields(ICallToActionPortlet)
    form_fields['image_ref'].custom_widget = UberSelectionWidget
    form_fields['form_ref'].custom_widget = UberSelectionWidget
    if WYSIWYGWidget is not None:
        form_fields['text'].custom_widget = WYSIWYGWidget
    label = _(
        u'title_edit_calltoaction_portlet',
        default=u'Edit call to action portlet')
    description = _(
        u'description_calltoaction_portlet',
        default=u'A portlet which displays a call to action overlay '
        'after waiting for some seconds.')

    def __call__(self):
        result = super(EditForm, self).__call__()
        assignment = self.context
        if assignment.new_version:
            assignment.new_version = False
            assignment.version = random_version()
        return result
