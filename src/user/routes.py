from flask import Blueprint, render_template, session
from urllib.parse import quote
from db.utils import get_db_conn

user_bp = Blueprint("user", __name__)


@user_bp.route("/")
def home_page():
    conn = get_db_conn()
    cursor = conn.cursor()

    user_id = session["user_id"]

    response = cursor.execute("SELECT * FROM feeds WHERE user_id= ? ", (user_id,))

    feeds = response.fetchall()

    for feed in feeds:
        feed["edit_url"] = f"/edit?url-input={quote(feed['homepage'], safe='')}"

    return render_template("home.html.jinja", feeds=feeds)
