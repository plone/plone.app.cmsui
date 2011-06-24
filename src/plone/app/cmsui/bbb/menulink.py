from zope.viewlet.viewlet import ViewletBase

class MenuLinkViewlet(ViewletBase):
    
    def getLink(self):
        return self.context.absolute_url()+"/@@cmsui-menu"
