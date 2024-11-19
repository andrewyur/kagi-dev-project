from flask import Blueprint, render_template, request, redirect, flash
from urllib.parse import quote
from edit.utils import generate_rss_data
from rss.utils import create_rss_object, RssData
from db.utils import get_db_conn
import requests
import lxml.html as html
from asgiref.sync import sync_to_async


edit_bp = Blueprint("edit", __name__)


@edit_bp.route("/", methods=["GET"])
def edit_screen():
    return render_template("editor.html.jinja", generate_css_queries=True)


@edit_bp.route("/", methods=["POST"])
def edit_screen_with_data():
    print(request.form.to_dict().keys())

    return render_template("editor.html.jinja", input_data=request.form.to_dict())


@edit_bp.route("/gen")
async def initial_css_queries():

    url = request.args.get("url-input")

    if url is None:
        flash("Did not recieve a URL!")
        return redirect("/")

    response: requests.Response
    try:
        response = requests.get(url, headers={"user-agent": "andrew's rss converter"})
    except requests.RequestException:
        flash("Did not recieve a response from the URL!")
        return redirect("/")

    if not response.headers["Content-Type"].startswith("text/html"):
        flash("expected an html response from the given URL!")
        return redirect("/")

    document: html.HtmlElement = html.document_fromstring(response.text)

    # this needs to be defined and run in a synchronous context because of issues with flask's request object and sqlite3 driver

    def search_db():
        conn = get_db_conn()
        cursor = conn.cursor()

        db_response = cursor.execute("SELECT * FROM feeds WHERE homepage= ? ", (url,))

        return db_response.fetchone()

    db_fetch_response = await sync_to_async(search_db)()

    rss_data: RssData | str
    if db_fetch_response is not None:
        print("fetching from DB")
        rss_data = RssData(**db_fetch_response)
    else:
        print("calling LLM API")
        rss_data = await generate_rss_data(url, document)

    if isinstance(rss_data, str):
        flash(f"There was a problem generating the feed data: {rss_data}")
        return redirect(f"/edit?url-input={quote(url, safe='')}")

    rss_object = create_rss_object(
        rss_data, input_document=html.document_fromstring(response.text)
    )

    if isinstance(rss_object, str):
        flash(
            f"There was a problem creating the feed from the generated data: {rss_object}"
        )
        return redirect(f"/edit?url-input={quote(url, safe='')}")

    return render_template(
        "preview.html.jinja", **rss_object.model_dump(), preview_data=rss_data
    )
