from zope.publisher.browser import BrowserView

class Menu(BrowserView):
    """The view containing the overlay menu
    """
    
    def __call__(self):
        # Disable theming
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        return self.index()
