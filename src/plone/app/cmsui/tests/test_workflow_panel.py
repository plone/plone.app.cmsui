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
        browser = Browser(self.layer['app'])
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Member', 'Manager'))
        document_id = portal.invokeFactory("Document", "panel_linked_to_in_menu_doc", title="Workflow transitions")
        document = portal[document_id]
        # Commit so the change in roles is visible to the browser
        transaction.commit()
        
        browser_login(portal, browser)
        browser.open(document.absolute_url())
        browser.getLink("Manage page").click()
        
        # raises exception if not present
        browser.getLink("Public draft").click()
        self.assertIn("form.widgets.workflow_action", browser.contents)

    def test_available_workflow_transition_shown_in_workflow_panel(self):
        browser = Browser(self.layer['app'])
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Member', 'Manager'))
        document_id = portal.invokeFactory("Document", "transition_shown_in_workflow_panel_doc", title="Workflow transitions")
        document = portal[document_id]
        # Commit so the change in roles is visible to the browser
        transaction.commit()
        
        browser_login(portal, browser)
        browser.open(document.absolute_url())
        browser.getLink("Manage page").click()
        browser.getLink("Public draft").click()
        
        # The submit button should be available
        transitions = portal.portal_workflow.getTransitionsFor(document)
        transition_ids = [transition['id'] for transition in transitions]
        # Ensure the workflow transition we are going to look for in the
        # workflow panel is actually available to save debugging headaches
        # later
        self.assertEqual(sorted(['submit', 'hide', 'publish']), sorted(transition_ids))
        
        # Make sure we have both labels and values for all possible workflow actions
        workflow_actions = browser.getControl(name="form.widgets.workflow_action:list")
        self.assertEqual(len(workflow_actions.mech_control.items),3)
        self.assertEqual(workflow_actions.getControl(label='Member submits content for publication').optionValue, 'submit')
        self.assertEqual(workflow_actions.getControl(label='Member makes content private').optionValue, 'hide')
        self.assertEqual(workflow_actions.getControl(label='Reviewer publishes content').optionValue, 'publish')
    
    def test_choosing_transition_transitions_content(self):
        browser = Browser(self.layer['app'])
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Member', 'Manager'))
        document_id = portal.invokeFactory("Document", "do_workflow_transition_doc", title="Workflow transitioning")
        document = portal[document_id]
        transaction.commit()
        
        browser_login(portal, browser)
        browser.open(document.absolute_url())
        browser.getLink("Manage page").click()
        browser.getLink("Public draft").click()
        workflow_actions = browser.getControl(name="form.widgets.workflow_action:list")
        workflow_actions.getControl(value="publish").click()
        browser.getControl("Save").click()
        
        self.assertEqual("published", portal.portal_workflow.getInfoFor(document, "review_state"))
    
    def test_can_enter_changenote(self):
        browser = Browser(self.layer['app'])
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Member', 'Manager'))
        document_id = portal.invokeFactory("Document", "changenote_transition_doc", title="Workflow note")
        document = portal[document_id]
        transaction.commit()
        
        browser_login(portal, browser)
        browser.open(document.absolute_url())
        browser.getLink("Manage page").click()
        browser.getLink("Public draft").click()
        workflow_actions = browser.getControl(name="form.widgets.workflow_action:list")
        workflow_actions.getControl(value="publish").click()
        # We set up a comment this time
        browser.getControl(name="form.widgets.comment").value = "wibble fkjwel"
        browser.getControl("Save").click()
        
        # and it shows up in the workflow history
        self.assertEqual("publish", document.workflow_history['plone_workflow'][-1]['action'])
        self.assertEqual("wibble fkjwel", document.workflow_history['plone_workflow'][-1]['comments'])
    
