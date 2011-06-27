from zope.interface import Interface
from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.filerepresentation.interfaces import IFileFactory

_ = MessageFactory(u"plone")

class ICMSUISettings(Interface):
    """CMS UI settings stored in the registry
    """
    
    skinName = schema.ASCIILine(
            title=_(u"CMS UI theme name"),
            default='cmsui',
        )
    
    folderContentsBatchSize = schema.Int(
            title=_(u"Folder Contents Batch Size"),
            default=30,
        )
    
    editActionId = schema.ASCIILine(
            title=_(u"Edit action id"),
            default='edit',
        )
    
    excludedActionIds = schema.Tuple(
            title=_(u"Actions not shown in the more menu"),
            default=('view', 'edit'),
        )
    
    defaultActionIcon = schema.ASCIILine(
            title=_(u"Default action icon path"),
            default='/++resource++plone.app.cmsui/icons/List.png',
        )

class ICMSUILayer(Interface):
    """Browser layer used to indicate that plone.app.cmsui is installed
    """

class IQuickUploadCapable(Interface):
    """Any container/object which supports quick uploading
    """

class IQuickUploadFileFactory(IFileFactory):
    """used for QuickUploadFileFactory
    """

