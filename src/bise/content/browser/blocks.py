""" block-related utils
"""


from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
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
