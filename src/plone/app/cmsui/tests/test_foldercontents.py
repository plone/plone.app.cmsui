import unittest2 as unittest

import transaction
from plone.testing.z2 import Browser
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.cmsui.testing import CMSUI_FUNCTIONAL_TESTING
from plone.app.cmsui.testing import browser_login


class TestFolderContents(unittest.TestCase):

    layer = CMSUI_FUNCTIONAL_TESTING

    def setUp(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.invokeFactory('Folder', 'empty-folder', title=u"Folder 1")
        transaction.commit()
        
        self.portal = portal
        self.browser = Browser(self.layer['app'])
        

    def test_not_visible_to_anon(self):
        browser = Browser(self.layer['app'])
        browser.open('http://nohost/plone/cmsui-structure')
        self.assertTrue('Log in' in browser.contents)

    def test_bbb_view(self):
        browser_login(self.portal, self.browser)
        self.browser.open('http://nohost/plone/@@folder_contents')
        self.assertTrue('cmsui-folder-contents' in self.browser.contents)

    def test_table_headers_hidden_on_empty_folder(self):
        browser_login(self.portal, self.browser)
        
        # empty folder
        self.browser.open('http://nohost/plone/empty-folder/cmsui-structure')
        self.assertFalse('foldercontents-title-column' in self.browser.contents)

        # non-empty folder
        self.browser.open('http://nohost/plone/cmsui-structure')
        self.assertTrue('foldercontents-title-column' in self.browser.contents)

"""
    Buttons
    -------

    With the folder contents view it is possible to copy, paste etc. a lot
    of content objects at once.

    An empty folder should only contain the paste button.

      >>> self.createFolder('empty-folder')
      >>> browser.open('http://nohost/plone/empty-folder/@@folder_contents')

      >>> browser.getControl('Copy')
      Traceback (most recent call last):
      ...
      LookupError: label 'Copy'

      >>> browser.getControl('Cut')
      Traceback (most recent call last):
      ...
      LookupError: label 'Cut'

      >>> browser.getControl('Rename')
      Traceback (most recent call last):
      ...
      LookupError: label 'Rename'

      >>> browser.getControl('Delete')
      Traceback (most recent call last):
      ...
      LookupError: label 'Delete'

      >>> browser.getControl('Change State')
      Traceback (most recent call last):
      ...
      LookupError: label 'Change State'

    The paste button should not be there yet either. We only want to see
    that when we have something copied.

      >>> browser.getControl('Paste')
      Traceback (most recent call last):
      ...
      LookupError: label 'Paste'

    When we look at a folder with content in it we should see more
    options.

      >>> browser.open('http://nohost/plone/@@folder_contents')

      >>> button = browser.getControl('Copy')
      >>> button = browser.getControl('Cut')
      >>> button = browser.getControl('Rename')
      >>> button = browser.getControl('Delete')
      >>> button = browser.getControl('Change State')

    Still the paste button should not be available.

      >>> browser.getControl('Paste')
      Traceback (most recent call last):
      ...
      LookupError: label 'Paste'

    Now we shall copy something so we can paste it.

      >>> objects = browser.getControl(name='paths:list')
      >>> objects.value = objects.options[0:1]
      >>> browser.getControl('Copy').click()

    Because we have copied something the paste button should show up.

      >>> button = browser.getControl('Paste')

    It should also show up in our empty folder.

      >>> browser.open('http://nohost/plone/empty-folder/@@folder_contents')
      >>> button = browser.getControl('Paste')


    Batching
    --------

    Because we have no content there should not be any batching.

      >>> browser.open('http://nohost/plone/@@folder_contents')
      >>> browser.getLink('Next 20 items')
      Traceback (most recent call last):
      ...
      LinkNotFoundError

    Create a few pages so that we have some content to play with.

      >>> self.createDocuments(65)

      >>> browser.open('http://nohost/plone/@@folder_contents')
      >>> 'Testing' in browser.contents
      True

    Now that we have a lot of pages we should also have some batching.

      >>> browser.getLink('Next 20 items')
      <Link ...>

    One of the later pages should not be in our current screen.

      >>> 'Testing \xc3\xa4 20' in browser.contents
      False

    Now when we go to the second screen it should show up.

      >>> browser.getLink('2').click()
      >>> 'Testing \xc3\xa4 20' in browser.contents
      True

    We should also have at most four pages of batched items. So at page four there
    should be no way to go further.

      >>> browser.getLink('4').click()
      >>> browser.getLink('Next 20 items')
      Traceback (most recent call last):
      ...
      LinkNotFoundError

    The batching navigation also should allow us to go back to previous pages.

      >>> browser.getLink('Previous 20 items')
      <Link ...>

    When we are at the first page this link should not be shown.

      >>> browser.open('http://nohost/plone/@@folder_contents')
      >>> browser.getLink('Previous 20 items')
      Traceback (most recent call last):
      ...
      LinkNotFoundError

    Selection
    ---------

    The folder contents view supports quite elaborate selection techniques. You can
    select items individually or group wise. We will now demonstrate how the group
    wise selection works.

      >>> browser.open('http://nohost/plone/@@folder_contents')

    First we can select all items on screen.

      >>> browser.getLink(id='foldercontents-selectall').click()

    This will show a message that only the items on the screen are selected.

      >>> print browser.contents
      <BLANKLINE>
      ... All 20 items on this page are selected...

    We now have a way to select all items in the batch.

      >>> browser.getLink(id='foldercontents-selectall-completebatch').click()

    This should have selected everything.

      >>> print browser.contents
      <BLANKLINE>
      ... All ... items in this folder are selected. ...

    We can also clear the selection, this will deselect everything.

      >>> browser.getLink(id='foldercontents-clearselection').click()

    Now we are back to square one and we can select all items on the screen again.

      >>> browser.getLink(id='foldercontents-selectall')
      <Link ...>

    The steps described are bit different for when we only have a few items. First
    we clean up all items by removing everything.

      >>> browser.getLink(id='foldercontents-selectall').click()
      >>> browser.getLink(id='foldercontents-selectall-completebatch').click()
      >>> browser.getControl(name='folder_delete:method').click()

    Notice that is no way to select any items now. This is because there
    is nothing to select.

      >>> browser.getLink(id='foldercontents-selectall')
      Traceback (most recent call last):
      ...
      LinkNotFoundError

    Now we will add some documents again.

      >>> self.createDocuments(3)

    When we press the select all button it should no longer offer us to select the
    whole batch because we are showing everything already.

      >>> browser.open('http://nohost/plone/@@folder_contents')
      >>> browser.getLink(id='foldercontents-selectall').click()
      >>> print browser.contents
      <BLANKLINE>
      ... All ... items in this folder are selected...

      >>> browser.getLink(id='foldercontents-selectall-completebatch')
      Traceback (most recent call last):
      ...
      LinkNotFoundError

    Instead we should now be able to clear the selection.

      >>> browser.getLink(id='foldercontents-clearselection')
      <Link ...>


    Going up
    --------

    When you are looking at the contents of a folder you might want to
    navigate to a different folder. This can be done by going to the
    parent folder.

    To show this we will need to create a folder first.

      >>> self.createFolder()

    Now we can go to this folder.

      >>> browser.open('http://nohost/plone/new-folder/@@folder_contents')

    In this folder contents view we should have link to go to the site root.

      >>> browser.getLink('Up one level')
      <Link ...>

    Now lets click it.

      >>> browser.getLink('Up one level').click()
      >>> browser.url
      'http://nohost/plone/folder_contents'

    In the site root we should not be able to go up any further.

      >>> browser.getLink('Up one level')
      Traceback (most recent call last):
      ...
      LinkNotFoundError


    Expanding the batch
    -------------------

    Sometimes you might want to see all the items in the folder. To make
    this possible you can ask the folder contents to show everything
    without enabling batching.

    Before we demonstrate we need to clear out the existing contents and
    create some new content.

      >>> browser.getLink(id='foldercontents-selectall').click()
      >>> browser.getControl(name='folder_delete:method').click()

    Putting only one page into the folder will not show the option to
    disable batching since there is no batching.

      >>> self.createDocuments(1)
      >>> browser.open('http://nohost/plone/@@folder_contents')
      >>> browser.getLink('Show all items')
      Traceback (most recent call last):
      ...
      LinkNotFoundError

    Create some more pages to show the batch disabling feature.

      >>> browser.open('http://nohost/plone/@@folder_contents')
      >>> browser.getLink(id='foldercontents-selectall').click()
      >>> browser.getControl(name='folder_delete:method').click()
      >>> self.createDocuments(60)

    Now we can show all the items in the folder if we want to.

      >>> browser.open('http://nohost/plone/@@folder_contents')
      >>> browser.getLink('Show all items').click()

    You can see all the items are now on the page.

      >>> browser.contents
      '...Testing \xc3\xa4 1...Testing \xc3\xa4 11...Testing \xc3\xa4 60...'

    Selecting the current page should make the entire folder selected
    (since we see everything).

      >>> browser.getLink(id='foldercontents-selectall').click()
      >>> print browser.contents
      <BLANKLINE>
      ... All ... items in this folder are selected. ...

"""