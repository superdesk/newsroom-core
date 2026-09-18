from pydantic import BaseModel
from datetime import datetime, timedelta

from superdesk.flask import url_for, render_template
from superdesk.core.web import EndpointGroup
from superdesk.core.types import Request
from superdesk.core.module import Module

blueprint = EndpointGroup("design", __name__)


class RouteArguments(BaseModel):
    page: str | None = None


@blueprint.endpoint("/design/detail", auth=False)
async def detail():
    item = {
        "headline": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
        "slugline": "Slugline",
        "type": "text",
        "byline": "Author byline",
        "versioncreated": datetime.utcnow(),
        "description_html": "<p>IN this exclusive interview, Aussie rock legend Jimmy Barnes reveals how he almost paid the ultimate price for his years of hard living.</p>",  # noqa
        "body_html": "<p>IT may have been the sleeping tablets. On top of the emptied minibar. On top of the cocaine, ecstasy and ketamine Jimmy Barnes had ingested to escape his demons. But the morning after the night before, when the rocker saw the dressing gown belt tied around a wardrobe rail in the ensuite of his Auckland hotel room, he was confronted with the reality he had attempted suicide. As he reveals in Working Class Man, the sequel to his best-selling Working Class Boy memoir, he had no recollection of getting out of bed and trying to take his life on that night in 2012. Confronting the evidence and confessing to wife Jane made him change his life forever, so he could keep living.</p>",  # noqa
        "genre": [{"name": "Article (news)"}],
        "subject": [{"name": "International News"}, {"name": "Politics"}],
        "associations": {
            "featuremedia": {
                "description_text": "Lorem ipsum etc.",
                "renditions": {"baseImage": {"href": url_for("static", filename="article_preview.png")}},
            },
        },
    }
    previous_versions = [
        {
            "_id": "foo",
            "headline": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
            "versioncreated": datetime.utcnow() - timedelta(minutes=8),
            "body_html": "<p>foo bar</p>",
        },
        {
            "_id": "bar",
            "headline": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
            "versioncreated": datetime.utcnow() - timedelta(hours=3, minutes=5),
            "body_html": "<p>foo bar</p>",
        },
    ]
    return await render_template("wire_item.html", item=item, previous_versions=previous_versions)


@blueprint.endpoint("/design/", auth=False)
async def index():
    return await render_template("design_index.html")


@blueprint.endpoint("/design/<string:page>", auth=False)
async def page(args: RouteArguments, params: None, req: Request):
    return await render_template(f"design_{args.page}.html")


module = Module(name="newsroom.design", endpoints=[blueprint])
