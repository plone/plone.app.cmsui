from zope.component import getMultiAdapter
from zope.publisher.browser import BrowserView
from plone.memoize.instance import memoize

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
        
        # Commonly useful variables
        self.contextState = getMultiAdapter((self.context, self.request), name=u'plone_context_state')
        self.portalState = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.tools = getMultiAdapter((self.context, self.request), name=u'plone_tools')
        self.securityManager = getSecurityManager()
        self.anonymous = self.portalState.anonymous()
        
        # Render the template
        return self.index()

    # Personal actions
    
    @memoize
    def personalActions(self):
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
        member = self.portalState.member()
        userid = member.getId()
        return "%s/author/%s" % (self.portalState.navigation_root_url(), userid)
    
    @memoize
    def breadcrumbs(self):
        breadcrumbsView = getMultiAdapter((self.context, self.request), name='breadcrumbs_view')
        return breadcrumbsView.breadcrumbs()
    
    @memoize
    def modificationDate(self):
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
        acl_users, owner = self.context.getOwnerTuple()
        membership = self.tools.membership()
        memberInfo = membership.getMemberInfo(owner)
        return memberInfo.get('fullname', '') or owner
    
    @memoize
    def workflowState(self):
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
        folder = self.contextState.folder()
        
        if IPloneSiteRoot.providedBy(folder):
            return len(folder.contentIds())
        
        # XXX: Assumes other folders behave well and only contain content
        return len(folder)

    @memoize
    def editLink(self):
        objectActions = self.contextState.actions('object')
        for action in objectActions:
            if action['id'] == 'edit':
                return action['url']
        return None
    
    @memoize
    def baseURL(self):
        return self.context.absolute_url()
