from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.component import getUtility
from zope.publisher.browser import BrowserView

class AddMenu(BrowserView):
    """Add menu overlay
    """
    
    def __call__(self):
        # Disable theming
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        
        factoriesMenu = getUtility(IBrowserMenu, name='plone_contentmenu_factory', context=self.context)
        self.addable_types = factoriesMenu.getMenuItems(self.context, self.request)


        return self.index()
