from flask import Blueprint, render_template, make_response, redirect
from db.utils import get_db_conn
import nanoid
from rss.utils import create_rss_object, extract_form_data, RssData

rss_bp = Blueprint("rss", __name__)


@rss_bp.route("/test")
def test_feed():
    # test_data: RssData = {
    #     "homepage": "https://venki.dev/notes",
    #     "channel_title": "venki.dev",
    #     "channel_description": "Notes",
    #     "item_title": "html:nth-child(1) > body:nth-child(2) > div:nth-child(3) > main:nth-child(1) > div:nth-child(2) > main:nth-child(2) > div:nth-child(1) > ul:nth-child(2) > li > div:nth-child(1) > a:nth-child(1) > p:nth-child(1)",
    #     "item_link": "html:nth-child(1) > body:nth-child(2) > div:nth-child(3) > main:nth-child(1) > div:nth-child(2) > main:nth-child(2) > div:nth-child(1) > ul:nth-child(2) > li > div:nth-child(1) > a:nth-child(1)",
    #     "item_pubDate": "html:nth-child(1) > body:nth-child(2) > div:nth-child(3) > main:nth-child(1) > div:nth-child(2) > main:nth-child(2) > div:nth-child(1) > ul:nth-child(2) > li > div:nth-child(1) > p:nth-child(2)",
    #     "item_description": None,
    # }

    test_data = RssData(
        homepage="https://venki.dev/notes",
        channel_title="TODO",
        channel_description="TODO",
        item_title="body:nth-child(2) > div:nth-child(3) > main:nth-child(1) > div:nth-child(1) > main:nth-child(2) > div:nth-child(1) > ul:nth-child(2) li > div > a > p",
        item_link="body:nth-child(2) > div:nth-child(3) > main:nth-child(1) > div:nth-child(1) > main:nth-child(2) > div:nth-child(1) > ul:nth-child(2) li > div > a",
        item_description=None,
        item_pubDate="body:nth-child(2) > div:nth-child(3) > main:nth-child(1) > div:nth-child(1) > main:nth-child(2) > div:nth-child(1) > ul:nth-child(2) li > div > p:nth-of-type(2)",
    )

    test_feed = create_rss_object(test_data, debug=True)

    if isinstance(test_feed, str):
        return render_template("error.html.jinja", message=test_feed), 500

    resp = make_response(render_template("feed.xml.jinja", **test_feed.model_dump()))

    resp.headers["content-type"] = "application/rss+xml"

    return resp


@rss_bp.route("/create", methods=["POST"])
def create_feed():
    conn = get_db_conn()
    cursor = conn.cursor()

    rss_data = extract_form_data().model_dump()

    feed_id = nanoid.generate()

    rss_data["feed_id"] = feed_id

    template_string = "INSERT INTO feeds(feed_id, homepage, channel_title, channel_description, item_title, item_link, item_description, item_pubDate) VALUES(:feed_id, :homepage, :channel_title, :channel_description, :item_title, :item_link, :item_description, :item_pubDate)"

    cursor.execute(template_string, rss_data)
    conn.commit()

    # when the user system is set up we will want to redirect to the user's profile & list of feeds here

    return redirect(f"feed/{feed_id}")


@rss_bp.route("/feed/<feed_id>")
def get_feed(feed_id):

    conn = get_db_conn()
    cursor = conn.cursor()

    response = cursor.execute("SELECT * FROM feeds WHERE feed_id= ? ", (feed_id,))

    rss_data = RssData(**response.fetchone())

    if rss_data is None:
        return "There is no RSS feed with this id in the database!"

    rss_object = create_rss_object(rss_data)

    if isinstance(rss_object, str):
        return "There was an error creating a feed from the retrieved data!"

    resp = make_response(render_template("feed.xml.jinja", **rss_object.model_dump()))

    resp.headers["content-type"] = "application/rss+xml"

    return resp


@rss_bp.route("/preview", methods=["POST"])
def preview_feed():

    preview_data = extract_form_data()

    rss_object = create_rss_object(preview_data)

    if isinstance(rss_object, str):
        return render_template("error.html.jinja", message=rss_object)

    return render_template(
        "preview.html.jinja", **rss_object.model_dump(), preview_data=preview_data
    )
