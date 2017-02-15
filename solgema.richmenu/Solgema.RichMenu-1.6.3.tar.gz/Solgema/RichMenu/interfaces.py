from zope.interface import Interface, Attribute
from plone.theme.interfaces import IDefaultPloneLayer
from Products.CMFPlone.utils import getFSVersionTuple
from zope import schema
try:
    from plone.supermodel import model
    has_p5 = getFSVersionTuple()[0] == 5
except:
    has_p5 = False

try:
    from z3c.relationfield.schema import RelationChoice, RelationList
    from plone.app.vocabularies.catalog import CatalogSource
    from plone.app.z3cform.widget import RelatedItemsFieldWidget
    has_rel = True
except:
    has_rel = False

try:
    from plone.formwidget.contenttree import ContentTreeFieldWidget, PathSourceBinder, UUIDSourceBinder
    has_ctree = True
except:
    has_ctree = False
    
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.i18nmessageid import MessageFactory
from plone.portlets.interfaces import IPortletAssignment
from config import _
from zope.i18nmessageid import MessageFactory as ZMessageFactory
_p = ZMessageFactory('plone')

class ISolgemaRichMenuLayer(IDefaultPloneLayer):
    """Solgema RichMenu layer"""

class ISolgemaRichMenuMarker(Interface):
    """Marker for RichMenu"""


