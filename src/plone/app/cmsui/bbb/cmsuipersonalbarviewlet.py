from plone.app.layout.viewlets.common import PersonalBarViewlet
from AccessControl import getSecurityManager


class CMSUIPersonalBarViewlet(PersonalBarViewlet):
    
    def render(self):
        """
        If this user has permission to see the CMSUI viewlet, display that. 
        Otherwise, degrade to old school log in and log out
        """
        if getSecurityManager().checkPermission("plone.ViewCMSUI", self.context):
            return u""
        return PersonalBarViewlet.render(self)