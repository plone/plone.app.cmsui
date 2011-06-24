from Products.CMFCore.utils import getToolByName
from zope.publisher.browser import BrowserView

class WorkflowPanel(BrowserView):
    """Shows a panel wit the adanced workflow options
    """
    
    def __call__(self):
        # Disable theming
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        return self.index()
    
    def getTransitions(self):
        wft = getToolByName(self.context, 'portal_workflow')
        return wft.getTransitionsFor(self.context)
    
