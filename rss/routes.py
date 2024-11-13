from flask import Blueprint, render_template, make_response, request
from lxml import html
import requests
from email.utils import formatdate
from time import mktime
from dateutil import parser

rss_bp = Blueprint('rss', __name__)



@rss_bp.route("/preview", methods=["POST"])
def preview_feed():

   preview_data = {   
      "homepage": request.form.get("homepage"),  
      "channel": {      
         "title": request.form.get("channel-title"),
         "description":  request.form.get("channel-description")
      },
      "item": {   
         "title": {
            "query": request.form.get("item-title-query"),
            "attribute": request.form.get("item-title-attribute")
         },
         "link": {
            "query": request.form.get("item-link-query"),
            "attribute": request.form.get("item-link-attribute")
         }
      }
   }

   if request.form.get("item-pubDate-query") is not None and  len(request.form.get("item-pubDate-query")) != 0:
      preview_data["item"]["pubDate"] = {}
      preview_data["item"]["pubDate"]["query"] = request.form.get("item-pubDate-query")
      preview_data["item"]["pubDate"]["attribute"] = request.form.get("item-pubDate-attribute")
   if request.form.get("item-description-query") is not None and len(request.form.get("item-description-query")) != 0:
      preview_data["item"]["description"] = {}
      preview_data["item"]["description"]["query"] = request.form.get("item-description-query")
      preview_data["item"]["description"]["attribute"] = request.form.get("item-description-attribute")

   rss_object = create_rss_object(preview_data)

   if isinstance(rss_object, str):
      return render_template(
         "error.html.jinja", 
         message=rss_object 
      )

   return render_template("preview.html.jinja", **rss_object, preview_data=preview_data)



def create_rss_object(rss_data):
   # might be better to forward the user-agent header from the route request
   response = requests.get(rss_data["homepage"], headers={'user-agent': 'andrew\'s rss converter'})

   if not response.ok:
      return "There was an error fetching from the supplied webpage!"

   document = html.document_fromstring(response.text)

   html_items = {
      rss_attr: [
         html_item for html_item in document.cssselect(rss_data["item"][rss_attr]["query"])
      ]  for rss_attr in rss_data["item"].keys() 
   }

   get_html_attr = lambda html_item, attr: html_item.text_content() if attr == "textContent" else html_item.get(attr)

   parse_rss_attr = lambda attr, i: get_html_attr(html_items[attr][i], rss_data["item"][attr]["attribute"])

   items_amt = len(html_items["title"])

   # crazy list/dict comprehension, i will make this readable later
   rss_items = [
      {
         attr_title: parse_rss_attr(attr_title, i) for attr_title in rss_data["item"].keys() 
      } for i in range(items_amt)
   ]

   # format dates, get earliest and latest pubdates, and format links
   latest_date = None
   earliest_date = None
   for item in rss_items: 
      if "pubDate" in item:
         parsed_date = None
         try: 
            parsed_date = parser.parse(item["pubDate"])
         except Exception as e:
            print(e)
            return "There was an error parsing the date from the supplied element!"

         item["pubDate"] = formatdate(mktime(parsed_date.timetuple()), localtime=False, usegmt=True)

         if latest_date is None or latest_date < parsed_date:
            latest_date = parsed_date
         if earliest_date is None or earliest_date > parsed_date:
            earliest_date = parsed_date

      if not item["link"].startswith("http"):
         item["link"] = rss_data["homepage"] + item["link"]

   format_date = lambda x: formatdate(mktime(x.timetuple()), localtime=False, usegmt=True)

   rss_channel = {
      **rss_data["channel"],
      "link": request.base_url
   }

   if latest_date is not None and earliest_date is not None:
      rss_channel["lastBuildDate"] = format_date(latest_date)
      rss_channel["pubDate"] = format_date(earliest_date)

   return {
      "channel": rss_channel,
      "items": rss_items
   }