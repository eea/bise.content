# -*- coding: utf-8 -*-

""" plone.restapi extensions and endpoints
"""

from bise.content.interfaces import IBiseFactsheetDatabase
from collections import deque
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse

import json
import logging


# from plone.restapi.services import Service
# from zope.component import queryMultiAdapter

logger = logging.getLogger('bise.content')


@implementer(IExpandableElement)
@adapter(IBiseFactsheetDatabase, Interface)
class FactsheetDatabaseListing(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        # we ignore expand here, because of specific interface
        result = {}
        batch = api.content.find(context=self.context,
                                 portal_type="bise_factsheet_section",
                                 sort_on="getObjPositionInParent",
                                 sort_order="ascending",
                                 )
        items = [
            getMultiAdapter((brain.getObject(), self.request),
                            ISerializeToJson)()

            for brain in batch
        ]

        result["factsheet-database-listing"] = items

        return result


# class FactsheetDatabaseListing(Service):
#     def reply(self):
#         data = ConnectorData(self.context, self.request)
#
#         return data(expand=True)["connector-data"]


@implementer(IPublishTraverse)
class BlockData(Service):
    """Returns raw, unprocessed data for blocks"""

    blockid = None

    def publishTraverse(self, request, blockid):
        self.blockid = blockid
        return self

    def reply(self):
        if self.blockid:
            return self.reply_block()

        blocks = self.context.blocks

        if isinstance(blocks, str):
            try:
                blocks = json.loads(blocks)
            except:
                logger.exception("Invalid json in blocks %s",
                                 self.context.absolute_url())
                blocks = {}

        return {
            '@id': '{}/@blocks'.format(self.context.absolute_url()),
            'items': [
                [blockid, blocks[blockid]] for blockid in
                (self.context.blocks_layout.items or [])
            ]
        }

    def _subforms(self, value):
        if not value:
            return []

        if 'data' in value:
            return self._subforms(value['data'])

        if 'blocks' in value:
            return value['blocks'].items()

        return []

    def find_block(self, blocks, searchid):
        """ Crawls tree of blocks (with columns, subblocks) to find a block
        """
        if searchid in blocks:
            return blocks[searchid]

        initial = blocks.items()
        stack = deque(initial)
        while stack:
            blockid, value = stack.pop()
            if blockid == searchid:
                return value

            children = self._subforms(value)
            stack.extend(children)

    def reply_block(self):
        blocks = self.context.blocks
        if isinstance(blocks, str):
            try:
                blocks = json.loads(blocks)
            except:
                logger.exception("Invalid json in blocks %s",
                                 self.context.absolute_url())
                blocks = {}

        data = self.find_block(blocks, self.blockid) or {}

        return {
            '@id': '{}/@blocks/{}'.format(self.context.absolute_url(),
                                          self.blockid),
            'data': data
        }
