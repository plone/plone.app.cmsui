from Products.CMFCore.utils import getToolByName
from zope.publisher.browser import BrowserView
from plone.app.cmsui.interfaces import _

from zope.interface import Interface, implements
from zope import schema
from z3c.form import form, field, button
from zope.schema import vocabulary, interfaces
from z3c.form.browser.radio import RadioFieldWidget

class WorkflowActionsSourceBinder(object):
    implements(interfaces.IContextSourceBinder)
    """Generates vocabulary for all allowed workflow transitions"""
    
    def __call__(self):
        # Disable theming
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        if self.request.method == "GET":
            return self.index()
        else:
            if not 'form.button.folderPublish' in self.request.form:
                return self.request.RESPONSE.redirect(self.context.absolute_url())
            action = self.request.form.get('workflow_action', None)
            if action is not None:
                self.context.portal_workflow.doActionFor(self.context, action, comment=self.request.form.get('comment', ''))
        self.request.RESPONSE.redirect(self.context.absolute_url())
    
    def getTransitions(self):
        wft = getToolByName(self.context, 'portal_workflow')
        return wft.getTransitionsFor(self.context)
    
    def __call__(self, context):
        wft = getToolByName(context, 'portal_workflow')
        return vocabulary.SimpleVocabulary([
            vocabulary.SimpleVocabulary.createTerm(t['id'],t['id'],t['title'])
            for t in wft.getTransitionsFor(context)
        ])

class IWorkflowPanel(Interface):
    """Form for workflow panel"""
    workflow_action = schema.Choice(
        title = _(u'label_workflow_action', u"Change State"),
        description = _(u'help_workflow_action',
                          default=u"Select the transition to be used for modifying the items state."),
        source= WorkflowActionsSourceBinder(),
        required= False,
        )
    comment = schema.Text(
        title = _(u"label_comment", u"Comments"),
        description = _(u'help_comment',
                          default=u"Will be added to the publishing history. If multiple "
                                   "items are selected, this comment will be attached to all of them."),
        required= False,
        )

class WorkflowPanel(form.Form):
    """Shows a panel with the adanced workflow options
    """
    fields = field.Fields(IWorkflowPanel)
    fields['workflow_action'].widgetFactory = RadioFieldWidget
    ignoreContext = True

    @button.buttonAndHandler(u'Save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        
        workflow_action = data.get('workflow_action', '')
        if workflow_action is not None:
            self.context.portal_workflow.doActionFor(self.context, workflow_action, comment=data.get('comment', ''))
        self.request.response.redirect(self.context.absolute_url())

    @button.buttonAndHandler(u'Cancel')
    def cancel(self, action):
        self.request.response.redirect(self.context.absolute_url())
