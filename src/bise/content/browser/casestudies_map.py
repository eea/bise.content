""" Case studies json  """

import json
import logging

from plone.api.portal import get_tool
from Products.Five import BrowserView
# from zope.component import getUtility
# from zope.schema.interfaces import IVocabularyFactory

# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

logger = logging.getLogger("bise.content")


class Items(BrowserView):
    """ Items"""

    def __call__(self):
        """"""
        results = {
            "type": "FeatureCollection",
            "metadata": {
                "generated": 1615559750000,
                "url": "https://earthquake.usgs.gov/earthquakes"
                    "/feed/v1.0/summary/all_month.geojson",
                "title": "BISE NRR Case Studies",
                "status": 200,
                "api": "1.10.3",
                "count": 10739,
            },
            "features": [],
        }

        catalog = get_tool("portal_catalog")
        brains = catalog.searchResults(
            {
                "portal_type": [
                    "nrr_case_study",
                ],
                # "path": "/",
                # "review_state": "published",
            }
        )
        for brain in brains:
            obj = brain.getObject()
            if not hasattr(obj, "geolocation") and obj.geolocation is not None:
                continue

            results["features"].append(
                {
                    "properties": {
                        "portal_type": obj.portal_type,
                        "title": obj.title,
                        "description": 'long_description',
                        "url": brain.getURL(),
                        "path": "/".join(
                            obj.getPhysicalPath()).replace('/Plone', ''),
                        "image": "",
                    },
                    "geometry": {
                        "type": "Point",
                        "svg": {"fill_color": "#009900"},
                        "color": "#009900",
                        "coordinates": [
                            # "6.0142918",
                            # "49.5057481"
                            obj.geolocation.longitude,
                            obj.geolocation.latitude,
                        ],
                    },
                }
            )

        response = self.request.response
        response.setHeader("Content-type", "application/json")

        return json.dumps(results)
