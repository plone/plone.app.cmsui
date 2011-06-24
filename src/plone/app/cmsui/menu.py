from zope.component import getMultiAdapter
from zope.publisher.browser import BrowserView
from plone.memoize.instance import memoize

from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName

class Menu(BrowserView):
    """The view containing the overlay menu
    """
    
    def __call__(self):
        # Disable theming
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        
        # Commonly useful variables
        self.contextState = getMultiAdapter((self.context, self.request), name=u'plone_context_state')
        self.portalState = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
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
        
        membership = getToolByName(self.context, 'portal_membership')
        memberInfo = membership.getMemberInfo(userid)
        
        fullname = userid
        
        # Member info is None if there's no Plone user object, as when using OpenID.
        if memberInfo is not None:
            fullname = memberInfo.get('fullname', '') or fullname
        
        return fullname
    
    @memoize
    def userHomeLinkURL(self):
        if self.securityManager.checkPermission('Portlets: View dashboard', self.context):
            return "%s/dashboard" % self.portalState.navigation_root_url()
        else:
            return "%s/personalize_form" % self.portalState.navigation_root_url()
    
    @memoize
    def breadcrumbs(self):
        breadcrumbsView = getMultiAdapter((self.context, self.request), name='breadcrumbs_view')
        return breadcrumbsView.breadcrumbs()
