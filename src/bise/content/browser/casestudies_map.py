""" Case studies json  """

import json
import logging
import re

from plone.api.portal import get_tool
from Products.Five import BrowserView
# from zope.component import getUtility
# from zope.schema.interfaces import IVocabularyFactory

# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

logger = logging.getLogger("bise.content")

# Typology choices are stored as "NRPM_001 - MA01 - <measure name>".
TYPOLOGY_LABEL_RE = re.compile(r"^([A-Za-z]+)")


def parse_typology_entry(value):
    """Split a typology choice label into its structured parts.

    Choices are stored as "NRPM_001 - MA01 - Prevent conversion of ...".
    Returns the NRPM code, the measure family (the MA/MB/... prefix) and
    the measure name. Labels that don't follow the pattern are returned
    whole, as their own title, with an empty family.
    """
    label = str(value).strip()
    parts = [part.strip() for part in label.split(" - ", 2)]

    if len(parts) < 2 or not (parts[0] and parts[1]):
        return {"code": label, "family": "", "title": label}

    code, measure_code = parts[0], parts[1]
    title = parts[2] if len(parts) == 3 and parts[2] else label
    family = TYPOLOGY_LABEL_RE.match(measure_code)

    return {
        "code": code,
        "family": family.group(1) if family else "",
        "title": title,
    }


def get_effective_date(obj):
    """Return the publication date as ISO 8601, falling back to creation.

    Unpublished content usually has no effective date yet, so the creation
    date is used instead. Note that ``created`` is a method on CMF objects
    (it returns a DateTime), hence the callable handling.
    """
    date = getattr(obj, "effective_date", None)
    if callable(date):
        date = date()

    if date is None:
        date = getattr(obj, "created", None)
        if callable(date):
            date = date()

    if date is None:
        return None

    isoformat = getattr(date, "ISO8601", None)

    return isoformat() if isoformat is not None else date.isoformat()


def get_preview_image_url(obj, scale="preview"):
    """Return an absolute URL for the object's preview image.

    Falls back to the unscaled image when the requested scale is not
    available (for example when the original is smaller than the scale).
    """
    if not getattr(obj, "preview_image", None):
        return ""

    images = obj.restrictedTraverse("@@images")
    image_scale = images.scale("preview_image", scale=scale)
    if image_scale is not None:
        return image_scale.absolute_url()

    return "{}/@@images/preview_image".format(obj.absolute_url())


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
            if getattr(obj, "geolocation", None) is None:
                continue

            measures = []

            if obj.nrr_measures_implemented:
                measures = [
                    {"id": measure.to_id,
                     "title": measure.to_object.title,
                     "path": measure.to_path.replace("/bise", "")}
                    for measure in obj.nrr_measures_implemented
                ]

            typology_of_measures = []
            typology = []

            if obj.nrr_typology_of_measures:
                typology_of_measures = [
                    str(tom)
                    for tom in obj.nrr_typology_of_measures
                ]
                typology = [
                    parse_typology_entry(tom)
                    for tom in typology_of_measures
                ]

            results["features"].append(
                {
                    "properties": {
                        "portal_type": obj.portal_type,
                        "title": obj.title,
                        "description": obj.description,
                        "url": brain.getURL(),
                        "path": "/".join(
                            obj.getPhysicalPath()).replace('/bise', ''),
                        "image": get_preview_image_url(obj),
                        "measures": measures,
                        "typology_of_measures": typology_of_measures,
                        "typology": typology,
                        "effective": get_effective_date(obj),
                        "current_status": obj.nrr_current_status,
                        "habitat_ecosystem_type": list(
                            obj.nrr_habitat_ecosystem_type or []
                        ),
                        "nrr_legislation": list(obj.nrr_legislation or []),
                        "nrr_biogeographical_region": list(
                            obj.nrr_biogeographical_region or []),
                        "scale_of_planning": list(
                            obj.nrr_scale_of_planning or []
                        ),
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
