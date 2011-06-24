from zope.publisher.browser import BrowserView

class AddMenu(BrowserView):
    """Add menu overlay
    """
    
    def __call__(self):
        # Disable theming
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        return self.index()
