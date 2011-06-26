from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='plone.app.cmsui',
      version=version,
      description="CMS user interface for Plone",
      long_description=open("README.txt").read() + "\n\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone ui',
      author='Plone developers',
      author_email='',
      url='http://pypi.python.org/pypi/plone.app.cmsui',
      license='GPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.registry',
          'Products.CMFPlone',
          'plone.namedfile[blobs]',
          'plone.formwidget.namedfile',
          'collective.quickupload',
      ],
      extras_require={
        'test': ['plone.app.testing'],
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
