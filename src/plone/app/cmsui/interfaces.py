from zope.interface import Interface
from zope import schema
from zope.i18nmessageid import MessageFactory

_ = MessageFactory(u"plone")

class ICMSUISettings(Interface):
    """CMS UI settings stored in the registry
    """

class ICMSUILayer(Interface):
    """Browser layer used to indicate that plone.app.cmsui is installed
    """
