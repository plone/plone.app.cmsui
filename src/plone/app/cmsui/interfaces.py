from zope.interface import Interface
from zope import schema
from zope.i18nmessageid import MessageFactory

_ = MessageFactory(u"plone")

class ICMSUISettings(Interface):
    """CMS UI settings stored in the registry
    """

    folder_contents_batch_size = schema.Int(title=_(u"Folder Contents Batch Size"), default=30)

class ICMSUILayer(Interface):
    """Browser layer used to indicate that plone.app.cmsui is installed
    """

# TODO Stolen from collective.quickupload, refactor
from zope.interface import Interface
from zope.filerepresentation.interfaces import IFileFactory

class IQuickUploadCapable(Interface):
    """Any container/object which supports quick uploading
    """

class IQuickUploadFileFactory(IFileFactory):
    """used for QuickUploadFileFactory
    """

