import unittest2 as unittest

from plone.app.cmsui.testing import CMSUI_FUNCTIONAL_TESTING
from plone.app.cmsui.testing import browser_login
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.testing.z2 import Browser
import transaction

class TestWorkflowPanel(unittest.TestCase):

    layer = CMSUI_FUNCTIONAL_TESTING

    def test_panel_linked_to_in_menu(self):
        self.browser = Browser(self.layer['app'])
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Member', 'Manager'))
        # Commit so the change in roles is visible to the browser
        transaction.commit()
        
        browser_login(portal, self.browser)
        self.browser.open(portal.absolute_url())
        self.browser.getLink("Manage page").click()
        
        # raises exception if not present
        self.browser.getLink("Workflow actions").click()
        self.assertIn("Workflow panel", self.browser.contents)
    
    def test_available_workflow_transition_shown_in_workflow_panel(self):
        self.browser = Browser(self.layer['app'])
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Member', 'Manager'))
        document_id = portal.invokeFactory("Document", "transition_shown_in_workflow_panel_doc", title="Workflow transitions")
        document = portal[document_id]
        # Commit so the change in roles is visible to the browser
        transaction.commit()
        
        browser_login(portal, self.browser)
        self.browser.open(document.absolute_url())
        self.browser.getLink("Manage page").click()
        self.browser.getLink("Workflow actions").click()
        
        # The submit button should be available
        transitions = portal.portal_workflow.getTransitionsFor(document)
        transition_ids = [transition['id'] for transition in transitions]
        # Ensure the workflow transition we are going to look for in the
        # workflow panel is actually available to save debugging headaches
        # later
        self.assertEqual(sorted(['submit', 'hide', 'publish']), sorted(transition_ids))
        
        workflow_actions = self.browser.getControl(name="workflow_action")
        submit_control = workflow_actions.getControl(value="submit")
        hide_control = workflow_actions.getControl(value="hide")
        publish_control = workflow_actions.getControl(value="publish")
        
        # Ugly, but it will do
        self.assertEqual('Member submits content for publication', submit_control.mech_item.attrs['title'])
        self.assertEqual('Member makes content private', hide_control.mech_item.attrs['title'])
        self.assertEqual('Reviewer publishes content', publish_control.mech_item.attrs['title'])
    
