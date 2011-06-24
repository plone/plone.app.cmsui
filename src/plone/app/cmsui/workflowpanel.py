from zope.publisher.browser import BrowserView

class WorkflowPanel(BrowserView):
    """Shows a panel wit the adanced workflow options
    """
    
    def __call__(self):
        # Disable theming
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        return self.index()
