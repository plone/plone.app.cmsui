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
    
    