from zope import schema
from zope.interface import Interface
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from Solgema.RichMenu.config import _

class IRichMenuSchema(Interface):

    sections_enable_submenues = schema.Bool(
        title=_(u"Enable Submenues"),
        description=_(
            u"Show submenues in tabs."),
        default=True,
        required=False)

    sections_displayed_types = schema.Tuple(
        title=_(u"Sections displayed content types"),
        description=_(
            u"The content types that should be shown in the main navigation menu."),
        required=False,
        default=(
            'Image',
            'File',
            'Link',
            'News Item',
            'Folder',
            'Document',
            'Event'
        ),
        value_type=schema.Choice(
            source="plone.app.vocabularies.ReallyUserFriendlyTypes"
        ))

    enable_wf_state_filtering = schema.Bool(
        title=_(u"Filter sections on workflow state"),
        description=_(
            u"The workflow states that should be shown in the main navigation menu."),
        default=False,
        required=False)

    sections_wf_states_to_show = schema.Tuple(
        required=False,
        default=(),
        value_type=schema.Choice(
            source="plone.app.vocabularies.WorkflowStates"))

    sections_depth = schema.Int(
        title=_(u"Submenues depth"),
        description=_(u"Number of folder levels to show in the submenues."),
        default=1,
        required=True
    )

    submenu_display = schema.Choice(
        title=_(u"label_submenu_display", default=u"Sub-menu display"),
        description=_(u"help_submenu_display", default=u"Choose when to display the submenu."),
        required = True,
        vocabulary=SimpleVocabulary([
            SimpleTerm('hover', 'hover', _(u"label_hover", default=u"Mouse hover")),
            SimpleTerm('click', 'click', _(u"label_click", default=u"Mouse click")),
            SimpleTerm('always', 'always', _(u"label_always", default=u"Always")),
        ]),
        default="hover"
        )

