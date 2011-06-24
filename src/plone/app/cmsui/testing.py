from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import applyProfile
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting
from zope.configuration import xmlconfig

class CMSUI(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # load ZCML
        import plone.app.cmsui
        xmlconfig.file('configure.zcml', plone.app.cmsui, context=configurationContext)

    def setUpPloneSite(self, portal):
        # install into the Plone site
        applyProfile(portal, 'plone.app.cmsui:default')

CMSUI_FIXTURE = CMSUI()
CMSUI_INTEGRATION_TESTING = IntegrationTesting(bases=(CMSUI_FIXTURE,), name="CMSUI:Integration")
CMSUI_FUNCTIONAL_TESTING = FunctionalTesting(bases=(CMSUI_FIXTURE,), name="CMSUI:Functional")

def browser_login(portal, browser, username=None, password=None):
    browser.open(portal.absolute_url() + '/login_form')
    if username is None:
        username = TEST_USER_NAME
    if password is None:
        password = TEST_USER_PASSWORD
    browser.getControl(name='__ac_name').value = username
    browser.getControl(name='__ac_password').value = password
    browser.getControl(name='submit').click()
