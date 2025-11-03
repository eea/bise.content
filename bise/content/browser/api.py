# -*- coding: utf-8 -*-

"""plone.restapi extensions and endpoints"""

import json
import logging

from urllib.parse import urlparse
from bise.content.interfaces import IBiseFactsheetDatabase
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.blocks import uid_to_url
from plone.restapi.services import Service
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse
from .utils import find_block

# from plone.restapi.services import Service
# from zope.component import queryMultiAdapter

logger = logging.getLogger("bise.content")


@implementer(IExpandableElement)
@adapter(IBiseFactsheetDatabase, Interface)
class FactsheetDatabaseListing(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        # we ignore expand here, because of specific interface
        result = {}
        batch = api.content.find(
            context=self.context,
            portal_type="bise_factsheet_section",
            sort_on="getObjPositionInParent",
            sort_order="ascending",
        )
        items = [
            getMultiAdapter((brain.getObject(), self.request), ISerializeToJson)()
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

    def url_to_path(self, url):
        # portal_url = api.portal.get().absolute_url()
        path = urlparse(url).path.replace("/@@download/file", "")
        bits = list(filter(None, path.split("/")))
        if bits[0] == "bise" or bits[0] == "api":
            bits = bits[1:]
        return "/" + "/".join(bits)
        # path = portal_url + '/' + '/'.join(bits)
        # return path

    def transform(self, blockid, value):
        for field in ["url", "href"]:
            if field in value.keys():
                value[field] = self.url_to_path(uid_to_url(value.get(field, "")))
        if value.get("chartData", {}).get("provider_url"):
            value["chartData"]["provider_url"] = self.url_to_path(
                value["chartData"]["provider_url"]
            )
        return value

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
                logger.exception(
                    "Invalid json in blocks %s", self.context.absolute_url()
                )
                blocks = {}

        return {
            "@id": "{}/@blocks".format(self.context.absolute_url()),
            "items": [
                [blockid, self.transform(blockid, blocks[blockid])]
                for blockid in (self.context.blocks_layout.items or [])
            ],
        }

    def reply_block(self):
        blocks = self.context.blocks
        if isinstance(blocks, str):
            try:
                blocks = json.loads(blocks)
            except:
                logger.exception(
                    "Invalid json in blocks %s", self.context.absolute_url()
                )
                blocks = {}

        data = find_block(blocks, self.blockid) or {}

        return {
            "@id": "{}/@blocks/{}".format(self.context.absolute_url(), self.blockid),
            "data": self.transform(self.blockid, data),
        }
