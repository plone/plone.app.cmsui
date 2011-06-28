from zope.publisher.browser import BrowserView
from Acquisition import aq_inner, aq_parent
from Products.CMFPlone.utils import pretty_title_or_id, isExpired
from zope.component import getMultiAdapter, getUtility
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from AccessControl import Unauthorized
from Products.ATContentTypes.interface import IATTopic
from zope.i18n import translate
import urllib
from Products.CMFPlone.utils import safe_unicode
from plone.memoize import instance
from zope.i18nmessageid import MessageFactory
from plone.app.content.batching import Batch
from zope.cachedescriptors.property import Lazy as lazy_property
from plone.registry.interfaces import IRegistry
from plone.folder.interfaces import IOrderableFolder, IExplicitOrdering
from plone.app.cmsui.interfaces import ICMSUISettings
from Products.CMFPlone.utils import base_hasattr

_ = MessageFactory('plone')


class StructureView(BrowserView):
    """Folder contents overlay
    """

    def __call__(self, contentFilter={}):
        # Disable theming
        self.contentFilter = contentFilter
        self.request.response.setHeader('X-Theme-Disabled', 'True')

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICMSUISettings, False)
        
        
        self.pagesize = settings.folderContentsBatchSize
        self.show_all = self.request.get('show_all', '').lower() == 'true'

        selection = self.request.get('select')
        if selection == 'all':
            self.selectall = True
        else:
            self.selectall = False

        self.pagenumber =  int(self.request.get('pagenumber', 1))

        self.context_state = getMultiAdapter((self.context, self.request), name=u'plone_context_state')

        return self.index()

    def title(self):
        """
        """
        return pretty_title_or_id(context=self.context, obj=self.context)

    def icon(self):
        """
        """
        context = aq_inner(self.context)
        plone_layout = getMultiAdapter((context, self.request), name="plone_layout")
        icon = plone_layout.getIcon(context)
        return icon.html_tag()

    def parent_url(self):
        """
        """
        context = aq_inner(self.context)
        portal_membership = getToolByName(context, 'portal_membership')

        obj = context

        checkPermission = portal_membership.checkPermission

        # Abort if we are at the root of the portal
        if IPloneSiteRoot.providedBy(context):
            return None

        # Get the parent. If we can't get it (unauthorized), use the portal
        parent = aq_parent(obj)

        # # We may get an unauthorized exception if we're not allowed to access#
        # the parent. In this case, return None
        try:
            if getattr(parent, 'getId', None) is None or \
                   parent.getId() == 'talkback':
                # Skip any Z3 views that may be in the acq tree;
                # Skip past the talkback container if that's where we are
                parent = aq_parent(parent)

            if not checkPermission('List folder contents', parent):
                return None

            return parent.absolute_url()
        except Unauthorized:
            return None

    def breadcrumbs(self):
        breadcrumbsView = getMultiAdapter((self.context, self.request), name='breadcrumbs_view')
        breadcrumbs = list(breadcrumbsView.breadcrumbs())
        if self.context_state.is_default_page():
            # then we need to mess with the breadcrumbs a bit.
            parent = aq_parent(aq_inner(self.context))
            if breadcrumbs:
                breadcrumbs[-1] = {'absolute_url' : parent.absolute_url(), 'Title': parent.Title()}
            breadcrumbs.append({'absolute_url' : self.context.absolute_url(), 'Title': self.context.Title()})
        return breadcrumbs

    def contentsMethod(self):
        context = aq_inner(self.context)
        if IATTopic.providedBy(context):
            contentsMethod = context.queryCatalog
        else:
            contentsMethod = context.getFolderContents
        return contentsMethod

    @lazy_property
    def folderitems(self):
        """
        """
        context = aq_inner(self.context)
        plone_utils = getToolByName(context, 'plone_utils')
        plone_view = getMultiAdapter((context, self.request), name=u'plone')
        plone_layout = getMultiAdapter((context, self.request), name=u'plone_layout')
        portal_workflow = getToolByName(context, 'portal_workflow')
        portal_types = getToolByName(context, 'portal_types')
        portal_membership = getToolByName(context, 'portal_membership')

        browser_default = plone_utils.browserDefault(context)

        contentsMethod = self.contentsMethod()

        pagenumber = int(self.request.get('pagenumber', 1))
        start = (pagenumber - 1) * self.pagesize
        end = start + self.pagesize

        results = []
        for i, obj in enumerate(contentsMethod(self.contentFilter)):
            path = obj.getPath() or "/".join(obj.getPhysicalPath())

            # avoid creating unnecessary info for items outside the current
            # batch;  only the path is needed for the "select all" case...
            if not self.selectall and not self.show_all and not start <= i < end:
                results.append(dict(path = path))
                continue

            if (i + 1) % 2 == 0:
                table_row_class = "draggable even"
            else:
                table_row_class = "draggable odd"

            url = obj.getURL()
            icon = plone_layout.getIcon(obj)
            type_class = 'contenttype-' + plone_utils.normalizeString(
                obj.portal_type)

            review_state = obj.review_state
            state_class = 'state-' + plone_utils.normalizeString(review_state)
            relative_url = obj.getURL(relative=True)

            fti = portal_types.get(obj.portal_type)
            if fti is not None:
                type_title_msgid = fti.Title()
            else:
                type_title_msgid = obj.portal_type
            url_href_title = u'%s: %s' % (translate(type_title_msgid,
                                                    context=self.request),
                                          safe_unicode(obj.Description))

            creator = obj.Creator
            memberInfo = portal_membership.getMemberInfo(creator)
            creator = memberInfo.get('fullname', '') or creator

            modified = plone_view.toLocalizedTime(
                obj.ModificationDate, long_format=1)

            obj_type = obj.Type
            view_url = url + "/cmsui-structure"

            is_browser_default = len(browser_default[1]) == 1 and (
                obj.id == browser_default[1][0])

            results.append(dict(
                url = url,
                url_href_title = url_href_title,
                id = obj.getId,
                quoted_id = urllib.quote_plus(obj.getId),
                path = path,
                title_or_id = safe_unicode(pretty_title_or_id(plone_utils, obj)),
                obj_type = obj_type,
                creator = creator,
                modified = modified,
                icon = icon.html_tag(),
                type_class = type_class,
                wf_state = review_state,
                state_title = portal_workflow.getTitleForStateOnType(review_state,
                                                           obj_type),
                state_class = state_class,
                is_browser_default = is_browser_default,
                folderish = obj.is_folderish,
                relative_url = relative_url,
                view_url = view_url,
                table_row_class = table_row_class,
                is_expired = isExpired(obj),
            ))
        return results

    @property
    @instance.memoize
    def orderable(self):
        """
        """
        context = aq_inner(self.context)
        if not IOrderableFolder.providedBy(context):
            if hasattr(context, 'moveObjectsByDelta'):
                # for instance, plone site root does not use plone.folder
                return True
            else:
                return False
        ordering = context.getOrdering()
        return IExplicitOrdering.providedBy(ordering)

    @property
    def show_sort_column(self):
        return self.orderable and self.editable

    @property
    def editable(self):
        """
        """
        return self.context_state.is_editable()

    @property
    def buttons(self):
        buttons = []
        context = aq_inner(self.context)
        portal_actions = getToolByName(context, 'portal_actions')
        button_actions = portal_actions.listActionInfos(object=aq_inner(self.context), categories=('folder_buttons', ))

        # Do not show buttons if there is no data, unless there is data to be
        # pasted
        if not len(self.folderitems):
            if self.context.cb_dataValid():
                for button in button_actions:
                    if button['id'] == 'paste':
                        return [self.setbuttonclass(button)]
            else:
                return []

        for button in button_actions:
            # Make proper classes for our buttons
            if button['id'] != 'paste' or context.cb_dataValid():
                buttons.append(self.setbuttonclass(button))
        return buttons

    def setbuttonclass(self, button):
        if button['id'] == 'paste':
            button['cssclass'] = 'standalone'
        else:
            button['cssclass'] = 'context'
        return button


    def msg_select_item(self, item):
        title_or_id = (item.get('title_or_id') or item.get('title') or
                       item.get('Title') or item.get('id') or item['getId'])
        return _(u'checkbox_select_item',
                 default=u"Select ${title}",
                 mapping={'title': safe_unicode(title_or_id)})

    @property
    def within_batch_size(self):
        return len(self.folderitems) <= self.pagesize

    def set_checked(self, item):
        item['checked'] = self.selectall and 'checked' or None
        item['table_row_class'] = item.get('table_row_class', '')

    @property
    @instance.memoize
    def batch(self):
        pagesize = self.pagesize
        if self.show_all:
            pagesize = len(self.folderitems)
        b = Batch(self.folderitems,
                  pagesize=pagesize,
                  pagenumber=self.pagenumber)
        map(self.set_checked, b)
        return b

    def _get_select_all(self):
        return self._select_all

    def _set_select_all(self, value):
        self._select_all = bool(value)

    selectall = property(_get_select_all, _set_select_all)

    # options
    _select_all = False

    @property
    def show_select_all_items(self):
        return not self.selectall

    def get_nosort_class(self):
        """
        """
        return "nosort"

    @lazy_property
    def view_url(self):
        return self.context.absolute_url() + '/cmsui-structure'

    @property
    def selectall_url(self):
        return self.selectnone_url+'&select=all'

    @property
    def selectnone_url(self):
        base = self.view_url + '?pagenumber=%s' % (self.pagenumber)
        if self.show_all:
            base += '&show_all=true'
        return base

    @property
    def show_all_url(self):
        base = self.view_url + '?show_all=true'
        if self.selectall:
            base += '&select=all'
        return base

    def quote_plus(self, string):
        return urllib.quote_plus(string)


    @instance.memoize
    def object_buttons(self):
        """Get the personal actions
        """
        
        actions = []
        for action in self.context_state.actions('object_buttons'):
            actions.append({
                'id': action['id'],
                'url': action['url'],
                'title': action['title'],
                'description': action['description'],
            })
        
        return actions

    def object_info(self):
        info = []
        pt = getToolByName(self.context, 'portal_types')
        fti = pt.listTypeTitles().get(self.context.portal_type, 'unknown')
        info.append({'name' : 'Kind', 'info' : fti.title})
        info.extend([
                {'name' : 'Created', 'info' : self.context.created()},
                {'name' : 'Modified', 'info' : self.context.modified()},
                {'name' : 'Owner', 'info' : self.context.getOwner()},
                ])
        return info
        

class MoveItem(BrowserView):
    """
    Pretty much straight copy of the folder_moveitem.py script
    so we can eventually remove the bloody thing.
    """
    def __call__(self, item_id, delta, subset_ids=None):
        context = aq_inner(self.context)
        try:
            if not IOrderableFolder.providedBy(context):
                if not base_hasattr(context, 'moveObjectsByDelta'):
                    # for instance, plone site root does not use plone.folder
                    raise ValueError("Not an ordered folder.")
            else:
                ordering = context.getOrdering()
                if not IExplicitOrdering.providedBy(ordering):
                    raise ValueError("Ordering disable on folder.")

            delta = int(delta)
            if subset_ids is not None:
                position_id = [(self.context.getObjectPosition(id), id) for id in subset_ids]
                position_id.sort()
                if subset_ids != [id for position, id in position_id]:
                    raise ValueError("Client/server ordering mismatch.")
                self.context.moveObjectsByDelta(item_id, delta, subset_ids)
        except ValueError as e:
            self.context.REQUEST.response.setStatus('BadRequest')
            return str(e)

        plone_utils = getToolByName(self.context, 'plone_utils')
        plone_utils.reindexOnReorder(self.context)
        return "<done />"
