# -*- coding: utf-8 -*-
"""Init and utils."""
from plone.restapi import batching
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('bise.content')


batching.DEFAULT_BATCH_SIZE = 1000
