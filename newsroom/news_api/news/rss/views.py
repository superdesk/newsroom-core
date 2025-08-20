import superdesk
import flask
from lxml import etree
from lxml.etree import SubElement

from superdesk.utc import utcnow
from superdesk.core import get_app_config
from superdesk.core.web import EndpointGroup
from superdesk.core.types import Request, BaseModel
from superdesk.flask import url_for

from newsroom.core import get_current_wsgi_app
from newsroom.news_api.news.search_service import NewsApiSearchServiceAsync
from newsroom.types import SectionEnum
from newsroom.news_api.utils import update_embed_urls
from newsroom.wire.formatters.utils import remove_unpermissioned_embeds

from email import utils
import datetime
import logging

logger = logging.getLogger(__name__)
rss_endpoints = EndpointGroup("rss", __name__)


class RSSArgs(BaseModel):
    token: str | None = None


@rss_endpoints.endpoint("rss/<path:token>", methods=["GET"], auth=False)
async def get_rss_token(args: RSSArgs, params: None, request: Request):
    return await get_rss(args, params, request)


@rss_endpoints.endpoint("rss", methods=["GET"], auth=False)
async def get_rss_authed(args: RSSArgs, params: None, request: Request):
    return await get_rss(args, params, request)


logger = logging.getLogger(__name__)


