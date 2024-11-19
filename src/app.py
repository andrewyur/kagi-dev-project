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

    if not os.path.exists("src/rss.db"):
        print("initialize the database first!")
    else:
        serve(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))


def run_dev():
    if not os.path.exists("src/rss.db"):
        print("initialize the database first!")
    else:
        app.run(debug=True, port=5001)


if __name__ == "__main__":
    run_dev()
