from flask import Blueprint, render_template, make_response, request, redirect
from lxml import html
import requests
from email.utils import formatdate
from time import mktime
from dateutil import parser
from db.utils import get_db_conn
import nh3
import nanoid

rss_bp = Blueprint('rss', __name__)


@rss_bp.route("/test")
def test_feed():
   test_data = {
      'homepage': 'https://venki.dev/notes', 
      'channel_title': 'venki.dev', 
      'channel_description': 'Notes',
      'item_title': 'html:nth-child(1) > body:nth-child(2) > div:nth-child(3) > main:nth-child(1) > div:nth-child(2) > main:nth-child(2) > div:nth-child(1) > ul:nth-child(2) > li > div:nth-child(1) > a:nth-child(1) > p:nth-child(1)',
      'item_link': 'html:nth-child(1) > body:nth-child(2) > div:nth-child(3) > main:nth-child(1) > div:nth-child(2) > main:nth-child(2) > div:nth-child(1) > ul:nth-child(2) > li > div:nth-child(1) > a:nth-child(1)', 
      'item_pubDate': 'html:nth-child(1) > body:nth-child(2) > div:nth-child(3) > main:nth-child(1) > div:nth-child(2) > main:nth-child(2) > div:nth-child(1) > ul:nth-child(2) > li > div:nth-child(1) > p:nth-child(2)', 
      'item_description': None
   }

   test_feed = create_rss_object(test_data)

   if isinstance(test_feed, str):
      return render_template(
         "error.html.jinja", 
         message=test_feed 
      ), 500

   resp = make_response(
      render_template(
         "feed.xml.jinja", 
         **test_feed
      )
   )

   resp.headers["content-type"] = "application/rss+xml"
   
   return resp


@rss_bp.route("/create", methods=["POST"])
def create_feed():
   conn = get_db_conn()
   cursor = conn.cursor()

   rss_data = extract_form_data()

   feed_id = nanoid.generate()

   rss_data["feed_id"] = feed_id


   print("feed data", rss_data)

   template_string = "INSERT INTO feeds(feed_id, homepage, channel_title, channel_description, item_title, item_link, item_description, item_pubDate) VALUES(:feed_id, :homepage, :channel_title, :channel_description, :item_title, :item_link, :item_description, :item_pubDate)"

   cursor.execute(template_string, rss_data)
   conn.commit()

   # when the user system is set up we will want to redirect to the user's profile & list of feeds here

   return redirect(f"feed/{feed_id}")


@rss_bp.route("/feed/<feed_id>")
def get_feed(feed_id):

   conn = get_db_conn()
   cursor = conn.cursor()

   response = cursor.execute("SELECT * FROM feeds WHERE feed_id= ? ", (feed_id,))

   rss_data = response.fetchone()

   if rss_data is None:
      return "There is no RSS feed with this id in the database!"

   print("fetched data", rss_data)

   rss_object = create_rss_object(rss_data)

   resp = make_response(
      render_template(
         "feed.xml.jinja", 
         **rss_object
      )
   )

   resp.headers["content-type"] = "application/rss+xml"
   
   return resp


@rss_bp.route("/preview", methods=["POST"])
def preview_feed():

   preview_data = extract_form_data()

   print("preview data",preview_data)

   rss_object = create_rss_object(preview_data)

   if isinstance(rss_object, str):
      return render_template(
         "error.html.jinja", 
         message=rss_object 
      )

   return render_template("preview.html.jinja", **rss_object, preview_data=preview_data)


def extract_form_data():
   form_keys = [
      "homepage",
      "channel_title",
      "channel_description",
      "item_title",
      "item_link",
      "item_pubDate",
      "item_description"
   ]

   rss_data =  {k: request.form.get(k) for k in form_keys}

   for k, v in rss_data.items():
      if v == '':
         rss_data[k] = None

   return rss_data


def create_rss_object(rss_data):

   # sanitize user input to protect against xss attacks
   for k,v in rss_data.items():
      if v is not None and nh3.is_html(v):
         return "Only text tags are allowed in the input!"
         
   # might be better to forward the user-agent header from the route request
   response = requests.get(rss_data["homepage"], headers={'user-agent': 'andrew\'s rss converter'})

   if not response.ok:
      return "There was an error fetching from the supplied webpage!"

   document = html.document_fromstring(response.text)


   item_attr_list =  ["item_title", "item_link", "item_description", "item_pubDate"]

   item_attr_list = list(filter(lambda a : rss_data[a] is not None, item_attr_list ))

   html_items = {
      rss_attr: document.cssselect(rss_data[rss_attr]) for rss_attr in item_attr_list
   }

   rss_to_html_attr = {
      "item_title": "textContent",
      "item_link": "href",
      "item_description": "textContent",
      "item_pubDate": "textContent"
   }

   get_attr = lambda el, attr: el.text_content() if attr == "textContent" else el.get(attr)

   parse_rss_attr = lambda attr, i: get_attr(html_items[attr][i],rss_to_html_attr[attr])

   rss_items = []
   for i in range(len(html_items["item_title"])):
      rss_items.append({
         rss_attr.split("_")[-1]: parse_rss_attr(rss_attr, i) for rss_attr in item_attr_list
      })

   # RSS has its own special date format
   format_date = lambda x: formatdate(mktime(x.timetuple()), localtime=False, usegmt=True)

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

         item["pubDate"] = format_date(parsed_date)

         if latest_date is None or latest_date < parsed_date:
            latest_date = parsed_date
         if earliest_date is None or earliest_date > parsed_date:
            earliest_date = parsed_date

      if not item["link"].startswith("http"):
         item["link"] = rss_data["homepage"] + item["link"]


   rss_channel = {
      "title": rss_data["channel_title"],
      "description": rss_data["channel_description"],
      "link": request.base_url
   }

   if latest_date is not None and earliest_date is not None:
      rss_channel["lastBuildDate"] = format_date(latest_date)
      rss_channel["pubDate"] = format_date(earliest_date)

   return {
      "channel": rss_channel,
      "items": rss_items
   }