""" block-related utils
"""


from .utils import find_block
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from urllib.parse import urlparse
from zope.component import adapter
from zope.component import subscribers
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest


# from plone.restapi.behaviors import IBlocks


@implementer(IBlockFieldSerializationTransformer)
@adapter(Interface, IBrowserRequest)
class ConnectedPlotlyChartSerializationTransformer(object):
    order = 1000
    block_type = 'connected_plotly_chart'

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block_value):
        if 'chartData' in block_value['chartData']:     # BBB
            del block_value['chartData']['chartData']
        print('serialization')
        print(block_value)
        block_value['chartData']['data'] = []
        if block_value['chartData'].get('provider_url'):
            url = block_value['chartData']['provider_url']
            block_value['chartData']['provider_url'] = urlparse(url).path
        return block_value


@implementer(IBlockFieldDeserializationTransformer)
@adapter(Interface, IBrowserRequest)
class ConnectedPlotyChartDeserializationTransformer(object):
    order = 100
    block_type = 'connected_plotly_chart'

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block_value):
        if not block_value['chartData'].get('data'):
            block = find_block(self.context.blocks, self.blockid)
            if block:
                block_value['chartData']['data'] = block['chartData'].get(
                    'data', [])

            # print('fixed blockvalue')
            # print(block_value)

        return block_value


@implementer(IBlockFieldSerializationTransformer)
@adapter(Interface, IBrowserRequest)
class ImageCardsSerializationTransformer(object):
    order = 1
    block_type = 'imagecards'

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def fix_links(self, card):
        card['attachedimage'] = urlparse(card['attachedimage']).path
        return card

    def __call__(self, block_value):
        if (block_value.get('cards')):
            block_value['cards'] = [
                self.fix_links(card) for card in block_value['cards']
            ]
        return block_value


class SubformsTransformer(object):
    order = -100      # this should to be executed as first as possible
    block_type = None
    iface = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _transform(self, blocks):
        for id, block_value in blocks.items():
            block_type = block_value.get("@type", "")
            handlers = []
            for h in subscribers(
                (self.context, self.request),
                self.iface
            ):
                if h.block_type == block_type or h.block_type is None:
                    h.blockid = id
                    handlers.append(h)

            for handler in sorted(handlers, key=lambda h: h.order):
                block_value = handler(block_value)

            blocks[id] = block_value

        return blocks

    def __call__(self, block_value):
        if not isinstance(block_value, dict):
            return block_value

        if 'data' in block_value:
            if isinstance(block_value['data'], dict):
                if 'blocks' in block_value['data']:
                    block_value['data']['blocks'] = self._transform(
                        block_value['data']['blocks']
                    )

        if 'blocks' in block_value:
            block_value['blocks'] = self._transform(block_value['blocks'])

        return block_value


@implementer(IBlockFieldSerializationTransformer)
@adapter(Interface, IBrowserRequest)
class SubformsSerializationTransformer(SubformsTransformer):
    iface = IBlockFieldSerializationTransformer


@implementer(IBlockFieldSerializationTransformer)
@adapter(Interface, IBrowserRequest)
class SubformsDeserializationTransformer(SubformsTransformer):
    iface = IBlockFieldDeserializationTransformer
