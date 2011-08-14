from datetime import datetime
from DateTime import DateTime

from zExceptions import Unauthorized
from Products.CMFCore.utils import getToolByName
from plone.app.cmsui.interfaces import _

from zope.interface import Interface, implements
from zope import schema
from z3c.form import form, field, button
from zope.schema import vocabulary, interfaces
from z3c.form.browser.radio import RadioFieldWidget


class WorkflowActionsSourceBinder(object):
    implements(interfaces.IContextSourceBinder)
    """Generates vocabulary for all allowed workflow transitions"""

    def getTransitions(self):
        wft = getToolByName(self.context, 'portal_workflow')
        return wft.getTransitionsFor(self.context)

    def __call__(self, context):
        wft = getToolByName(context, 'portal_workflow')
        return vocabulary.SimpleVocabulary([
            vocabulary.SimpleVocabulary.createTerm(t['id'], t['id'], t['name'])
            for t in wft.getTransitionsFor(context)
        ])


class IWorkflowPanel(Interface):
    """Form for workflow panel"""
    workflow_action = schema.Choice(
        title=_(u'label_workflow_action', u"Change State"),
        description=_(u'help_workflow_action',
                          default=u"Select the transition to be used for modifying the items state."),
        source=WorkflowActionsSourceBinder(),
        required=False,
        )
    comment = schema.Text(
        title=_(u"label_comment", u"Comments"),
        description=_(u'help_comment',
                          default=u"Any comments will be added to the publishing history. If multiple "
                                   "items are selected, this comment will be attached to all of them."),
        required=False,
        )
    effective_date = schema.Datetime(
        title=_(u'label_effective_date', u'Publishing Date'),
        description=_(u'help_effective_date',
                          default=u"If this date is in the future, the content will "
                                   "not show up in listings and searches until this date."),
        required=False
        )
    expiration_date = schema.Datetime(
        title=_(u'label_expiration_date', u'Expiration Date'),
        description=_(u'help_expiration_date',
                              default=u"When this date is reached, the content will no"
                                       "longer be visible in listings and searches."),
        required=False
        )


class WorkflowPanel(form.Form):
    """Shows a panel with the advanced workflow options
    """

    @property
    def label(self):
        return _(u'Workflow for ${name}', mapping={'name': self.context.Title()})

    def render(self):
        return self.index()

    css_class = 'overlayForm'

    fields = field.Fields(IWorkflowPanel)
    fields['workflow_action'].widgetFactory = RadioFieldWidget
    ignoreContext = True

    def updateActions(self):
        super(WorkflowPanel, self).updateActions()
        self.actions["cancel"].addClass("overlayCloseAction")

    @button.buttonAndHandler(_(u'Save'))
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # Context might be temporary
        real_context = self.context.portal_factory.doCreate(self.context)

        # Read form
        workflow_action = data.get('workflow_action', '')
        effective_date = data.get('effective_date', None)
        if workflow_action and not effective_date and real_context.EffectiveDate() == 'None':
            effective_date = DateTime()
        expiration_date = data.get('expiration_date', None)

        # Try editing content, might not be able to yet
        retryContentEdit = False
        try:
            self._editContent(real_context, effective_date, expiration_date)
        except Unauthorized:
            retryContentEdit = True

        postwf_context = None
        if workflow_action is not None:
            postwf_context = real_context.portal_workflow.doActionFor(self.context,
                             workflow_action, comment=data.get('comment', ''))
        if postwf_context is None:
            postwf_context = real_context

        # Retry if need be
        if retryContentEdit:
            self._editContent(postwf_context, effective_date, expiration_date)

        self.request.response.redirect(postwf_context.absolute_url())

    @button.buttonAndHandler(_(u'Cancel'))
    def cancel(self, action):
        self.request.response.redirect(self.context.absolute_url())

    def _editContent(self, context, effective, expiry):
        kwargs = {}
        if isinstance(effective, datetime):
            kwargs['effective_date'] = DateTime(effective)
        # may contain the year
        elif effective and (isinstance(effective, DateTime) or len(effective) > 5):
            kwargs['effective_date'] = effective
        if isinstance(expiry, datetime):
            kwargs['expiration_date'] = DateTime(expiry)
        # may contain the year
        elif expiry and (isinstance(expiry, DateTime) or len(expiry) > 5):
            kwargs['expiration_date'] = expiry
        context.plone_utils.contentEdit(context, **kwargs)
