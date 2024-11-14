from flask import Flask, render_template, redirect, g
from urllib.parse import quote
from auth.routes import auth_bp
from edit.routes import edit_bp
from rss.routes import rss_bp
from proxy.routes import proxy_bp
import os


app = Flask(__name__)

# need this for message flashing
app.secret_key = os.environ["SECRET_KEY"]


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


@app.teardown_appcontext
def close_db(error):  # type: ignore
    db = g.pop("db", None)
    if db is not None:
        db.close()


app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(edit_bp, url_prefix="/edit")
app.register_blueprint(rss_bp, url_prefix="/rss")
app.register_blueprint(proxy_bp, url_prefix="/proxy")


if __name__ == "__main__":
    if not os.path.exists("rss.db"):
        print("initialize the database first!")
    else:
        app.run(debug=True, port=5001)