async def get_rss(args: RSSArgs, params: None, request: Request):
    def _format_date(date):
        iso8601 = date.isoformat()
        if date.tzinfo:
            return iso8601
        return iso8601 + "Z"

    def _format_date_2(date):
        DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
        return date.strftime(DATETIME_FORMAT) + "Z"

    def _format_date_3(date):
        return utils.format_datetime(date)

    auth = get_current_wsgi_app().auth
    if not auth.authorized([], None, request.method):
        if args.token:
            if not auth.check_auth(args.token, allowed_roles=None, resource=None, method="GET"):
                return auth.authenticate()
        else:
            return auth.authenticate()

    XML_ROOT = '<?xml version="1.0" encoding="UTF-8"?>'

    _message_nsmap = {
        "dcterms": "http://purl.org/dc/terms/",
        "media": "http://search.yahoo.com/mrss/",
        "dc": "http://purl.org/dc/elements/1.1/",
        "mi": "http://schemas.ingestion.microsoft.com/common/",
        "content": "http://purl.org/rss/1.0/modules/content/",
    }

    site_name = get_app_config("SITE_NAME")
    #    feed = etree.Element('feed', attrib={'lang': 'en-us'}, nsmap=_message_nsmap)
    feed = etree.Element("rss", attrib={"version": "2.0"}, nsmap=_message_nsmap)
    channel = SubElement(feed, "channel")
    SubElement(channel, "title").text = "{} RSS Feed".format(site_name)
    SubElement(channel, "description").text = "{} RSS Feed".format(site_name)
    SubElement(channel, "link").text = url_for("rss.get_rss_authed", _external=True)

    response = await NewsApiSearchServiceAsync().process_web_request(request)

    for item in response.body.get("_items"):
        try:
            complete_item = superdesk.get_resource_service("items").find_one(req=None, _id=item.get("_id"))
            if not complete_item:
                continue

            await remove_unpermissioned_embeds(complete_item, SectionEnum.NEWS_API)

            entry = SubElement(channel, "item")

            # If the item has any parents we use the id of the first, this should be constant throught the update
            # history
            if complete_item.get("ancestors") and len(complete_item.get("ancestors")):
                SubElement(entry, "guid").text = complete_item.get("ancestors")[0]
            else:
                SubElement(entry, "guid").text = complete_item.get("_id")

            SubElement(entry, "title").text = etree.CDATA(complete_item.get("headline"))
            SubElement(entry, "pubDate").text = _format_date_3(complete_item.get("firstpublished"))
            SubElement(entry, etree.QName(_message_nsmap.get("dcterms"), "modified")).text = _format_date_2(
                complete_item.get("versioncreated")
            )
            url_kwargs = {
                "item_id": item.get("_id"),
                "format": "TextFormatter",
                "_external": True,
            }

            # Conditionally add the 'token' to url_kwargs
            if args.token:
                url_kwargs["token"] = args.token

            # Create the SubElement with the dynamically generated href
            SubElement(
                entry,
                "link",
                attrib={
                    "rel": "self",
                    "href": url_for("news/item.get_item", **url_kwargs),
                },
            )

            if complete_item.get("byline"):
                name = complete_item.get("byline")
                if (
                    complete_item.get("source")
                    and not get_app_config("COPYRIGHT_HOLDER", "").lower() == complete_item.get("source", "").lower()
                ):
                    name = name + " - " + complete_item.get("source")
                SubElement(entry, etree.QName(_message_nsmap.get("dc"), "creator")).text = name
            else:
                SubElement(entry, etree.QName(_message_nsmap.get("dc"), "creator")).text = (
                    complete_item.get("source")
                    if complete_item.get("source")
                    else get_app_config("COPYRIGHT_HOLDER", "")
                )

            SubElement(
                entry, "source", attrib={"url": url_for("rss.get_rss_authed", _external=True)}
            ).text = complete_item.get("source", "")

            if complete_item.get("pubstatus") == "usable":
                SubElement(
                    entry, etree.QName(_message_nsmap.get("dcterms"), "valid")
                ).text = "start={}; end={}; scheme=W3C-DTF".format(
                    _format_date(utcnow()), _format_date(utcnow() + datetime.timedelta(days=30))
                )
            else:
                # in effect a kill set the end date into the past
                SubElement(
                    entry, etree.QName(_message_nsmap.get("dcterms"), "valid")
                ).text = "start={}; end={}; scheme=W3C-DTF".format(
                    _format_date(utcnow()), _format_date(utcnow() - datetime.timedelta(days=30))
                )

            categories = (
                [{"name": s.get("name")} for s in complete_item.get("service", [])]
                + [{"name": s.get("name")} for s in complete_item.get("subject", [])]
                + [{"name": s.get("name")} for s in complete_item.get("place", [])]
                + [{"name": k} for k in complete_item.get("keywords", [])]
            )
            for category in categories:
                SubElement(entry, "category").text = category.get("name")

            SubElement(entry, "description").text = etree.CDATA(complete_item.get("description_text", ""))

            update_embed_urls(complete_item, args.token)

            SubElement(entry, etree.QName(_message_nsmap.get("content"), "encoded")).text = etree.CDATA(
                complete_item.get("body_html", "")
            )

            if ((complete_item.get("associations") or {}).get("featuremedia") or {}).get("renditions"):
                image = (
                    ((complete_item.get("associations") or {}).get("featuremedia") or {}).get("renditions").get("16-9")  # type: ignore
                )
                metadata = (complete_item.get("associations") or {}).get("featuremedia") or {}

                url = (
                    url_for("assets.get_item", _external=True, asset_id=image.get("media"), token=args.token)
                    if args.token
                    else url_for("assets.get_item", _external=True, asset_id=image.get("media"))
                )

                media = SubElement(
                    entry,
                    etree.QName(_message_nsmap.get("media"), "content"),
                    attrib={"url": url, "type": image.get("mimetype"), "medium": "image"},
                )

                SubElement(media, etree.QName(_message_nsmap.get("media"), "credit")).text = metadata.get("byline")
                SubElement(media, etree.QName(_message_nsmap.get("media"), "title")).text = metadata.get(
                    "description_text"
                )
                SubElement(media, etree.QName(_message_nsmap.get("media"), "text")).text = metadata.get("body_text")
                if image.get("poi"):
                    focr = SubElement(media, etree.QName(_message_nsmap.get("mi"), "focalRegion"))
                    SubElement(focr, etree.QName(_message_nsmap.get("mi"), "x1")).text = str(image.get("poi").get("x"))
                    SubElement(focr, etree.QName(_message_nsmap.get("mi"), "x2")).text = str(image.get("poi").get("x"))
                    SubElement(focr, etree.QName(_message_nsmap.get("mi"), "y1")).text = str(image.get("poi").get("y"))
                    SubElement(focr, etree.QName(_message_nsmap.get("mi"), "y2")).text = str(image.get("poi").get("y"))
        except Exception as ex:
            logger.exception("processing {} - {}".format(item.get("_id"), ex))

    return flask.Response(
        XML_ROOT + etree.tostring(feed, method="xml", pretty_print=True).decode("utf-8"), mimetype="application/rss+xml"
    )
