from flask import Blueprint, render_template, make_response, request as flask_request
from pyquery import PyQuery as pq
from urllib import request as urllib_request
from email.utils import formatdate
from time import mktime
from datetime import datetime
from dateutil import parser

rss_bp = Blueprint('rss', __name__)


sample_data = {
   "rss_id": "test_feed",    
   "homepage": "https://venki.dev/notes",  
   "channel": {      
      "title": "venki.dev notes",
      "language": "en-us",
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
      "pubDate": {            # required
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


   html = None
   try:
      # might be better to forward the user-agent header from the route request
      req = urllib_request.Request(sample_data["homepage"], headers={'user-agent': 'andrew\'s rss converter'})

      response = urllib_request.urlopen(req)

      html = response.read().decode('utf-8') 

   except Exception as e:
      return render_template(
         "error.html", 
         message="There was an error fetching from the supplied webpage!", 
         subtitle=str(e)
      )


   document = pq(html)

   html_items = {
      rss_attr: [
         html_item for html_item in document(sample_data["base_query"] + sample_data["item"][rss_attr]["query"] )
      ]  for rss_attr in sample_data["item"].keys() 
   }

   get_html_attr = lambda html_str, attr: pq(html_str).text() if attr == "textContent" else pq(html_str).attr(attr)

   parse_rss_attr = lambda attr, i: get_html_attr(html_items[attr][i], sample_data["item"][attr]["attribute"])

   items_amt = len(html_items["title"])

   # crazy list/dict comprehension, i will make this readable later
   rss_items = [
      {
         attr_title: parse_rss_attr(attr_title, i) for attr_title in sample_data["item"].keys() 
      } for i in range(items_amt)
   ]

   # format dates, get most recent date, and format links
   latest_date = None
   for item in rss_items: 
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

      if not item["link"].startswith("http"):
         item["link"] = sample_data["homepage"] + item["link"]



   rss_channel = {
      **sample_data["channel"],
      "lastBuildDate": formatdate(mktime(datetime.now().timetuple()), localtime=False, usegmt=True),
      "pubDate": formatdate(mktime(latest_date.timetuple()), localtime=False, usegmt=True),
      "link": flask_request.base_url
   }

   resp = make_response(
      render_template(
         "feed.xml", 
         channel=rss_channel,
         items=rss_items
      )
   )
   resp.headers["content-type"] = "application/rss+xml"
   
   return resp