if has_p5:
    if has_rel:
        class ISolgemaRichMenuAttributes(model.Schema):
            """GlobalSection attributes for item"""
            
            menu_width = schema.TextLine(
                title=_(u"label_menu_width", default=u"Submenu width"),
                description=_(u"help_menu_width", default=u"Set the width of the submenu (in 'px' or '%'). Leave blank for default setting."),
                required = False
                )
            
            menu_position = schema.Choice(
                title=_(u"label_menu_position", default=u"Menu position"),
                description=_(u"help_menu_position", default=u"Set the horizontal position of the menu."),
                required = True,
                vocabulary=SimpleVocabulary([
                    SimpleTerm('left', 'left', _(u"label_left", default=u"left")),
                    SimpleTerm('right', 'right', _(u"label_right", default=u"right")),
                    SimpleTerm('center', 'center', _(u"label_center", default=u"center (submenu width only in px)")),
                    SimpleTerm('left_site', 'left_site', _(u"label_left_site", default=u"site left (submenu width 100%)")),
                    SimpleTerm('right_site', 'right_site', _(u"label_right_site", default=u"site right (submenu width 100%)")),
                ]),
                default="left"
                )
            
            menu_content = schema.List(
                title=_(u"label_menu_content", default=u"Wich content must be displayed in the menu?"),
                value_type = schema.Choice(vocabulary=SimpleVocabulary([
                    SimpleTerm('title', 'title', _(u"label_title", default=u"Title")),
                    SimpleTerm('description', 'description', _(u"label_description", default=u"Description")),
                    SimpleTerm('image', 'image', _(u"label_image", default=u"Image")),
                ])),
                default=['title',]
                )
            
            menu_image_size = schema.Choice(
                title=_(u"label_menu_image_size", default=u"Wich size you want to use for the image in the menu?"),
                vocabulary = SimpleVocabulary([
                      SimpleTerm('icon','icon','Icon (32px*32px)'),
			          SimpleTerm('tile','tile','Small (64px*64px)'),
			          SimpleTerm('thumb','thumb','Middle (128px*128px)'),
			          SimpleTerm('mini','mini','Large (200px*200px)'),
			          SimpleTerm('preview','preview','Preview (400px*400px)'),
	            ]),
                default='tile'
                )
          
            menu_columns = schema.Choice(
                title=_(u"label_menu_columns", default=u"Menu columns"),
                description=_(u"help_menu_columns", default=u"Set the number of columns in the menu."),
                required = True,
                vocabulary=SimpleVocabulary([
                    SimpleTerm('1', '1', '1'),
                    SimpleTerm('2', '2', '2'),
                    SimpleTerm('3', '3', '3'),
                    SimpleTerm('4', '4', '4'),
                ]),
                default="1"
                )
            
            menu_sections_depth = schema.Int(
                title=_(u"label_menu_sections_depth", default=u"Menu Sections depth"),
                description=_(u"help_menu_sections_depth", default=u"Set the depth of submenu to be displayed. Leave empty for default."),
                required = False,
                default=1
            )
            
            menu_direction = schema.Choice(
                title=_(u"label_menu_direction", default=u"Submenu items direction"),
                description=_(u"help_menu_direction", default=u"Choose wether to display items by row or by column."),
                required = True,
                vocabulary=SimpleVocabulary([
                    SimpleTerm('row', 'row', _(u'Row')),
                    SimpleTerm('column', 'column', _('Column')),
                ]),
                default='row'
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

            menu_item_content = schema.List(
                title=_(u"label_menu_item_content", default=u"Wich content must be displayed in the sub-menu?"),
                value_type = schema.Choice(vocabulary=SimpleVocabulary([
                    SimpleTerm('title', 'title', _(u"label_title", default=u"Title")),
                    SimpleTerm('description', 'description', _(u"label_description", default=u"Description")),
                    SimpleTerm('content', 'content', _(u"label_content", default=u"Content")),
                ])),
                default=['title','description','content']
                )
           
            show_menu = schema.Choice(
                title=_(u"label_show_menu", default=u"Show the submenu next to the page?"),
                required = True,
                vocabulary=SimpleVocabulary([
                    SimpleTerm('no', 'no', _p(u"No", default=u"No")),
                    SimpleTerm('left', 'left', _(u"label_left", default=u"left")),
                    SimpleTerm('right', 'right', _(u"label_right", default=u"right")),
                ]),
                default=u'right'
                )
            
            submenu_width = schema.TextLine(
                title=_(u"label_submenu_width", default=u"Sub-menu width"),
                description=_(u"help_submenu_width", default=u"Set the width of the submenu when displayed in a  (in 'px' or '%'). Leave blank for default setting."),
                required = False,
                default = u'50%'
                )
    
            section_menu_item = RelationChoice(
                title=_(u'label_section_menu_item', default=u'Item displayed in menu'),
                description=_(u"help_section_menu_item", default=u"Choose an item that will be displayed in the drop down menu of this section."),
                required=False,
                source=CatalogSource(portal_type=['Document', 'Folder', 'Collage', 'Topic', 'Collection', 'Image'])
                )

            model.fieldset(
                'content_item',
                label=_(u"Content item"),
                fields=['section_menu_item', 'show_menu', 'submenu_width', 'menu_item_content']
                )
    else:
        class ISolgemaRichMenuAttributes(model.Schema):
            """GlobalSection attributes for item"""
            
            menu_width = schema.TextLine(
                title=_(u"label_menu_width", default=u"Submenu width"),
                description=_(u"help_menu_width", default=u"Set the width of the submenu (in 'px' or '%'). Leave blank for default setting."),
                required = False
                )
            
            menu_position = schema.Choice(
                title=_(u"label_menu_position", default=u"Menu position"),
                description=_(u"help_menu_position", default=u"Set the horizontal position of the menu."),
                required = True,
                vocabulary=SimpleVocabulary([
                    SimpleTerm('left', 'left', _(u"label_left", default=u"left")),
                    SimpleTerm('right', 'right', _(u"label_right", default=u"right")),
                    SimpleTerm('center', 'center', _(u"label_center", default=u"center (submenu width only in px)")),
                    SimpleTerm('left_site', 'left_site', _(u"label_left_site", default=u"site left (submenu width 100%)")),
                    SimpleTerm('right_site', 'right_site', _(u"label_right_site", default=u"site right (submenu width 100%)")),
                ]),
                default="left"
                )
            
            menu_content = schema.List(
                title=_(u"label_menu_content", default=u"Wich content must be displayed in the menu?"),
                value_type = schema.Choice(vocabulary=SimpleVocabulary([
                    SimpleTerm('title', 'title', _(u"label_title", default=u"Title")),
                    SimpleTerm('description', 'description', _(u"label_description", default=u"Description")),
                    SimpleTerm('image', 'image', _(u"label_image", default=u"Image")),
                ])),
                default=['title',]
                )
            
            menu_image_size = schema.Choice(
                title=_(u"label_menu_image_size", default=u"Wich size you want to use for the image in the menu?"),
                vocabulary = SimpleVocabulary([
                      SimpleTerm('icon','icon','Icon (32px*32px)'),
			          SimpleTerm('tile','tile','Small (64px*64px)'),
			          SimpleTerm('thumb','thumb','Middle (128px*128px)'),
			          SimpleTerm('mini','mini','Large (200px*200px)'),
			          SimpleTerm('preview','preview','Preview (400px*400px)'),
	            ]),
                default='tile'
                )
          
            menu_columns = schema.Choice(
                title=_(u"label_menu_columns", default=u"Menu columns"),
                description=_(u"help_menu_columns", default=u"Set the number of columns in the menu."),
                required = True,
                vocabulary=SimpleVocabulary([
                    SimpleTerm('1', '1', '1'),
                    SimpleTerm('2', '2', '2'),
                    SimpleTerm('3', '3', '3'),
                    SimpleTerm('4', '4', '4'),
                ]),
                default="1"
                )
            
            menu_sections_depth = schema.Int(
                title=_(u"label_menu_sections_depth", default=u"Menu Sections depth"),
                description=_(u"help_menu_sections_depth", default=u"Set the depth of submenu to be displayed. Leave empty for default."),
                required = False,
                default=1
            )
            
            menu_direction = schema.Choice(
                title=_(u"label_menu_direction", default=u"Submenu items direction"),
                description=_(u"help_menu_direction", default=u"Choose wether to display items by row or by column."),
                required = True,
                vocabulary=SimpleVocabulary([
                    SimpleTerm('row', 'row', _(u'Row')),
                    SimpleTerm('column', 'column', _('Column')),
                ]),
                default='row'
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

            menu_item_content = schema.List(
                title=_(u"label_menu_item_content", default=u"Wich content must be displayed in the sub-menu?"),
                value_type = schema.Choice(vocabulary=SimpleVocabulary([
                    SimpleTerm('title', 'title', _(u"label_title", default=u"Title")),
                    SimpleTerm('description', 'description', _(u"label_description", default=u"Description")),
                    SimpleTerm('content', 'content', _(u"label_content", default=u"Content")),
                ])),
                default=['title','description','content']
                )
           
            show_menu = schema.Choice(
                title=_(u"label_show_menu", default=u"Show the submenu next to the page?"),
                required = True,
                vocabulary=SimpleVocabulary([
                    SimpleTerm('no', 'no', _p(u"No", default=u"No")),
                    SimpleTerm('left', 'left', _(u"label_left", default=u"left")),
                    SimpleTerm('right', 'right', _(u"label_right", default=u"right")),
                ]),
                default=u'right'
                )
            
            submenu_width = schema.TextLine(
                title=_(u"label_submenu_width", default=u"Sub-menu width"),
                description=_(u"help_submenu_width", default=u"Set the width of the submenu when displayed in a  (in 'px' or '%'). Leave blank for default setting."),
                required = False,
                default = u'50%'
                )
    
            section_menu_item = schema.Choice(
                title=_(u'label_section_menu_item', default=u'Item displayed in menu'),
                description=_(u"help_section_menu_item", default=u"Choose an item that will be displayed in the drop down menu of this section."),
                required=False,
                source=UUIDSourceBinder(navigation_tree_query=None, portal_type=['Document', 'Folder', 'Collage', 'Topic', 'Collection', 'Image'])
                )

            model.fieldset(
                'content_item',
                label=_(u"Content item"),
                fields=['section_menu_item', 'show_menu', 'submenu_width', 'menu_item_content']
                )
else:
    if has_rel:
        class ISolgemaRichMenuAttributes(Interface):
            """GlobalSection attributes for item"""
            
            menu_width = schema.TextLine(
                title=_(u"label_menu_width", default=u"Submenu width"),
                description=_(u"help_menu_width", default=u"Set the width of the submenu (in 'px' or '%'). Leave blank for default setting."),
                required = False
                )
            
            menu_position = schema.Choice(
                title=_(u"label_menu_position", default=u"Menu position"),
                description=_(u"help_menu_position", default=u"Set the horizontal position of the menu."),
                required = True,
                vocabulary=SimpleVocabulary([
                    SimpleTerm('left', 'left', _(u"label_left", default=u"left")),
                    SimpleTerm('right', 'right', _(u"label_right", default=u"right")),
                    SimpleTerm('center', 'center', _(u"label_center", default=u"center (submenu width only in px)")),
                    SimpleTerm('left_site', 'left_site', _(u"label_left_site", default=u"site left (submenu width 100%)")),
                    SimpleTerm('right_site', 'right_site', _(u"label_right_site", default=u"site right (submenu width 100%)")),
                ]),
                default="left"
                )
            
            menu_content = schema.List(
                title=_(u"label_menu_content", default=u"Wich content must be displayed in the menu?"),
                value_type = schema.Choice(vocabulary=SimpleVocabulary([
                    SimpleTerm('title', 'title', _(u"label_title", default=u"Title")),
                    SimpleTerm('description', 'description', _(u"label_description", default=u"Description")),
                    SimpleTerm('image', 'image', _(u"label_image", default=u"Image")),
                ])),
                default=['title',]
                )
            
            menu_image_size = schema.Choice(
                title=_(u"label_menu_image_size", default=u"Wich size you want to use for the image in the menu?"),
                vocabulary = SimpleVocabulary([
                      SimpleTerm('icon','icon','Icon (32px*32px)'),
			          SimpleTerm('tile','tile','Small (64px*64px)'),
			          SimpleTerm('thumb','thumb','Middle (128px*128px)'),
			          SimpleTerm('mini','mini','Large (200px*200px)'),
			          SimpleTerm('preview','preview','Preview (400px*400px)'),
	            ]),
                default='tile'
                )
          
            menu_columns = schema.Choice(
                title=_(u"label_menu_columns", default=u"Menu columns"),
                description=_(u"help_menu_columns", default=u"Set the number of columns in the menu."),
                required = True,
                vocabulary=SimpleVocabulary([
                    SimpleTerm('1', '1', '1'),
                    SimpleTerm('2', '2', '2'),
                    SimpleTerm('3', '3', '3'),
                    SimpleTerm('4', '4', '4'),
                ]),
                default="1"
                )
            
            menu_sections_depth = schema.Int(
                title=_(u"label_menu_sections_depth", default=u"Menu Sections depth"),
                description=_(u"help_menu_sections_depth", default=u"Set the depth of submenu to be displayed. Leave empty for default."),
                required = False,
                default=1
            )
            
            menu_direction = schema.Choice(
                title=_(u"label_menu_direction", default=u"Submenu items direction"),
                description=_(u"help_menu_direction", default=u"Choose wether to display items by row or by column."),
                required = True,
                vocabulary=SimpleVocabulary([
                    SimpleTerm('row', 'row', _(u'Row')),
                    SimpleTerm('column', 'column', _('Column')),
                ]),
                default='row'
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

            menu_item_content = schema.List(
                title=_(u"label_menu_item_content", default=u"Wich content must be displayed in the sub-menu?"),
                value_type = schema.Choice(vocabulary=SimpleVocabulary([
                    SimpleTerm('title', 'title', _(u"label_title", default=u"Title")),
                    SimpleTerm('description', 'description', _(u"label_description", default=u"Description")),
                    SimpleTerm('content', 'content', _(u"label_content", default=u"Content")),
                ])),
                default=['title','description','content']
                )
           
            show_menu = schema.Choice(
                title=_(u"label_show_menu", default=u"Show the submenu next to the page?"),
                required = True,
                vocabulary=SimpleVocabulary([
                    SimpleTerm('no', 'no', _p(u"No", default=u"No")),
                    SimpleTerm('left', 'left', _(u"label_left", default=u"left")),
                    SimpleTerm('right', 'right', _(u"label_right", default=u"right")),
                ]),
                default=u'right'
                )
            
            submenu_width = schema.TextLine(
                title=_(u"label_submenu_width", default=u"Sub-menu width"),
                description=_(u"help_submenu_width", default=u"Set the width of the submenu when displayed in a  (in 'px' or '%'). Leave blank for default setting."),
                required = False,
                default = u'50%'
                )
    
            section_menu_item = RelationChoice(
                title=_(u'label_section_menu_item', default=u'Item displayed in menu'),
                description=_(u"help_section_menu_item", default=u"Choose an item that will be displayed in the drop down menu of this section."),
                required=False,
                source=CatalogSource(portal_type=['Document', 'Folder', 'Collage', 'Topic', 'Collection', 'Image'])
                )
    elif has_ctree:
        class ISolgemaRichMenuAttributes(Interface):
            """GlobalSection attributes for item"""
            
            menu_width = schema.TextLine(
                title=_(u"label_menu_width", default=u"Submenu width"),
                description=_(u"help_menu_width", default=u"Set the width of the submenu (in 'px' or '%'). Leave blank for default setting."),
                required = False
                )
            
            menu_position = schema.Choice(
                title=_(u"label_menu_position", default=u"Menu position"),
                description=_(u"help_menu_position", default=u"Set the horizontal position of the menu."),
                required = True,
                vocabulary=SimpleVocabulary([
                    SimpleTerm('left', 'left', _(u"label_left", default=u"left")),
                    SimpleTerm('right', 'right', _(u"label_right", default=u"right")),
                    SimpleTerm('center', 'center', _(u"label_center", default=u"center (submenu width only in px)")),
                    SimpleTerm('left_site', 'left_site', _(u"label_left_site", default=u"site left (submenu width 100%)")),
                    SimpleTerm('right_site', 'right_site', _(u"label_right_site", default=u"site right (submenu width 100%)")),
                ]),
                default="left"
                )
            
            menu_content = schema.List(
                title=_(u"label_menu_content", default=u"Wich content must be displayed in the menu?"),
                value_type = schema.Choice(vocabulary=SimpleVocabulary([
                    SimpleTerm('title', 'title', _(u"label_title", default=u"Title")),
                    SimpleTerm('description', 'description', _(u"label_description", default=u"Description")),
                    SimpleTerm('image', 'image', _(u"label_image", default=u"Image")),
                ])),
                default=['title',]
                )
            
            menu_image_size = schema.Choice(
                title=_(u"label_menu_image_size", default=u"Wich size you want to use for the image in the menu?"),
                vocabulary = SimpleVocabulary([
                      SimpleTerm('icon','icon','Icon (32px*32px)'),
			          SimpleTerm('tile','tile','Small (64px*64px)'),
			          SimpleTerm('thumb','thumb','Middle (128px*128px)'),
			          SimpleTerm('mini','mini','Large (200px*200px)'),
			          SimpleTerm('preview','preview','Preview (400px*400px)'),
	            ]),
                default='tile'
                )
          
            menu_columns = schema.Choice(
                title=_(u"label_menu_columns", default=u"Menu columns"),
                description=_(u"help_menu_columns", default=u"Set the number of columns in the menu."),
                required = True,
                vocabulary=SimpleVocabulary([
                    SimpleTerm('1', '1', '1'),
                    SimpleTerm('2', '2', '2'),
                    SimpleTerm('3', '3', '3'),
                    SimpleTerm('4', '4', '4'),
                ]),
                default="1"
                )
            
            menu_sections_depth = schema.Int(
                title=_(u"label_menu_sections_depth", default=u"Menu Sections depth"),
                description=_(u"help_menu_sections_depth", default=u"Set the depth of submenu to be displayed. Leave empty for default."),
                required = False,
                default=1
            )
            
            menu_direction = schema.Choice(
                title=_(u"label_menu_direction", default=u"Submenu items direction"),
                description=_(u"help_menu_direction", default=u"Choose wether to display items by row or by column."),
                required = True,
                vocabulary=SimpleVocabulary([
                    SimpleTerm('row', 'row', _(u'Row')),
                    SimpleTerm('column', 'column', _('Column')),
                ]),
                default='row'
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

            menu_item_content = schema.List(
                title=_(u"label_menu_item_content", default=u"Wich content must be displayed in the sub-menu?"),
                value_type = schema.Choice(vocabulary=SimpleVocabulary([
                    SimpleTerm('title', 'title', _(u"label_title", default=u"Title")),
                    SimpleTerm('description', 'description', _(u"label_description", default=u"Description")),
                    SimpleTerm('content', 'content', _(u"label_content", default=u"Content")),
                ])),
                default=['title','description','content']
                )
           
            show_menu = schema.Choice(
                title=_(u"label_show_menu", default=u"Show the submenu next to the page?"),
                required = True,
                vocabulary=SimpleVocabulary([
                    SimpleTerm('no', 'no', _p(u"No", default=u"No")),
                    SimpleTerm('left', 'left', _(u"label_left", default=u"left")),
                    SimpleTerm('right', 'right', _(u"label_right", default=u"right")),
                ]),
                default=u'right'
                )
            
            submenu_width = schema.TextLine(
                title=_(u"label_submenu_width", default=u"Sub-menu width"),
                description=_(u"help_submenu_width", default=u"Set the width of the submenu when displayed in a  (in 'px' or '%'). Leave blank for default setting."),
                required = False,
                default = u'50%'
                )

            section_menu_item = schema.Choice(
                title=_(u'label_section_menu_item', default=u'Item displayed in menu'),
                description=_(u"help_section_menu_item", default=u"Choose an item that will be displayed in the drop down menu of this section."),
                required=False,
                source=UUIDSourceBinder(navigation_tree_query=None, portal_type=['Document', 'Folder', 'Collage', 'Topic', 'Collection', 'Image'])
                )


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

