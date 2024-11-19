from flask import (
    Blueprint,
    render_template,
    make_response,
    redirect,
    flash,
    session,
    request,
)
from db.utils import get_db_conn
import nanoid
from rss.utils import create_rss_object, extract_form_data, RssData
import pydantic

rss_bp = Blueprint("rss", __name__)


@rss_bp.route("/create", methods=["POST"])
def create_feed():
    conn = get_db_conn()
    cursor = conn.cursor()

    rss_data: dict
    try:
        rss_data = extract_form_data().model_dump()
    except pydantic.ValidationError:
        flash("Could not create feed from given data!")
        return redirect("/")

    feed_id = nanoid.generate()

    rss_data["user_id"] = session["user_id"]
    rss_data["feed_id"] = feed_id

    template_string = "INSERT INTO feeds(user_id, feed_id, homepage, channel_title, channel_description, item_title, item_link, item_description, item_pubDate) VALUES(:user_id, :feed_id, :homepage, :channel_title, :channel_description, :item_title, :item_link, :item_description, :item_pubDate)"

    cursor.execute(template_string, rss_data)
    conn.commit()

    return redirect("/user")


@rss_bp.route("/delete/<feed_id>", methods=["POST"])
def delete_feed(feed_id):
    conn = get_db_conn()
    cursor = conn.cursor()

    feed_creator = cursor.execute(
        "SELECT user_id FROM feeds WHERE feed_id = ?", (feed_id,)
    ).fetchone()

    if feed_creator is None:
        flash("There is no feed with this id!")
        return redirect("/")

    if feed_creator["user_id"] != session["user_id"]:
        flash("You don't have permission to edit this feed!")
        return redirect("/")

    cursor.execute("DELETE FROM feeds WHERE feed_id = ?", (feed_id,))
    conn.commit()

    return redirect("/user")


@rss_bp.route("/edit", methods=["POST"])
def edit_feed():
    conn = get_db_conn()
    cursor = conn.cursor()

    rss_data: dict
    try:
        rss_data = extract_form_data().model_dump()
    except pydantic.ValidationError:
        flash("Could not create feed from given data!")
        return redirect("/")

    rss_data["feed_id"] = request.form.get("feed_id")

    feed_creator = cursor.execute(
        "SELECT user_id FROM feeds WHERE feed_id = ?", (rss_data["feed_id"],)
    ).fetchone()

    if feed_creator is None:
        flash("There is no feed with this id!")
        return redirect("/")

    if feed_creator["user_id"] != session["user_id"]:
        flash("You don't have permission to edit this feed!")
        return redirect("/")

    template_string = "UPDATE feeds SET channel_title = :channel_title, channel_description = :channel_description, item_title = :item_title, item_link = :item_link, item_description = :item_description, item_pubDate = :item_pubDate WHERE feed_id = :feed_id"

    cursor.execute(template_string, rss_data)

    conn.commit()

    return redirect("/user")


@rss_bp.route("/feed/<feed_id>")
def get_feed(feed_id):

    conn = get_db_conn()
    cursor = conn.cursor()

    response = cursor.execute("SELECT * FROM feeds WHERE feed_id= ? ", (feed_id,))

    fetch_response = response.fetchone()

    if fetch_response is None:
        return "There is no RSS feed with this id in the database!"

    rss_data = RssData(**fetch_response)

    rss_object = create_rss_object(rss_data)

    if isinstance(rss_object, str):
        return "There was an error creating a feed from the retrieved data!"

    resp = make_response(render_template("feed.xml.jinja", **rss_object.model_dump()))

    resp.headers["content-type"] = "application/rss+xml"

    return resp


@rss_bp.route("/preview", methods=["POST"])
def preview_feed():

    preview_data: RssData
    try:
        preview_data = extract_form_data()
    except pydantic.ValidationError:
        flash("Could not create feed from given data!")
        return redirect("/")

    feed_id = request.form.get("feed_id")

    preview_data_dump = preview_data.model_dump()

    if feed_id is not None and feed_id != "":
        preview_data_dump["feed_id"] = feed_id

    rss_object = create_rss_object(preview_data)

    if isinstance(rss_object, str):
        flash(f"Could not create feed from given data: {rss_object}")
        return redirect("/")

    return render_template(
        "preview.html.jinja", **rss_object.model_dump(), preview_data=preview_data_dump
    )
