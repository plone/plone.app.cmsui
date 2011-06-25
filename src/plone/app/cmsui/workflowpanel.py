from Products.CMFCore.utils import getToolByName
from zope.publisher.browser import BrowserView

class WorkflowPanel(BrowserView):
    """Shows a panel wit the adanced workflow options
    """
    
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
                return "Complete"
        self.request.RESPONSE.redirect(self.context.absolute_url())
    
    def getTransitions(self):
        wft = getToolByName(self.context, 'portal_workflow')
        return wft.getTransitionsFor(self.context)
    
