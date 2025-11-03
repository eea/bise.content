"""Upgrade to version 1001"""

from Products.CMFCore.utils import getToolByName


def migrate_composite_page(context):
    """Fix Indicator schema"""
    ctool = getToolByName(context, "portal_catalog")
    portal_type = "CompositePage"
    brains = ctool.unrestrictedSearchResults(portal_type=portal_type)

    for brain in brains:
        doc = brain.getObject()
        setattr(doc, "portal_type", "Document")
        doc.reindexObject()
