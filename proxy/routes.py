from flask import Blueprint, render_template
import requests
from lxml import html


proxy_bp = Blueprint("proxy", __name__)


@proxy_bp.route("/<path:proxy_url>")
def reflect(proxy_url):

    try:
        response = requests.get(
            proxy_url, headers={"user-agent": "andrew's rss converter"}
        )
    except requests.RequestException:
        return (
            render_template("error.html.jinja", message="Invalid URL supplied!"),
            400,
        )

    if not response.ok:
        print(response.status_code)
        return (
            render_template(
                "error.html.jinja", message="The webpage could not be loaded!"
            ),
            400,
        )

    # this is only for the initial html page, not anything else
    if not response.headers["Content-Type"] == "text/html; charset=utf-8":
        return (
            render_template("error.html.jinja", message="Expected an html response!"),
            400,
        )

    document: html.HtmlElement = html.document_fromstring(response.text)

    # edits to the dom in the webpage's script tags can cause issues with the css queries
    for script in document.cssselect("script"):
        script.drop_tree()

    document.make_links_absolute(proxy_url)

    return html.tostring(document)
