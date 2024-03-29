# -*- coding: utf-8 -*-
"""Installer for the bise.content package."""

from os.path import join
from setuptools import setup, find_packages

NAME = 'bise.content'
PATH = ['src'] + NAME.split('.') + ['version.txt']
VERSION = open(join(*PATH)).read().strip()


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name=NAME,
    version=VERSION,
    description="Bise Content and Site Policy",
    long_description_content_type="text/x-rst",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.1",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone Bise BiseContent',
    author='European Environment Agency: IDM2 A-Team',
    author_email='eea-edw-a-team-alerts@googlegroups.com',
    url='https://github.com/eea/bise.content',
    project_urls={
        'PyPI': 'https://pypi.python.org/pypi/bise.content',
        'Source': 'https://github.com/collective/bise.content',
        'Tracker': 'https://github.com/collective/bise.content/issues',
        # 'Documentation': 'https://bise.content.readthedocs.io/en/latest/',
    },
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['bise'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'z3c.jbot',
        'plone.api>=1.8.4',
        'plone.restapi',
        'plone.app.dexterity',
        'eea.restapi',
        'pas.plugins.ldap',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            'plone.testing>=5.0.0',
            'plone.app.contenttypes',
            'plone.app.robotframework[debug]',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = bise.content.locales.update:update_locale
    """,
)
