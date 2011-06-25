from plone.app.content.browser.folderfactories import _allowedTypes
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.z3cform.interfaces import IWrappedForm
from z3c.form import button, form, field
from z3c.form.browser.radio import RadioFieldWidget
from zope import interface, schema
from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.component import getUtility, queryUtility, getMultiAdapter
from zope.container.interfaces import INameChooser
from zope.interface import implements
from zope.publisher.browser import BrowserView
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


class AddableTypesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getattr(context, 'context', context)
        request = context.REQUEST
        
        factories_view = getMultiAdapter((context, request), name='folder_factories')

        addContext = factories_view.add_context()
        allowedTypes = _allowedTypes(request, addContext)
        items = [SimpleTerm(i.id, i.id, i.Title()) for i in allowedTypes]
        return SimpleVocabulary(items)

AddableTypesVocabularyFactory = AddableTypesVocabulary()


class IAddMenu(interface.Interface):

    title = schema.TextLine(title=u"Title")
    content_type = schema.Choice(title=u"Type", vocabulary=u"plone.app.cmsui.AddableContentTypes")


class AddForm(form.Form):
    implements(IWrappedForm)
    
    fields = field.Fields(IAddMenu)
    ignoreContext = True # don't use context to get widget data
    label = "Add content"

    fields['content_type'].widgetFactory = RadioFieldWidget
    
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
        container.invokeFactory(data['content_type'], id=id, title=title)
        # redirect to immediate_view
        self.request.response.redirect("%s/edit" % container[id].absolute_url())
        # open edit overlay    


class AddMenu(BrowserView):
    """Add menu overlay
    """
    
    def __call__(self):
        # Disable theming
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        
        factoriesMenu = getUtility(IBrowserMenu, name='plone_contentmenu_factory', context=self.context)
        self.addable_types = factoriesMenu.getMenuItems(self.context, self.request)

        breadcrumbs_view = getMultiAdapter((self.context, self.request),
                                           name='breadcrumbs_view')
        self.breadcrumbs = breadcrumbs_view.breadcrumbs()
        
        factories_view = getMultiAdapter((self.context, self.request), name='folder_factories')
        
        self.allowedTypes = factories_view.addable_types()
        
        
        return self.index()


        
        
        
