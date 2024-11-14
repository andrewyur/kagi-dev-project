from flask import Blueprint, render_template
import requests
from lxml import html


proxy_bp = Blueprint('proxy', __name__)

@proxy_bp.route("/<path:proxy_url>")
def reflect(proxy_url):

   try:
      response = requests.get(proxy_url, headers={'user-agent': 'andrew\'s rss converter'})
   except requests.exceptions.InvalidURL:
      return render_template("error.html.jinja", message="Malformed URL supplied!")

   if response.headers["Content-Type"] == "text/html; charset=utf-8":

      if not response.ok:
         print(response.status_code)
         return render_template("error.html.jinja", message="The webpage could not be loaded!"), 400

      reflected_html = response.text
      
      document = html.document_fromstring(reflected_html)

      # edits to the dom in the webpage's script tags can cause issues with the css queries
      for script in document.cssselect("script"):
         script.drop_tree()
      
      document.make_links_absolute(proxy_url)

      return html.tostring(document)
   
   # this is only for the initial html page, not anything else
   return 400