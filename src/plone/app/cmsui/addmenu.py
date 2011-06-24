from zope.component import queryUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.app.content.browser.folderfactories import _allowedTypes
from plone.app.z3cform.layout import wrap_form
from z3c.form import button, form, field
from zope import interface, schema
from zope.component import getMultiAdapter
from zope.interface import implements
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


class AddMenu(form.Form):
    fields = field.Fields(IAddMenu)
    ignoreContext = True # don't use context to get widget data
    label = "Add content"
    
    
    @button.buttonAndHandler(u'Add content')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            return
        # invoke factory
        title = data['title']
        # title-to-id
        util = queryUtility(IIDNormalizer)
        id = util.normalize(title)
        # create the object
        self.context.invokeFactory('Document', id=id, title=title)
        # redirect to immediate_view
        # open edit overlay    

AddForm = wrap_form(AddMenu)



# class AddMenu(BrowserView):
#     """Add menu overlay
#     """
#     
#     def __call__(self):
#         # Disable theming
#         self.request.response.setHeader('X-Theme-Disabled', 'True')
#         
#         factoriesMenu = getUtility(IBrowserMenu, name='plone_contentmenu_factory', context=self.context)
#         self.addable_types = factoriesMenu.getMenuItems(self.context, self.request)
# 
#         breadcrumbs_view = getMultiAdapter((self.context, self.request),
#                                            name='breadcrumbs_view')
#         self.breadcrumbs = breadcrumbs_view.breadcrumbs()
#         
#         return self.index()
# 
# 
#         
#         
#         
