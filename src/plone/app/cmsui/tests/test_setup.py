import unittest2 as unittest

from plone.app.cmsui.testing import CMSUI_INTEGRATION_TESTING

class TestSetup(unittest.TestCase):

    layer = CMSUI_INTEGRATION_TESTING

    def test_records_installed(self):
        from zope.component import getUtility
        from plone.app.cmsui.interfaces import ICMSUISettings
        from plone.registry.interfaces import IRegistry
        
        registry = getUtility(IRegistry)
        
        # This will throw an exception if not installed
        try:
            registry.forInterface(ICMSUISettings)
        except:
            self.fail("Unable to load records")

