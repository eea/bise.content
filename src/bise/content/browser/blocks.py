""" block-related utils
"""


from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from urllib.parse import urlparse
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class ConnectedPlotlyChartSerializationTransformer(object):
    order = -1
    block_type = 'connected_plotly_chart'

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block_value):
        block_value['chartData']['data'] = []
        return block_value


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class ImageCardsSerializationTransformer(object):
    order = -1
    block_type = 'imagecards'

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def fix_links(self, card):
        card['attachedimage'] = urlparse(card['attachedimage']).path
        return card

    def __call__(self, block_value):
        import pdb
        pdb.set_trace()
        if (block_value.get('cards')):
            block_value['cards'] = [
                self.fix_links(card) for card in block_value['cards']
            ]
        return block_value
