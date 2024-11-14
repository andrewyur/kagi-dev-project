from lxml import html
import requests
from email.utils import formatdate
from time import mktime
from dateutil import parser
import nh3
from pydantic import BaseModel
from flask import request
from typing import List
import cssselect
from urllib.parse import urlparse


class RssData(BaseModel):
    homepage: str
    channel_title: str
    channel_description: str
    item_title: str
    item_link: str
    item_pubDate: str | None
    item_description: str | None


class RssChannel(BaseModel):
    title: str
    description: str
    link: str
    lastBuildDate: str | None
    pubDate: str | None


class RssItem(BaseModel):
    title: str
    link: str
    pubDate: str | None
    description: str | None


class RssFeed(BaseModel):
    channel: RssChannel
    items: List[RssItem]


def extract_form_data() -> RssData:
    form_keys = [
        "homepage",
        "channel_title",
        "channel_description",
        "item_title",
        "item_link",
        "item_pubDate",
        "item_description",
    ]

    rss_data = {k: request.form.get(k) for k in form_keys}
    for k, v in rss_data.items():
        if v == "":
            rss_data[k] = None

    # I want this to throw if the required form data is not passed in
    return RssData(
        homepage=rss_data["homepage"],  # type: ignore
        channel_title=rss_data["channel_title"],  # type: ignore
        channel_description=rss_data["channel_description"],  # type: ignore
        item_title=rss_data["item_title"],  # type: ignore
        item_link=rss_data["item_link"],  # type: ignore
        item_pubDate=rss_data["item_pubDate"],
        item_description=rss_data["item_description"],
    )


def create_rss_object(
    rss_data: RssData, input_document: html.HtmlElement | None = None, debug=False
) -> RssFeed | str:

    if debug:
        print(rss_data)

    rss_data_dump = rss_data.model_dump()

    # sanitize user input to protect against xss attacks
    for _, v in rss_data_dump.items():
        if isinstance(v, str) and nh3.is_html(v):
            return "Only text tags are allowed in the input!"

    document: html.HtmlElement
    if input_document is None:

        # might be better to forward the user-agent header from the route request
        response = requests.get(
            rss_data_dump["homepage"], headers={"user-agent": "andrew's rss converter"}
        )

        if not response.ok:
            return "There was an error fetching from the supplied webpage!"

        document: html.HtmlElement = html.document_fromstring(response.text)
    else:
        document = input_document

    item_attr_list = ["item_title", "item_link", "item_description", "item_pubDate"]

    try:
        html_items = {
            rss_attr: document.cssselect(rss_data_dump[rss_attr])
            for rss_attr in item_attr_list
            if rss_data_dump[rss_attr] is not None
        }
    except cssselect.SelectorSyntaxError:
        return "The rss creator was not given valid css selectors!"

    # filter out attributes whose css queries returned empty lists

    html_items = dict(filter(lambda kvp: len(kvp[1]) != 0, html_items.items()))
    item_attr_list = html_items.keys()

    if debug:
        print(html_items)

    # if the lengths of the attributes are not all the same length, we cannot be sure which corresponds to which
    lengths = [len(v) for v in html_items.values()]
    if len(set(lengths)) > 1:
        print(lengths)
        return "The css queries returned items that were not all the same length!"

    rss_to_html_attr = {
        "item_title": "textContent",
        "item_link": "href",
        "item_description": "textContent",
        "item_pubDate": "textContent",
    }

    def get_attr(el: html.HtmlElement, attr: str):
        return el.text_content() if attr == "textContent" else el.get(attr, "")

    def parse_rss_attr(attr, i):
        return get_attr(html_items[attr][i], rss_to_html_attr[attr])

    # RSS has its own special date format
    def format_date(x):
        return (
            None
            if x is None
            else formatdate(mktime(x.timetuple()), localtime=False, usegmt=True)
        )

    rss_items: List[RssItem] = []

    for i in range(len(html_items["item_title"])):
        rss_item = RssItem(
            title=parse_rss_attr("item_title", i),
            link=parse_rss_attr("item_link", i),
            description=(
                parse_rss_attr("item_description", i)
                if "item_description" in item_attr_list
                else None
            ),
            pubDate=(
                parse_rss_attr("item_pubDate", i)
                if "item_pubDate" in item_attr_list
                else None
            ),
        )

        rss_items.append(rss_item)

    if debug:
        print(rss_items)

    # format dates, get earliest and latest pubdates, and format links
    latest_date = None
    earliest_date = None
    for item in rss_items:

        if item.pubDate is not None:
            parsed_date = None
            try:
                parsed_date = parser.parse(item.pubDate)
            except Exception as e:
                print(e)
                return "There was an error parsing the date from the supplied element!"

            item.pubDate = format_date(parsed_date)

            if latest_date is None or latest_date < parsed_date:
                latest_date = parsed_date
            if earliest_date is None or earliest_date > parsed_date:
                earliest_date = parsed_date

        if not item.link.startswith("http"):
            parsed_uri = urlparse(rss_data_dump["homepage"])
            item.link = (
                f"{parsed_uri.scheme}://{parsed_uri.netloc}/{item.link.strip("/")}"
            )

    rss_channel = RssChannel(
        title=rss_data_dump["channel_title"],
        description=rss_data_dump["channel_description"],
        link=request.base_url,
        lastBuildDate=format_date(latest_date),
        pubDate=format_date(earliest_date),
    )

    if debug:
        print(rss_channel)

    return RssFeed(channel=rss_channel, items=rss_items)
