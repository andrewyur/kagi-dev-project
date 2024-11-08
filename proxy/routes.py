from flask import Blueprint, render_template, Response
import requests
from urllib.parse import urlparse
from lxml import html


proxy_bp = Blueprint('proxy', __name__)

@proxy_bp.route("/<path:proxy_url>")
def reflect(proxy_url):

   
   try:
      response = requests.get(proxy_url, headers={'user-agent': 'andrew\'s rss converter'})
   except requests.exceptions.InvalidURL:
      return render_template("error.html.jinja", message="Invalid URL supplied!")

   if response.headers["Content-Type"] == "text/html; charset=utf-8":

      if not response.ok:
         print(response.status_code)
         return render_template("error.html.jinja", message="The webpage could not be loaded!"), 400

      reflected_html = response.text
      
      # maybe I should strip all javascript here?
      # but any malicious javascript that would be returned here would be on the original website the user requested
      # the only time the user loads a website from this page is from their own url, so xss is not a problem here

      # replacing attributes that have relative links with their proxied equivalent, so that they request from the correct location
      
      document = html.document_fromstring(reflected_html)

      url_parts = urlparse(proxy_url)

      for tag in ["img", "script", "link", "a", "form", "audio", "video", "source"]:
         for element in document.cssselect(tag):
            for attribute in ["href", "src", "srcset", "action"]:
               if element.get(attribute) is not None :
                  element.set(attribute, f"/proxy/{url_parts.scheme}://{url_parts.netloc}{element.get(attribute)}")

      return html.tostring(document)
   

   # at this point in the function, the request is for an asset, and we just need to send it back without changing anything

   return Response(
      response=response.content,
      status=response.status_code,
      mimetype=response.headers["content-type"]
   )