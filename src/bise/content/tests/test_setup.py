# -*- coding: utf-8 -*-
"""Setup tests for this package."""
import unittest

from bise.content.testing import BISE_CONTENT_INTEGRATION_TESTING  # noqa: E501
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that bise.content is properly installed."""

    layer = BISE_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if bise.content is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'bise.content'))

    def test_browserlayer(self):
        """Test that IBiseContentLayer is registered."""
        from bise.content.interfaces import (
            IBiseContentLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IBiseContentLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = BISE_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['bise.content'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if bise.content is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'bise.content'))

    def test_browserlayer_removed(self):
        """Test that IBiseContentLayer is removed."""
        from bise.content.interfaces import \
            IBiseContentLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            IBiseContentLayer,
            utils.registered_layers())
