============
Introduction
============

.. contents:: Contents

plone.app.cmsui installs a new content management user interface for Plone.
For the moment, it is an experiment only, but hopefully one that will point
the way towards Plone's future.

The main premise of plone.app.cmsui is to put all the content management
user interface elements into a separate package, with its own, isolated styles
and JavaScript files, injected into the page and displayed overlaying the
content page. The idea is that no matter how you theme your site, and what
you install, you should not be able to break the editing and administration
UI.

Installation
============

You can use the following buildout to test plone.app.cmsui against
Plone 4.1rc3 - update versions as applicable::

    [buildout]
    parts = instance
    extends =
        http://good-py.appspot.com/release/plone.app.cmsui/1.0a1?plone=4.1rc3
    
    [instance]
    recipe = plone.recipe.zope2instance
    user = admin:admin
    eggs =
        Plone
        plone.app.cmsui

Make sure you install the "CMS User Interface" profile when creating your
Plone site.

Using with Diazo
================

If you are using Diazo and plone.app.theming, you can enable the CMS UI in
your site by including the following rule::

    <before css:theme-children="body" css:content="#plone-cmsui-trigger" />

Theme and resource bundles
==========================

All CMS UI resources are loaded in a theme (in the portal_skins sense) called
'cmsui'. Using the concept of resource bundles (in Products.ResourceRegistries
2.1a1), resources are segregated between this theme and the theme (probably
'Sunburst Theme') used for the public site.

Participation and conventions
=============================

See http://projects-wiki.plone.org/display/NEWUI/Home for details about how
to participate, the rationale behind the project, and related information.
Log in with your plone.org username.

The following rules and conventions apply:

* No functionality should live in this package, only views and associated
  user interface logic.
* Dependencies on other packages should be minimised: With the exception
  of edit forms and the control panel, the goal is to move all the editing
  views into this package, so that they can be maintained consistently.
* There is a ``bbb`` subpackage that contains overrides and integration
  code required for this package to install on a clean Plone 4.1 site. In
  time, this package should be entirely removed and the changes propagated
  to the relevant parts of Plone, if and when this package is merged via the
  PLIP process.
