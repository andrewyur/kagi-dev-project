#!/usr/bin/env python

from flask import Flask, render_template, redirect, g, session
from urllib.parse import quote
from edit.routes import edit_bp
from rss.routes import rss_bp
from proxy.routes import proxy_bp
from user.routes import user_bp
import os
import uuid


app = Flask(__name__)

# need this for message flashing
app.secret_key = os.environ["FLASK_SECRET"]


@app.route("/")
def input_url():
    return render_template("input.html.jinja")


# catch an url supplied to the app through the address bar
@app.route("/http<path:url>")
def catch_url(url: str):

    # add back the "http" stripped off by the route selector
    url = f"http{url}"

    # redirect to generate page
    return redirect(f"/edit/gen?url-input={quote(url, safe='')}")


# creates a userid if one does not exist, stores it in the session, and makes it permanent
@app.before_request
def gen_user_id():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())
        session.permanent = True


# need this in production to prevent redirects through http, which cause POST request bodies to be lost
@app.after_request
def specify_secure_redirect(response):
    if os.environ.get("FLASK_ENV") == "production":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )
    return response


@app.teardown_appcontext
def close_db(error):  # type: ignore
    db = g.pop("db", None)
    if db is not None:
        db.close()


app.register_blueprint(edit_bp, url_prefix="/edit")
app.register_blueprint(rss_bp, url_prefix="/rss")
app.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(proxy_bp, url_prefix="/proxy")


def run_prod():
    from waitress import serve
    from db.db_init import init_db

    os.environ["FLASK_ENV"] = "production"

    init_db()

    serve(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))


def run_dev():
    db_path = os.getenv("DB_PATH", "src/rss.db")

    if not os.path.exists(db_path):
        print("initialize the database first!")
    else:
        app.run(debug=True, port=5001)


if __name__ == "__main__":
    run_dev()
