from flask import Blueprint
from lxml import html
from proxy.utils import check_request


proxy_bp = Blueprint("proxy", __name__)


@proxy_bp.route("/<path:proxy_url>")
def reflect(proxy_url):

    response = check_request(proxy_url)

    if isinstance(response, str):
        return response, 400

    document: html.HtmlElement = html.document_fromstring(response.text)

    # edits to the dom in the webpage's script tags can cause issues with the css queries
    for script in document.cssselect("script"):
        script.drop_tree()

    document.make_links_absolute(proxy_url)

    return html.tostring(document)
