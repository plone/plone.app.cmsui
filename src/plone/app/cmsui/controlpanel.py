from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper

from plone.app.cmsui.interfaces import ICMSUISettings
from plone.z3cform import layout

class CMSUIPanelForm(RegistryEditForm):
    schema = ICMSUISettings

CMSUIControlPanelView = layout.wrap_form(CMSUIPanelForm, ControlPanelFormWrapper)
CMSUIControlPanelView.label = u"CMS User Interface settings"