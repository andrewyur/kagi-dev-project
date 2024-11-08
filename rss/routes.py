from flask import Blueprint, render_template, make_response, request
from lxml import html
import requests
from email.utils import formatdate
from time import mktime
from dateutil import parser

rss_bp = Blueprint('rss', __name__)


sample_data = {
   "rss_id": "test_feed",    
   "homepage": "https://venki.dev/notes",  
   "channel": {      
      "title": "venki.dev notes",
      "description": "items from venki.dev/notes"
   },
   "base_query": "html > body > div > main > div:nth-of-type(2) > main > div > ul > li > div",
   "item": {   
      "title": {              # required
         "query": " > a > p",
         "attribute": "textContent"
      },
      "link": {               # required
         "query": " > a",
         "attribute": "href"
      },
      "pubDate": {            # optional
         "query": " > p",
         "attribute": "textContent"
      },
      # "descrption": {            # optional
      #    "query": None,
      #    "attribute": None
      # }
   }
}

@rss_bp.route("/test_feed")
def test_feed():

   # might be better to forward the user-agent header from the route request
   response = requests.get(sample_data["homepage"], headers={'user-agent': 'andrew\'s rss converter'})

   if not response.ok:
      return render_template(
         "error.html.jinja", 
         message="There was an error fetching from the supplied webpage!", 
         subtitle=str(e)
      )


   document = html.document_fromstring(response.text)

   html_items = {
      rss_attr: [
         html_item for html_item in document.cssselect(sample_data["base_query"] + sample_data["item"][rss_attr]["query"] )
      ]  for rss_attr in sample_data["item"].keys() 
   }

   get_html_attr = lambda html_item, attr: html_item.text_content() if attr == "textContent" else html_item.get(attr)

   parse_rss_attr = lambda attr, i: get_html_attr(html_items[attr][i], sample_data["item"][attr]["attribute"])

   items_amt = len(html_items["title"])

   # crazy list/dict comprehension, i will make this readable later
   rss_items = [
      {
         attr_title: parse_rss_attr(attr_title, i) for attr_title in sample_data["item"].keys() 
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
            return render_template(
               "error.html", 
               message="There was an error parsing the date from the supplied element!", 
               subtitle=e
            )

         item["pubDate"] = formatdate(mktime(parsed_date.timetuple()), localtime=False, usegmt=True)

         if latest_date is None or latest_date < parsed_date:
            latest_date = parsed_date
         if earliest_date is None or earliest_date > parsed_date:
            earliest_date = parsed_date

      if not item["link"].startswith("http"):
         item["link"] = sample_data["homepage"] + item["link"]

   format_date = lambda x: formatdate(mktime(x.timetuple()), localtime=False, usegmt=True)

   rss_channel = {
      **sample_data["channel"],
      "link": request.base_url
   }

   if latest_date is not None and earliest_date is not None:
      rss_channel["lastBuildDate"] = format_date(latest_date)
      rss_channel["pubDate"] = format_date(earliest_date)

   resp = make_response(
      render_template(
         "feed.xml.jinja", 
         channel=rss_channel,
         items=rss_items
      )
   )
   resp.headers["content-type"] = "application/rss+xml"
   
   return resp


