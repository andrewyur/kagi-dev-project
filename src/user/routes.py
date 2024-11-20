from flask import Blueprint, render_template, session, request
from urllib.parse import quote
from db.utils import get_db_conn
import os

user_bp = Blueprint("user", __name__)


@user_bp.route("/")
def home_page():
    conn = get_db_conn()
    cursor = conn.cursor()

    user_id = session["user_id"]

    response = cursor.execute("SELECT * FROM feeds WHERE user_id= ? ", (user_id,))

    feeds = response.fetchall()

    # using absolute urls here cause the form to be submitted to http instead of https, which causes a redirect to https, which turns the POST request into a GET request, causing the form data to be lost

    # however, using https locally breaks the server, because https is handled entirely by google cloud run, and the applictaion thinks it is running in http

    for feed in feeds:
        feed["edit_url"] = (
            f"https://{request.headers['Host']}/edit?url-input={quote(feed['homepage'], safe='')}"
            if os.environ.get("FLASK_ENV") == "production"
            else f"/edit?url-input={quote(feed['homepage'], safe='')}"
        )

    return render_template("home.html.jinja", feeds=feeds)
