from flask import Blueprint, render_template, request


edit_bp = Blueprint('edit', __name__)

@edit_bp.route("/", methods=["GET"])
def edit_screen():
   return render_template("editor.html.jinja")


@edit_bp.route("/", methods=["POST"])
def edit_screen_with_data():

   print(request.form.to_dict())

   return render_template("editor.html.jinja", input_data=request.form.to_dict() )