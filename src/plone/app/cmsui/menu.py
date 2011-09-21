from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.publisher.browser import BrowserView
from plone.registry.interfaces import IRegistry
from plone.memoize.instance import memoize
from plone.app.cmsui.interfaces import ICMSUISettings

from Acquisition import aq_base
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot


class Menu(BrowserView):
    """The view containing the overlay menu
    """
    
    def __call__(self):
        # Disable theming
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        
        # Set the CMSUI skin so that we get the correct resources
        self.context.changeSkin(self.settings.skinName, self.request)
        
        # Commonly useful variables
        self.securityManager = getSecurityManager()
        self.anonymous = self.portalState.anonymous()
        self.tools = getMultiAdapter((self.context, self.request), name=u'plone_tools')
        
        # Render the template
        return self.index()

    # Personal actions

    @property
    @memoize
    def contextState(self):
        return getMultiAdapter((self.context, self.request), name=u'plone_context_state')

    @property
    @memoize
    def portalState(self):
        return getMultiAdapter((self.context, self.request), name=u'plone_portal_state')

    @property
    @memoize
    def settings(self):
        return getUtility(IRegistry).forInterface(ICMSUISettings, False)

    @memoize
    def personalActions(self):
        """Get the personal actions
        """
        actions = []
        for action in self.contextState.actions('user'):
            actions.append({
                'id': action['id'],
                'url': action['url'],
                'title': action['title'],
                'description': action['description'],
            })
        
        return actions

    @memoize
    def userName(self):
        """Get the username of the currently logged in user
        """
        if self.anonymous:
            return None
        
        member = self.portalState.member()
        userid = member.getId()
        
        membership = self.tools.membership()
        memberInfo = membership.getMemberInfo(userid)
        
        fullname = userid
        
        # Member info is None if there's no Plone user object, as when using OpenID.
        if memberInfo is not None:
            fullname = memberInfo.get('fullname', '') or fullname
        
        return fullname
    
    @memoize
    def userHomeLinkURL(self):
        """Get the URL of the user's home page (profile age)
        """
        member = self.portalState.member()
        userid = member.getId()
        return "%s/author/%s" % (self.portalState.navigation_root_url(), userid)
    
    @memoize
    def breadcrumbs(self):
        """Get the breadcrumbs data structure
        """
        breadcrumbsView = getMultiAdapter((self.context, self.request), name='breadcrumbs_view')
        return breadcrumbsView.breadcrumbs()
    
    @memoize
    def modificationDate(self):
        """Get the modification date for display purposes
        """
        if hasattr(aq_base(self.context), 'modified'):
            modifiedDate = self.context.modified()
        
            translationService = getToolByName(self.context, 'translation_service')
            return translationService.ulocalized_time(modifiedDate,
                    context=self.context,
                    domain='plonelocales'
                )
        
        return None
    
    @memoize
    def authorName(self):
        """Get the full name of the author
        """
        
        owner = None
        if hasattr(aq_base(self.context), 'Creator'):
            owner = self.context.Creator()
        if owner is None:
            acl_users, owner = self.context.getOwnerTuple()
        
        membership = self.tools.membership()
        memberInfo = membership.getMemberInfo(owner)
        return memberInfo.get('fullname', '') or owner
    
    @memoize
    def workflowState(self):
        """Get the name of the workflow state
        """
        state = self.contextState.workflow_state()
        if state is None:
            return None
        
        workflows = self.tools.workflow().getWorkflowsFor(self.context)
        if workflows:
            for w in workflows:
                if w.states.has_key(state):
                    return w.states[state].title or state
        
        return state
    
    @memoize
    def itemsInFolder(self):
        """Count the items in the screen
        """
        folder = self.contextState.folder()
        
        if IPloneSiteRoot.providedBy(folder):
            return len(folder.contentIds())
        
        # XXX: Assumes other folders behave well and only contain content
        return len(folder)

    @memoize
    def editLink(self):
        """Get the URL of the edit action - taking locking into account
        """
        
        if not self.securityManager.checkPermission('Modify portal content', self.context):
            return None
        
        if self.contextState.is_locked():
            return self.context.absolute_url() + "/@@cmsui-lock-info"
        
        objectActions = self.contextState.actions('object')
        for action in objectActions:
            if action['id'] == self.settings.editActionId:
                return "%s?last_referer=%s" % (action['url'], self.context.absolute_url())
        
        return None
        
    @memoize
    def deleteLink(self):
        """Get the URL of the delete action - also looks at locking
        """
        
        if not self.securityManager.checkPermission('Delete objects', self.context):
            return None
        
        if self.contextState.is_locked():
            return self.context.absolute_url() + "/@@cmsui-lock-info"
        
        objectButtons = self.contextState.actions('object_buttons')
        for action in objectButtons:
            if action['id'] == 'delete':
                return "%s" % (action['url'])
        
        return None
    
    
    @memoize
    def settingsActions(self):
        """Render every action other than the excluded ones (edit, view).
        Use the action icon if applicable, but fall back on the default icon.
        """
        
        actions = []
        objectActions = self.contextState.actions('object')
        
        defaultIcon = self.portalState.navigation_root_url() + self.settings.defaultActionIcon
        
        for action in objectActions:
            if action['id'] in self.settings.excludedActionIds:
                continue
            
            icon = action['icon']
            if not icon:
                icon = defaultIcon
            
            actions.append({
                'id': action['id'],
                'url': action['url'],
                'title': action['title'],
                'description': action['description'],
                'icon': icon,
            })
        
        return actions
    
    @memoize
    def baseURL(self):
        return self.context.absolute_url()

    def canAdd(self):
        pm = getToolByName(self.context, 'portal_membership')
        return pm.checkPermission('Add portal content', self.context)

    def canListFolderContents(self):
        pm = getToolByName(self.context, 'portal_membership')
        return pm.checkPermission('List folder contents', self.context)

    def canChangeState(self):
        wft = getToolByName(self.context, 'portal_workflow')
        return len(wft.getTransitionsFor(self.context))>0

    def canAccessHistory(self):
        pm = getToolByName(self.context, 'portal_membership')
        return pm.checkPermission('CMFEditions: Access previous versions', self.context)
