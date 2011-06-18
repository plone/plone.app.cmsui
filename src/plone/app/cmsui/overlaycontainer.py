from zope.publisher.browser import BrowserView

class OverlayContainer(BrowserView):
    """View that provides a main_template replacement for overlays.
    
    Use metal:use-macro="context/@@cmsui-overlay-container/macros/master"
    and then fill the main macro.
    """
    
    def __call__(self):
        # Disable theming
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        return self.index()

    @property
    def macros(self):
        return self.index.macros
