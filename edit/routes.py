from flask import Blueprint, render_template, request, redirect, flash
from urllib.parse import quote
from edit.utils import generate_rss_data
from rss.utils import create_rss_object
import requests
import lxml.html as html


edit_bp = Blueprint("edit", __name__)


@edit_bp.route("/", methods=["GET"])
def edit_screen():
    return render_template("editor.html.jinja", generate_css_queries=True)


@edit_bp.route("/", methods=["POST"])
def edit_screen_with_data():
    return render_template("editor.html.jinja", input_data=request.form.to_dict())


@edit_bp.route("/gen")
async def initial_css_queries():

    url = request.args.get("url-input")

    if url is None:
        flash("Did not recieve a URL!")
        return redirect("/")

    try:
        response = requests.get(url, headers={"user-agent": "andrew's rss converter"})
    except Exception:
        flash("Recieved a malformed URL!")
        return redirect("/")

    if not response.headers["Content-Type"].startswith("text/html"):
        flash("expected an html response from the given URL!")
        return redirect("/")

    document: html.HtmlElement = html.document_fromstring(response.text)

    rss_data = await generate_rss_data(url, document)

    if isinstance(rss_data, str):
        flash(f"There was a problem generating the feed data: {rss_data}")
        return redirect(f"/edit?url-input={quote(url, safe='')}")

    rss_object = create_rss_object(
        rss_data, input_document=html.document_fromstring(response.text), debug=True
    )

    if isinstance(rss_object, str):
        flash(
            f"There was a problem creating the feed from the generated data: {rss_object}"
        )
        return redirect(f"/edit?url-input={quote(url, safe='')}")

    return render_template(
        "preview.html.jinja", **rss_object.model_dump(), preview_data=rss_data
    )
