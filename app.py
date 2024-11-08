from flask import Flask, render_template, redirect, url_for
from api.routes import api_bp
from auth.routes import auth_bp
from edit.routes import edit_bp
from rss.routes import rss_bp
from proxy.routes import proxy_bp


app = Flask(__name__)


@app.route('/')
def input_url():
    return render_template("input.html.jinja")

# catch an url supplied to the app through the address bar
@app.route('/http<path:url>')
def catch_url(url: str):

    # add back the "http" stripped off by the route selector
    url = f"http{url}"

    # redirect to edit page
    return redirect(f"/edit?url-input={url}")
    


app.register_blueprint(api_bp, url_prefix="/api")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(edit_bp, url_prefix="/edit")
app.register_blueprint(rss_bp, url_prefix="/rss")
app.register_blueprint(proxy_bp, url_prefix="/proxy")


if __name__ == '__main__':
    app.run(debug=True, port=5001)
