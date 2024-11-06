from flask import Flask, render_template

# if this was a bigger app, I would use blueprints and organize the different routes into folders, but this has only 1 route
app = Flask(__name__)

# catch an url supplied to the app through the address bar
@app.route('/')
@app.route('/http<path:url>')
def home(url=""):

    # re add the http stripped off by the route
    if len(url) > 0:
        url = f"http{url}"

    return render_template("input.html.jinja", url=url)

if __name__ == '__main__':
    app.run(debug=True)
