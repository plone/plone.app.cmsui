import unittest2 as unittest

import transaction
from plone.testing.z2 import Browser
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.cmsui.testing import CMSUI_FUNCTIONAL_TESTING
from plone.app.cmsui.testing import browser_login
from plone.app.cmsui.tests import createObject


class TestPermissions(unittest.TestCase):

    layer = CMSUI_FUNCTIONAL_TESTING

    def setUp(self):
        portal = self.layer['portal']
        acl_users = portal.acl_users
        acl_users.userFolderAddUser('other_user', 'secret', ['Manager'], [])
        login(portal, 'other_user')
        createObject(portal, 'Folder', 'empty-folder', delete_first=True, title=u"Folder 1")
        transaction.commit()
        self.portal = portal

    def test_not_visible_to_anon(self):
        browser = Browser(self.layer['app'])
        browser.open('http://nohost/plone/cmsui-structure')
        self.assertTrue('Log in' in browser.contents)

    def test_visible_to_members(self):
        browser = Browser(self.layer['app'])
        browser_login(self.portal, browser)
        browser.open('http://nohost/plone/cmsui-menu')
        self.assertTrue('Logged in as test_user_1_')

    def test_add_button_permission(self):
        browser = Browser(self.layer['app'])
        browser_login(self.portal, browser)
        browser.open('http://nohost/plone/empty-folder/cmsui-menu')
        self.assertTrue('folder-add_content' not in browser.contents)
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Contributor'])
        transaction.commit()
        browser.open('http://nohost/plone/empty-folder/cmsui-menu')
        self.assertTrue('folder-add_content' in browser.contents)

    def test_structure_button_permission(self):
        browser = Browser(self.layer['app'])
        browser_login(self.portal, browser)
        browser.open('http://nohost/plone/empty-folder/cmsui-menu')
        self.assertTrue('structure' not in browser.contents)
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Contributor'])
        transaction.commit()
        browser.open('http://nohost/plone/empty-folder/cmsui-menu')
        self.assertTrue('structure' in browser.contents)

    def test_edit_button_permission(self):
        browser = Browser(self.layer['app'])
        browser_login(self.portal, browser)
        browser.open('http://nohost/plone/empty-folder/cmsui-menu')
        self.assertTrue('document-edit' not in browser.contents)
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Editor'])
        transaction.commit()
        browser.open('http://nohost/plone/empty-folder/cmsui-menu')
        self.assertTrue('document-edit' in browser.contents)

    def test_delete_button_permission(self):
        browser = Browser(self.layer['app'])
        browser_login(self.portal, browser)
        browser.open('http://nohost/plone/empty-folder/cmsui-menu')
        self.assertTrue('document-delete' not in browser.contents)
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Editor'])
        transaction.commit()
        browser.open('http://nohost/plone/empty-folder/cmsui-menu')
        self.assertTrue('document-delete' in browser.contents)

    def test_workflow_button_permission(self):
        browser = Browser(self.layer['app'])
        browser_login(self.portal, browser)
        browser.open('http://nohost/plone/empty-folder/cmsui-menu')
        self.assertTrue('plone-contentmenu-workflow' not in browser.contents)
        self.assertTrue('Status:' in browser.contents)
        self.assertTrue('Public draft' in browser.contents)
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Reviewer'])
        transaction.commit()
        browser.open('http://nohost/plone/empty-folder/cmsui-menu')
        self.assertTrue('plone-contentmenu-workflow' in browser.contents)

    def test_history_button_permission(self):
        browser = Browser(self.layer['app'])
        browser_login(self.portal, browser)
        browser.open('http://nohost/plone/empty-folder/cmsui-menu')
        self.assertTrue('document-history' not in browser.contents)
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Editor'])
        transaction.commit()
        browser.open('http://nohost/plone/empty-folder/cmsui-menu')
        self.assertTrue('document-history' in browser.contents)

    def test_sharing_button_permission(self):
        browser = Browser(self.layer['app'])
        browser_login(self.portal, browser)
        browser.open('http://nohost/plone/empty-folder/cmsui-menu')
        self.assertTrue('document-author' not in browser.contents)
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Editor'])
        transaction.commit()
        browser.open('http://nohost/plone/empty-folder/cmsui-menu')
        self.assertTrue('document-author' in browser.contents)

    def test_site_setup_button_permission(self):
        browser = Browser(self.layer['app'])
        browser_login(self.portal, browser)
        browser.open('http://nohost/plone/empty-folder/cmsui-menu')
        self.assertTrue('site-setup' not in browser.contents)
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Manager'])
        transaction.commit()
        browser.open('http://nohost/plone/empty-folder/cmsui-menu')
        self.assertTrue('site-setup' in browser.contents)
