from flask import Flask, render_template
from api.routes import api_bp
from auth.routes import auth_bp
from edit.routes import edit_bp
from rss.routes import rss_bp


app = Flask(__name__)


# catch an url supplied to the app through the address bar
@app.route('/')
@app.route('/http<path:url>')
def home(url=""):

    # re add the "http" stripped off by the route
    if len(url) > 0:
        url = f"http{url}"

    return render_template("input.html.jinja", url=url)


app.register_blueprint(api_bp, url_prefix="/api")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(edit_bp, url_prefix="/edit")
app.register_blueprint(rss_bp, url_prefix="/rss")


if __name__ == '__main__':
    app.run(debug=True, port=5001)
