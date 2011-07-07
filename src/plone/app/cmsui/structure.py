from Acquisition import aq_inner, aq_parent
from Products.CMFPlone.utils import pretty_title_or_id, isExpired, base_hasattr, \
    safe_unicode
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interface import IATTopic

from plone.memoize import instance
from plone.app.content.batching import Batch
from plone.registry.interfaces import IRegistry
from plone.folder.interfaces import IOrderableFolder, IExplicitOrdering
from plone.app.cmsui.interfaces import ICMSUISettings

from zope.component import getMultiAdapter, getUtility
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.cachedescriptors.property import Lazy as lazy_property
from zope.publisher.browser import BrowserView

import urllib

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
        self.showAll = self.request.get('show_all', '').lower() == 'true'
        self.selectAll = self.request.get('select', '').lower() == 'all'
        
        return self.index()


    @lazy_property
    def contextState(self):
        return getMultiAdapter((self.context, self.request), 
            name=u'plone_context_state')


    def breadcrumbs(self):
        breadcrumbsView = getMultiAdapter((self.context, self.request), 
            name='breadcrumbs_view')
        breadcrumbs = list(breadcrumbsView.breadcrumbs())
        if self.contextState.is_default_page():
            # then we need to mess with the breadcrumbs a bit.
            parent = aq_parent(aq_inner(self.context))
            if breadcrumbs:
                breadcrumbs[-1] = {
                    'absolute_url' : parent.absolute_url(), 
                    'Title': parent.Title()
                    }
            breadcrumbs.append({
                'absolute_url' : self.context.absolute_url(),
                'Title': self.context.Title()}
                )
        return breadcrumbs


    def contentsMethod(self):
        context = aq_inner(self.context)
        if IATTopic.providedBy(context):
            contentsMethod = context.queryCatalog
        else:
            contentsMethod = context.getFolderContents
        return contentsMethod


    @lazy_property
    def folderItems(self):
        """
        """
        context = aq_inner(self.context)
        ploneUtils = getToolByName(context, 'plone_utils')
        ploneView = getMultiAdapter((context, self.request), name=u'plone')
        ploneLayout = getMultiAdapter((context, self.request), name=u'plone_layout')
        portalWorkflow = getToolByName(context, 'portal_workflow')
        portalTypes = getToolByName(context, 'portal_types')
        portalMembership = getToolByName(context, 'portal_membership')

        browser_default = ploneUtils.browserDefault(context)

        contentsMethod = self.contentsMethod()

        start = 0
        end = start + self.pagesize

        results = []
        for i, obj in enumerate(contentsMethod(self.contentFilter)):
            path = obj.getPath() or "/".join(obj.getPhysicalPath())

            # avoid creating unnecessary info for items outside the current
            # batch;  only the path is needed for the "select all" case...
            if not self.selectAll and not self.showAll and not start <= i < end:
                results.append(dict(path = path))
                continue

            url = obj.getURL()
            viewUrl = url + "/cmsui-structure"
            
            fti = portalTypes.get(obj.portal_type)
            if fti is not None:
                typeTitleMsgid = fti.Title()
            else:
                typeTitleMsgid = obj.portal_type
            urlHrefTitle = u'%s: %s' % (translate(typeTitleMsgid,
                                            context=self.request),
                                            safe_unicode(obj.Description))
            creator = obj.Creator
            memberInfo = portalMembership.getMemberInfo(creator)
            creator = memberInfo.get('fullname', '') or creator

            modified = ploneView.toLocalizedTime(
                obj.ModificationDate, long_format=1)
            
            isBrowserDefault = len(browser_default[1]) == 1 and (
                obj.id == browser_default[1][0])

            results.append(dict(
                url = url,
                urlHrefTitle = urlHrefTitle,
                id = obj.getId,
                quotedId = urllib.quote_plus(obj.getId),
                path = path,
                titleOrId = safe_unicode(pretty_title_or_id(ploneUtils, obj)),
                creator = creator,
                modified = modified,
                icon = ploneLayout.getIcon(obj).html_tag(),
                typeClass = 'contenttype-' + ploneUtils.normalizeString(obj.portal_type),
                wf_state =  obj.review_state,
                stateTitle = portalWorkflow.getTitleForStateOnType(obj.review_state,
                                                           obj.Type),
                stateClass = 'state-' + ploneUtils.normalizeString(obj.review_state),
                isBrowserDefault = isBrowserDefault,
                folderish = obj.is_folderish,
                viewUrl = viewUrl,
                isExpired = isExpired(obj),
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
    def showSortColumn(self):
        return self.orderable and self.editable


    @property
    def editable(self):
        """
        """
        return self.contextState.is_editable()


    @property
    def buttons(self):
        buttons = []
        context = aq_inner(self.context)
        portalActions = getToolByName(context, 'portal_actions')
        buttonActions = portalActions.listActionInfos(
            object=aq_inner(self.context), categories=('folder_buttons',))

        # Do not show buttons if there is no data, unless there is data to be
        # pasted
        if not len(self.folderItems):
            if self.context.cb_dataValid():
                for button in buttonActions:
                    if button['id'] == 'paste':
                        return [self.setButtonClass(button)]
            else:
                return []

        for button in buttonActions:
            # Make proper classes for our buttons
            if button['id'] != 'paste' or context.cb_dataValid():
                buttons.append(self.setButtonClass(button))
        return buttons


    def setButtonClass(self, button):
        if button['id'] == 'paste':
            button['cssclass'] = 'standalone'
        else:
            button['cssclass'] = 'context'
        return button


    def msgSelectItem(self, item):
        titleOrId = (item.get('titleOrId') or item.get('title') or
                       item.get('Title') or item.get('id') or item['getId'])
        return _(u'checkbox_select_item',
                 default=u"Select ${title}",
                 mapping={'title': safe_unicode(titleOrId)})


    def setChecked(self, item):
        item['checked'] = self.selectAll and 'checked' or None


    @lazy_property
    def batch(self):
        pagesize = self.pagesize
        if self.showAll:
            pagesize = len(self.folderItems)
        b = Batch(self.folderItems,
                  pagesize=pagesize,
                  pagenumber=1)
        map(self.setChecked, b)
        return b


    # options
    _select_all = False
    def _getSelectAll(self):
        return self._select_all

    def _setSelectAll(self, value):
        self._select_all = bool(value)
    selectAll = property(_getSelectAll, _setSelectAll)


    @lazy_property
    def viewUrl(self):
        return self.context.absolute_url() + '/cmsui-structure'


    @property
    def selectallUrl(self):
        if '?' in self.selectnoneUrl:
            return self.selectnoneUrl+'&select=all'
        else:
            return self.selectnoneUrl+'?select=all'


    @property
    def selectnoneUrl(self):
        base = self.viewUrl
        if self.showAll:
            if '?' in base:
                base += '&show_all=true'
            else:
                base += '?show_all=true'
        return base


    @property
    def showAllUrl(self):
        base = self.viewUrl + '?show_all=true'
        if self.selectAll:
            base += '&select=all'
        return base


    def quotePlus(self, string):
        return urllib.quote_plus(string)


    @instance.memoize
    def objectButtons(self):
        """
        Get the Actions for the current item.
        """
        actions = []
        for action in self.contextState.actions('object_buttons'):
            actions.append({
                'id': action['id'],
                'url': action['url'],
                'title': action['title'],
                'description': action['description'],
            })        
        return actions


    def objectInfo(self):
        """
        Retrieve information on the current item.
        """
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
                objectPos = self.context.getObjectPosition
                position_id = [(objectPos(id), id) for id in subset_ids]
                position_id.sort()
                if subset_ids != [id for position, id in position_id]:
                    raise ValueError("Client/server ordering mismatch.")
                self.context.moveObjectsByDelta(item_id, delta, subset_ids)
        except ValueError as e:
            self.context.REQUEST.response.setStatus('BadRequest')
            return str(e)

        ploneUtils = getToolByName(self.context, 'plone_utils')
        ploneUtils.reindexOnReorder(self.context)
        return "<done />"
