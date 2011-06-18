from zope.viewlet.viewlet import ViewletBase

class NullViewlet(ViewletBase):
    """Simply view that renders an empty string.
    
    For BBB purposes, to disable certain viewlets, we register an override
    for the same name and context, specific to the ICMSUILayer layer, using
    this class to render nothing.
    """
    
    def render(self):
        return u""
