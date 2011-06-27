from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from plone.app.z3cform.layout import wrap_form
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.namedfile.field import NamedFile
from plone.z3cform.interfaces import IWrappedForm
from z3c.form import button, form, field
from z3c.form.interfaces import HIDDEN_MODE
from zope import interface, schema
from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.component import getUtility, queryUtility, getMultiAdapter
from zope.container.interfaces import INameChooser
from zope.interface import implements
from zope.publisher.browser import BrowserView


class IAddNewContent(interface.Interface):

    title = schema.TextLine(title=u"Title")
    type_name = schema.TextLine(title=u"Type")


class AddNewContentForm(form.Form):
    
    fields = field.Fields(IAddNewContent)
    ignoreContext = True # don't use context to get widget data
    label = "Add content"
    css_class = 'overlayForm'
    
    def update(self):
        tn = self.fields['type_name']
        tn.mode = HIDDEN_MODE
        tn.field.default = unicode(getattr(self.request, 'type_name', ''))
        super(AddNewContentForm, self).update()

    @button.buttonAndHandler(u'Add content')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            return
        
        title = data['title']
        
        # Generate a name based on the title..
        util = queryUtility(IIDNormalizer)
        id = util.normalize(title)
        
        # Context may not be a container, get one.
        context_state = getMultiAdapter((self.context, self.request), name="plone_context_state")
        container = context_state.folder()
        
        # Make sure our chosen id is unique, iterate until we get one that is.
        chooser = INameChooser(container)
        id = chooser._findUniqueName(id, None)

        # create the object
        container.invokeFactory(data['type_name'], id=id, title=title)
        
        self.request.response.redirect("%s/edit" % container[id].absolute_url())

AddNewContentView = wrap_form(AddNewContentForm)


class IFileUploadForm(interface.Interface):
    file = NamedFile(title=u"File")

class FileUploadForm(form.Form):
    implements(IWrappedForm)
    
    fields = field.Fields(IFileUploadForm)
    ignoreContext = True # don't use context to get widget data
    label = "Add content"
    
    @button.buttonAndHandler(u'Upload content')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            return
            
        # Context may not be a container, get one.
        context_state = getMultiAdapter((self.context, self.request), name="plone_context_state")
        container = context_state.folder()

        title = data['file'].filename
        # Generate a name based on the title..
        util = queryUtility(IIDNormalizer)
        id = util.normalize(title)
        
        # Make sure our chosen id is unique, iterate until we get one that is.
        chooser = INameChooser(container)
        id = chooser._findUniqueName(id, None)

        # Determine the Content Type
        ct_reg = getToolByName(self.context, 'content_type_registry')
        typeName = ct_reg.findTypeName(data['file'].filename, 
                                       data['file'].contentType,
                                       data['file'].data)

        # Really, we want Image if it's an image, and File for everything else...
        typeName = 'Image' if typeName == 'Image' else 'File'

        # create the object
        container.invokeFactory(typeName, 
                                id=id,
                                title=title,
                                file=data['file'].data)

        # Redirect to the view page.
        self.request.response.redirect("%s/view" % container[id].absolute_url())


class AddMenu(BrowserView):
    """Add menu overlay
    """
    
    def __call__(self):
        # Disable theming
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        
        # Get this of types addable here, by this user.
        factoriesMenu = getUtility(IBrowserMenu, name='plone_contentmenu_factory', context=self.context)
        self.addable_types = factoriesMenu.getMenuItems(self.context, self.request)

        breadcrumbs_view = getMultiAdapter((self.context, self.request),
                                           name='breadcrumbs_view')
        self.breadcrumbs = breadcrumbs_view.breadcrumbs()
        
        factories_view = getMultiAdapter((self.context, self.request), name='folder_factories')
        
        self.allowedTypes = factories_view.addable_types()
        
        self.uploadForm = FileUploadForm(self.context, self.request)
        self.uploadForm.update()
        
        
        return self.index()

    def showUploadForm(self):
        """We can't show the upload form if uploadable types can't be created here.
        """
        # TODO How are we sure which types are uploadable?
        # For now, just check on File/Image.
        uploadTypes = ['Image','File']
        for a in self.allowedTypes:
            if a['id'] in uploadTypes:
                return True
        return False

    def getUploadUrl(self):
        """
        return upload url in current folder
        """
        ploneview = getMultiAdapter((self.context, self.request), name="plone")

        folder_url = ploneview.getCurrentFolderUrl()                      
        return '%s/@@quick_upload' %folder_url

    def getDataForUploadUrl(self):
        return 'data_url'
