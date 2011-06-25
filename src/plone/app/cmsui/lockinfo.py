from zope.component import getMultiAdapter
from zope.publisher.browser import BrowserView
from plone.memoize.instance import memoize

class LockInfo(BrowserView):
    """Manage locks
    """
    
    def __call__(self):
        # Disable theming
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        return self.index()
    
    @memoize
    def lock_info(self):
        return getMultiAdapter((self.context, self.request), name="plone_lock_info")
