from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import applyProfile

from zope.configuration import xmlconfig
from plone.app.testing.layers import IntegrationTesting
from plone.app.testing.layers import FunctionalTesting

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
