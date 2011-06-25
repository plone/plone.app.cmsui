import unittest2 as unittest

from plone.app.cmsui.testing import CMSUI_FUNCTIONAL_TESTING
from plone.app.cmsui.testing import browser_login
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.testing.z2 import Browser
import transaction

class TestMenuLink(unittest.TestCase):

    layer = CMSUI_FUNCTIONAL_TESTING

    def test_menu_sublinks_rendered_in_correct_context(self):
        """
        The menu link was rendered as a relative link, which means it generally
        wasn't on the correct context.  e.g. /news/@@cmsui-menu is the folder,
        not the default view.
        """

        browser = Browser(self.layer['app'])
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Member', 'Manager'))
        document_id = portal.invokeFactory("Document", "menu_test_context", title="Context test")
        document = portal[document_id]
        # Commit so the change in roles is visible to the browser
        transaction.commit()
        
        browser_login(portal, browser)
        browser.open(document.absolute_url())
        browser.getLink("Manage page").click()
        self.assertIn("menu_test_context", browser.url)
    
