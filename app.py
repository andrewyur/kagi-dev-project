from flask import Flask, render_template
from api.routes import api_bp
from auth.routes import auth_bp
from edit.routes import edit_bp
from rss.routes import rss_bp


app = Flask(__name__)


@app.route('/')
def input_url():
    return render_template("input.html")

# catch an url supplied to the app through the address bar
@app.route('/http<path:url>')
def catch_url(url: str):

    # add back the "http" stripped off by the route selector
    url = f"http{url}"

    # redirect to edit page


app.register_blueprint(api_bp, url_prefix="/api")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(edit_bp, url_prefix="/edit")
app.register_blueprint(rss_bp, url_prefix="/rss")


if __name__ == '__main__':
    app.run(debug=True, port=5001)
