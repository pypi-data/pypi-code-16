import logging
import sys, traceback
from Acquisition import aq_inner, aq_parent, aq_base
from zope.interface import implements, alsoProvides
from zope.component import getMultiAdapter, queryMultiAdapter, getUtility, adapts
from zope.viewlet.interfaces import IViewlet
from zope.deprecation.deprecation import deprecate
from Products.CMFPlone import utils
from Products.CMFPlone.browser.navigation import get_view_url, get_id
from Products.CMFCore.utils import getToolByName
from zope.interface import implements, Interface
from Products.CMFCore.interfaces._content import IDublinCore
from Products.CMFPlone.utils import getFSVersionTuple
from zope.browsermenu.interfaces import IBrowserMenu
from plone.registry.interfaces import IRegistry

from Products.Five.browser import BrowserView
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.viewlets.common import GlobalSectionsViewlet as baseGlobalSectionsViewlet
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFPlone.interfaces import IPloneSiteRoot

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from plone.memoize import instance, view, ram, forever
from time import time
try:
    from plone.dexterity.interfaces import IDexterityContent
    from plone.namedfile.scaling import ImageScaling
    from plone.app.contenttypes.interfaces import IImage
    has_dx = True
except:
    has_dx = False
try:
    from Martronic.ContentImageExtend.interfaces import IContentImageExtend
    has_cie = True
except:
    has_cie = False
try:
    from plone.app.contenttypes.behaviors.leadimage import ILeadImage
    has_leadimage = True
except:
    has_leadimage = False

LOG = logging.getLogger(__name__)

def _secondLevelTabs_cachekey(fun, self, query):
    return query.items()

class GlobalSectionsViewlet(ViewletBase):

    def index(self):
        if getFSVersionTuple()[0] <= 4:
            return ViewPageTemplateFile('sections-p4.pt')(self)
        else:
            return ViewPageTemplateFile('sections.pt')(self)
        
    def rootsUrls(self):
        catalog = getToolByName(self.context, "portal_catalog")
        roots = catalog.searchResults({'object_provides' : INavigationRoot.__identifier__})
        urls = [a.getURL() for a in roots]
        urls.sort(lambda x, y : cmp (len(x.split('/')),len(y.split('/'))))
        urls.reverse()
        return urls

    @property
    def context_url(self):
        context = aq_inner(self.context)
        while not IDublinCore.providedBy(context):
            context = aq_parent(context)
        url = context.absolute_url()
        rootsUrls = self.rootsUrls()
        portal_state = getMultiAdapter((context, self.request),
                                            name=u'plone_portal_state')
        plone_url = portal_state.portal_url()
        rootsUrls.append(plone_url)
        rootURL = plone_url
        for rurl in rootsUrls:
            if rurl in url or rurl == url:
                rootURL = rurl
                break
        if len(url.split('/'))>len(rootURL.split('/'))+1:
            url = '/'.join(url.split('/')[0:len(rootURL.split('/'))+1])
