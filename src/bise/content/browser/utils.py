from collections import deque


def _subforms(value):
    if not value:
        return []

    if 'data' in value:
        return _subforms(value['data'])

    if 'blocks' in value:
        return value['blocks'].items()

    return []


def find_block(blocks, searchid):
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

        children = _subforms(value)
        stack.extend(children)
