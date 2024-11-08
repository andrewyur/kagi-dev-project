from flask import Blueprint, render_template, request


edit_bp = Blueprint('edit', __name__)

@edit_bp.route("/")
def edit_screen():
   return render_template("editor.html.jinja")