#        traceback.print_stack()
        return url

    @property
    def anonymous(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        return self.portal_state.anonymous()

    def content(self):
        content = GlobalSectionsContentPage(self.context, self.request)
        return content()

def _firstLevelTabs_cachekey(method, self, rootPath=None, sublevels=None, category='portal_tabs'):
    if rootPath == None:
        rootPath = getMultiAdapter((self.context, self.request), name="plone_portal_state").navigation_root_path()
    return (str(rootPath),)

class GlobalSectionsContentPage(BrowserView):

    index = ViewPageTemplateFile('sections_content.pt')
    recurse = ViewPageTemplateFile('sections_recurse.pt')
        
    def update(self):
        context = aq_inner(self.context)
        self.portal_properties = getToolByName(context, 'portal_properties')
        self.portal_catalog = getToolByName(context, 'portal_catalog')
        self.site_properties = getattr(self.portal_properties, 'site_properties')
        self.has_p4 = getFSVersionTuple()[0] <= 4
        if getFSVersionTuple()[0] <= 4:
            self.navtree_properties = getattr(self.portal_properties, 'navtree_properties')
            self.view_action_types = self.portal_properties.getProperty('typesUseViewActionInListings', ())
            self.sortAttribute = self.navtree_properties.getProperty('sortAttribute', None)
            self.sortOrder = self.navtree_properties.getProperty('sortOrder', None)
            self.sections_displayed_types = self.navtree_properties.getProperty('sections_displayed_types', False)
            self.enable_wf_state_filtering = self.navtree_properties.getProperty('enable_wf_state_filtering', True)
            self.wf_states_to_show = self.navtree_properties.getProperty('wf_states_to_show', ())
            self.sections_wf_states_to_show = self.navtree_properties.getProperty('sections_wf_states_to_show', self.wf_states_to_show)
            self.disable_nonfolderish_sections = self.site_properties.getProperty('disable_nonfolderish_sections', False)
            self.sections_depth = self.navtree_properties.getProperty('sections_depth', 1)
            self.submenu_display = self.navtree_properties.getProperty('submenu_display', 'hover')
        else:
            from Solgema.RichMenu.dx.interfaces import IRichMenuSchema
            from Products.CMFPlone.interfaces import INavigationSchema
            registry = getUtility(IRegistry)
            self.richmenu_properties = registry.forInterface(
                IRichMenuSchema,
                prefix="plone",
                check=False
            )
            self.navtree_properties = registry.forInterface(INavigationSchema,
                                                    prefix="plone")
            self.view_action_types = registry.get('plone.types_use_view_action_in_listings', [])
            self.sortAttribute = self.navtree_properties.sort_tabs_on
            self.sortOrder = self.navtree_properties.sort_tabs_reversed and 'reverse' or 'ascending'
            self.sections_displayed_types = self.richmenu_properties.sections_displayed_types
            self.enable_wf_state_filtering = self.richmenu_properties.enable_wf_state_filtering
            self.workflow_states_to_show = self.navtree_properties.workflow_states_to_show
            self.sections_wf_states_to_show = self.richmenu_properties.sections_wf_states_to_show\
                and self.richmenu_properties.sections_wf_states_to_show or self.workflow_states_to_show
            self.disable_nonfolderish_sections = not self.navtree_properties.nonfolderish_tabs
            self.sections_depth = self.richmenu_properties.sections_depth
            self.submenu_display = self.richmenu_properties.submenu_display
        self.portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.anonymous = self.portal_state.anonymous()
        self.navigation_root_url = self.portal_state.navigation_root_url()
        root = self.portal_state.navigation_root()
        portal = self.portal_state.portal()
        self.canManageNavTree = not self.anonymous and portal.portal_membership.checkPermission('Add portal content', root) or False
        self.proxy = self.request.getHeader('proxy') == 'Varnish'
        self.portal_tabs = self.firstLevelTabs()
    
    @property
    def selected_portal_tab(self):
        selected_tabs = self.selectedTabs(portal_tabs=self.portal_tabs)
        return selected_tabs['portal']

    def createSections(self):
        return self.recurse(children=self.portal_tabs, level=1)

#    @view.memoize_contextless
    def _getNavQuery(self, rootPath=None):

        customQuery = getattr(self.context, 'getCustomNavQuery', False)
        if customQuery is not None and utils.safe_callable(customQuery):
            query = customQuery()
        else:
            query = {}
        if rootPath == None:
            rootPath = getMultiAdapter((self.context, self.request), name="plone_portal_state").navigation_root_path()
        query['path'] = {'query' : rootPath, 'depth' : 1}

        if self.sections_displayed_types:
            query['portal_type'] = self.sections_displayed_types
        else:
            query['portal_type'] = ['Folder', 'Collection', 'Topic', 'Collage', 'FormFolder']

        if self.sortAttribute is not None:
            query['sort_on'] = self.sortAttribute
            if self.sortOrder is not None:
                query['sort_order'] = self.sortOrder

        rootItem = self.context.restrictedTraverse(rootPath)

        if self.enable_wf_state_filtering and rootItem.portal_type not in ['MemberFolder']:
            query['review_state'] = self.sections_wf_states_to_show

        query['is_default_page'] = False
        
        if self.disable_nonfolderish_sections:
            query['is_folderish'] = True
        return query
        
#    @view.memoize
#    @ram.cache(_firstLevelTabs_cachekey)
    def firstLevelTabs(self, rootPath=None, sublevels=None, category='portal_tabs'):
        context = aq_inner(self.context)
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        try:
            actions = context_state.actions()
        except:
            actions = None

        if sublevels == None:
            sublevels = self.sections_depth
                
        # Build result dict
        result = []
        # first the actions
        
        if actions is not None:
            if isinstance(actions, list):
                for actionInfo in [a for a in actions if a.get('category') == category]:
                    data = actionInfo.copy()
                    data['name'] = data['title']
                    result.append(data)
            else:
                for actionInfo in actions.get(category, []):
                    data = actionInfo.copy()
                    data['name'] = data['title']
                    result.append(data)
        # check whether we only want actions
        if self.disable_nonfolderish_sections:
            return result

        query = self._getNavQuery(rootPath)
        rawresult = self.portal_catalog.searchResults(**query)

        def _get_url(item):
            member = self.portal_state.member()
            if item.getRemoteUrl and not member == item.Creator:
                return (get_id(item), item.getRemoteUrl)
            return get_view_url(item)
            
        # now add the content to results
        for item in rawresult:
            if not getattr(item, 'exclude_from_nav', False) and not getattr(item, 'exclude_from_globalnav', False):
                if isinstance(getattr(item, 'menu_sections_depth', None), int):
                    sublevels = getattr(item, 'menu_sections_depth', 1)

                cid, item_url = _get_url(item)


                children = []

                menu_columns = getattr(item, 'menu_columns', None)
                if not menu_columns:
                    menu_columns = '1'
                
                if sublevels > 0 and getattr(item, 'show_menu', 'right') != u'no':
                    itempath = item.getPath()
                    query['path'] = {'query' : itempath.replace('/','',1), 'depth' : 1}
                    group = getattr(item, 'menu_direction', 'row') == 'column' and int(menu_columns) or 1
                    children = self.secondLevelTabs(query, 1, item, sublevels, group=group)

                data = {'name'              : utils.pretty_title_or_id(context, item),
                        'id'                : item.getId,
                        'url'               : item_url,
                        'description'       : item.Description,
                        'review_state'      :'state-'+item.review_state,
                        'children'          : children,
                        'is_default_page'   : getattr(item, 'is_default_page', False),
                        'sectionmenuitem'   : None,
                        'menustyle'         : None,
                        'menumarginleft'    : None,
                        'showmenu'          : None
                        }
                if getattr(item, 'section_menu_item', None):
                    res = self.portal_catalog.searchResults(UID=item.section_menu_item)
                    if res:
                        res = res[0].getObject()
                        showmenu = getattr(item, 'show_menu', 'right')
                        if showmenu:
                            data['showmenu'] = showmenu
                        else:
                            data['showmenu'] = 'right'
                        if has_dx and IDexterityContent.providedBy(res):
                            page = queryMultiAdapter((res, self.request), name='richmenu_view_item')
                            if page:
                                menu_item_content = {'display_title':True,
                                                     'display_description':True,
                                                     'display_content':True}
                                if getattr(item, 'menu_item_content', None):
                                    mic = item.menu_item_content
                                    if 'title' not in mic:
                                        menu_item_content['display_title'] = False
                                    if 'description' not in mic:
                                        menu_item_content['display_description'] = False
                                    if 'content' not in mic:
                                        menu_item_content['display_content'] = False
                                data['sectionmenuitem'] = page(**menu_item_content)
                        else:
                            data['sectionmenuitem'] = res.restrictedTraverse('folder_full_view_item')()

                data['menucolumns'] = menu_columns
                data['menuwidth'] = getattr(item, 'menu_width', None)
                data['submenuwidth'] = getattr(item, 'submenu_width', None)
                menu_position = getattr(item, 'menu_position', None)
                if not menu_position:
                    menu_position = 'left'
                data['menuposition'] = menu_position
                if data['menuposition'] == 'center':
                    if not data['menuwidth'] or '%' in data['menuwidth']:
                        if menu_columns == '1':
                            data['menuwidth'] = '200px'
                            data['menumarginleft'] = '-100px'
                        if menu_columns == '2':
                            data['menuwidth'] = '250px'
                            data['menumarginleft'] = '-125px'
                        if menu_columns == '3':
                            data['menuwidth'] = '300px'
                            data['menumarginleft'] = '-150px'
                        if menu_columns == '4':
                            data['menuwidth'] = '400px'
                            data['menumarginleft'] = '-200px'
                    else:
                        marginleft = None
                        try:
                            marginleft = int(data['menuwidth'])
                            data['menumarginleft'] = '-'+str(marginleft/2)
                        except:
                            try:
                                marginleft = int(data['menuwidth'][0:-2])
                                data['menumarginleft'] = '-'+str(marginleft/2)+data['menuwidth'][-2:]
                            except:
                                data['menumarginleft'] = None
                if data['menuwidth']:
                    data['menustyle'] = 'width:'+data['menuwidth']+';'
                    if data['menumarginleft']:
                        data['menustyle'] += 'margin-left:'+data['menumarginleft']+';'
                if data['showmenu'] == u'right' and len(children)>0:
                    if data['submenuwidth']:
                        data['contentstyle'] = 'margin-right:'+data['submenuwidth']+';'
                    elif menu_columns == '1':
                        data['contentstyle'] = 'margin-right:200px;'
                    elif menu_columns == '2':
                        data['contentstyle'] = 'margin-right:250px;'
                    elif menu_columns == '3':
                        data['contentstyle'] = 'margin-right:300px;'
                    elif menu_columns == '4':
                        data['contentstyle'] = 'margin-right:400px;'
                        
                result.append(data)
        final_results = []
        for res in result:
            res['number'] = result.index(res)
            if not res.get('is_default_page', False):
                final_results.append(res)
        return final_results

#    @ram.cache(_secondLevelTabs_cachekey)
    def secondLevelTabs(self, query, currentlevel, currentitem, sublevels=None, group=1):
        context = aq_inner(self.context)

        result = []

        if currentitem.portal_type in ['Topic', 'Collection'] and getattr(currentitem, 'show_results_in_globalnav', False):
            topic = currentitem.getObject()
            rawresult = topic.queryCatalog(review_state=query['review_state'], portal_type=query['portal_type'])
        else:
            rawresult = self.portal_catalog.searchResults(**query)
        if group > 1:
            grouplist = []
            lgroup = range(group)
            for i in lgroup:
                grouplist.append([])
            for item in rawresult:
                idx = (list(rawresult).index(item)+1)%group
                grouplist[idx-1].append(item)
            rawresult = []
            for g in grouplist:
                rawresult += g
        if sublevels == None:
            sublevels = getattr(self.navtree_properties, 'sections_depth', 1)

        def _get_url(item):
            member = self.portal_state.member()
            if item.getRemoteUrl and not member == item.Creator:
                return (get_id(item), item.getRemoteUrl)
            return get_view_url(item)
            
        # now add the content to results
        for item in rawresult:
            if not getattr(item, 'exclude_from_nav', False) and not getattr(item, 'exclude_from_globalnav', False):

                cid, item_url = _get_url(item)

                children = []
                if sublevels > currentlevel:
                    itempath = item.getPath()
                    query['path'] = {'query' : itempath.replace('/','',1), 'depth' : 1}
                    newlevel = currentlevel + 1
                    children = self.secondLevelTabs(query, newlevel, item, sublevels)

                data = {'name'        : utils.pretty_title_or_id(context, item),
                        'id'          : item.getId,
                        'url'         : item_url,
                        'description' : item.Description,
                        'review_state': 'state-'+item.review_state,
                        'children'    : children,
                        }
                menucontent = getattr(currentitem, 'menu_content', None)
                if not menucontent:
                    menucontent = ['title']
                data['menucontent'] = menucontent
                if menucontent and 'image' in menucontent:
                    data['menuimage'] = None
                    image = None
                    if has_cie:
                        if getattr(item, 'image_assoc', None):
                            results = self.portal_catalog.searchResults({'UID':item.image_assoc[0], 'Language':'all'})
                            if results:
                                image = results[0].getObject()
                    if not image:
                        obj = item.getObject()
                        if (has_dx and IImage.providedBy(obj)) or hasattr(obj, 'tag') or getattr(obj, 'image', None):
                            image = obj
                    if image:
                        size = getattr(currentitem, 'menu_image_size', 'tile')
                        if not size:
                            size = 'tile'
                        data['menuimagesize'] = size
                        if hasattr(image, 'tag'):
                            data['menuimage'] = image.tag(scale=size, css_class='')
                        elif has_dx:
                            if IImage.providedBy(image):
                                data['menuimage'] = ImageScaling(image, self.request).tag(scale=size, css_class='')
                            else:
                                data['menuimage'] = ImageScaling(image, self.request).tag(fieldname='image', scale=size, css_class='')
                                
                submenudisplay = getattr(currentitem, 'submenu_display', None)
                if not submenudisplay:
                    submenudisplay = 'hover'
                data['submenudisplay'] = submenudisplay
                if not getattr(item, 'is_default_page', False):
                    result.append(data)

        return result

    def selectedTabs(self, default_tab='index_html', portal_tabs=()):
        plone_url = self.portal_state.portal_url()
        plone_url_len = len(plone_url)
        request = self.request
        valid_actions = []

        url = request['URL']
        path = url[plone_url_len:]

        for action in portal_tabs:
            if not action['url'].startswith(plone_url):
                # In this case the action url is an external link. Then, we
                # avoid issues (bad portal_tab selection) continuing with next
                # action.
                continue
            action_path = action['url'][plone_url_len:]
            if not action_path.startswith('/'):
                action_path = '/' + action_path
            if path.startswith(action_path + '/'):
                # Make a list of the action ids, along with the path length
                # for choosing the longest (most relevant) path.
                valid_actions.append((len(action_path), action['id']))

        # Sort by path length, the longest matching path wins
        valid_actions.sort()
        if valid_actions:
            return {'portal' : valid_actions[-1][1]}

        return {'portal' : default_tab}

    def __call__(self):
        self.update()
        if self.request.get('esi'):
            self.request.response.setHeader('X-Theme-Disabled', 'True')
        return self.index()

class GlobalSectionsPage(BrowserView):
    
    def viewlet(self):
        viewlet = GlobalSectionsViewlet(self.context, self.request, self)
        viewlet.update()
        return viewlet.render()
