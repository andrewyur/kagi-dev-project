# Kagi Full Stack Demo Project

By: Andrew Yurovchak

## How to run

export your google genai api key as the `API_KEY` env var

To run in development mode (given you have some way of running commands defined in pyproject.toml):

- activate the shell with `nix develop`
  - then run `python -m venv .venv`, `source .venv/bin/activate`, and `pip install -r requirements.txt`
- run the db init script `db-init` to initialize the database
- run `dev` to start the development server

To run in production mode:

`docker-compose up`

## Design Outline

The majority of the function of this app happens on the backend. I am using python & flask for the backend of this project for 4 reasons:

- It is easy to write, and easy to read (for simple code)
- This is not an application where performance is critical
  - If I write my code well it will be fast enough
- I already know python, and how to use Flask
- It is fun to write

The frontend is around Jinja2, the templating engine built into flask. Any JS & CSS needed will be located directly in the template files as `<script>` and `<style>` elements.

To persist data, I will likely be using SQLite, because it is very easy to use and set up, and is very portable.

For authentication, I only need something simple and will be using permanent cookies to store a unique user id

To deploy it, I be running it inside a docker image in gcr. I already have a domain name I can use under google cloud provider, so I will provision a subdomain for it to use.

Routing structure:

├──
└──

```md
/                  -> html page where user can input a link to edit
/http...           -> redirects to /edit, as if user had just input the link
/rss/
  ├── /create      -> db interface route
  ├── /delete         ^
  ├── /edit           ^
  ├── /preview     -> preview articles for given rss data
  └── /feed        -> get the rss file for a feed
/edit              -> html page for the user to create an rss feed
  └── /gen         -> generate inital feed data from html using an LLM 
/user              -> user interface for editing/deleting feeds
/proxy             -> proxy page for iframe, so i can get around same-origin policy
```

The backend uses lxml to extract data from the provided page using css queries. To create a feed, the user will direct the frontend to submit css queries to the backend, which are stored in the database. Every time an rss endpoint with a specific id recieves a request, the backend will find the css queries associated with the id in the database, use the queries on the website, and then return the items, formatted into an xml document with jinja.

data schema:

| Column Name | Data Type | Description |
|-|-|-|
| `homepage` | VARCHAR(50) | URL of the of the website to be converted |
| `channel-title` | VARCHAR(50) | Title of the RSS feed |
| `channel-description` | TEXT | Description of the RSS feed |
| `item-title` | TEXT | CSS Query for retrieving the title of RSS feed items |
| `item-link` | TEXT | CSS Query for retrieving the link of RSS feed items |
| `item-pubDate` | TEXT | CSS Query for retrieving the pubDate of RSS feed items |
| `item-description` | TEXT | CSS Query for retrieving the description of RSS feed items |

## Roadmap

- [x] Setup flask server
  - [x] Setup blueprints for each routing section
- [x] add main functionality
  - [x] make a url input screen
  - [x] make rss feeds return data from the database
    - [x] route for generating a preview of data stored in browser session
    - [x] get the database working, and pull in data from the database for each route
  - [x] make rss editor
    - [x] initial screen layout
    - [x] iframe functionality and initial form layout
      - [x] use the html selector for static content
      - [ ] FoUC
      - [x] loading shroud/modal
    - [x] html element selector
    - [x] form validation
    - [x] help modals & more accurate tooltips
    - [x] direct to preview page on submission
  - [x] Endpoint for creating an rss feed
  - [x] use LLM API to construct an initial RSS feed to load into the editor
    - [x] make the input go straight to the preview page, then the user can edit the queries with the editor if they dont like it
    - [x] migrate RssData and RssFeed classes to pydantic
    - [x] structured output for openai
    - [x] add channel title and channel description queries
  - [x] implement caching for each rss feed to reduce the use of the LLM for initial construction
- [ ] go over code, and make things readable
  - [x] make further use of message flashing
  - [x] better exception handling
  - [ ] update route map in readme
- [x] Add authn & authz with cookies
  - [x] add a nav bar with login/logout buttons
  - [x] CRUD operations for feeds in the user api
  - [x] page to display all feeds created by a user
  - [x] require user to be the creator of the feed to edit
- [ ] Configure everything for prod
  - [x] production server
  - [x] move files into src
  - [x] nix flake stuff
  - [x] dockerfile
    - secrets managment
  - [ ] js bundler/minifiers & other file compression
- [ ] deploy to cloud
  - [x] docker compose file
  - [x] use only db path accross project
  - [x] store db in volume in docker
  - [ ] GCP cloud storage bucket
- [ ] test with RSS reader
- [ ] extra feature: atom feed compatibility (is this already compatible with atom feeds?)

## Development Notes

The point and click element selector will probably be the most difficult part of this project for me. The way it is described it seems very similar to the devtools present in various browsers, maybe I can leverage this. There also may be some obscure JS API that could be useful here.

I do think I will be using an LLM (via an API) to try and build the initial RSS feed because it would be very hard/impossible to create an algorithm that would do it correctly. However, I will be trying to minimize the amount I depend on it because it could get very pricey if the service scales

I really like how 12ft.io allows you to input a website by just prepending 12ft.io/ to the webpage's URL. it leads to a very smooth UX, and I think I could do something similar here

For the user to manage RSS feeds, this means there has to be some way to keep track of users, and of user data. Traditionally, what this means is that I would need to implement an authentication system, and a database to store user credentials and feeds. Unfortunately it looks like there is no way around either of these: we will need some sort of database for user data, and the alternatives for email/password authentication either add additional dependencies or make the UX worse. Pocketbase seems like a relatively painless way to do this.

TODO: when this is finally finished and deployed, it would be a good test to see how this works with an actual RSS reader.

to maximize the simplicity of this app, the user should login via a modal, and not a dedicated page. this will prevent unnecessary page loads and reloads.

NOTE: Jinja2 automatically escapes html when rendering variables, which is why I do not escape everything manually when rendering templates.

A good way to reduce calls to the LLM would be to use other users' compositions of the page if they have one instead of sending it off to an LLM.

Another good way to reduce repeated parsing/extraction of the same data is to have the caching system use a hash of the item and the homepage fields as a key instead of the rss_id field, so that if the same rss config is used across different users, it does not get extracted for each user.

since the method for identifying item attributes relies on css selectors, you have to be a bit smart to get a way to uniquely identify each element. Sometimes the list of html elements that we are parsing RSS item attributes from has an id, and you can get the article element by looking for a child under it (i.e. "#list > li > p"). But what do you do when there is no id? or if the id is automatically generated by a frontend framework, and that you cannot trust to stay the same between updates to the website? you could muck around with classes and attribute values, but ultimately, the only way to uniquely identify an html element in a page without relying on ids is by its position in the document. We can do this by using the > selector in conjunction with the :nth-of-type selector. This way, we can simulate indexing through all of the direct childs of each element type of the parent html element until we have what we want. Moreso, we can easily generate a query of this type if we have the DOM node of the element we want by just traversing the tree using the .parentNode attribute until we get to the top level of the document.

I decided to do all the css as style elements in the head of the html page. It seemed a lot easier this way, than having to wrangle separate css files for every page. The template engine makes it very easy to make the css modular, so that the browser is loading only the css necessary for the current page.

I am not a css wizard, and unfortunately firefox does not have any tools to test the webpage at different desktop resolutions other than shrinking the screen. The website looks good on my machine, and all of the ones I have at my disposal to test it with, but it may not look good on yours.

For the same reason I wrote all the CSS as style tags in the various templates, I will be writing all of the JS as script tags.

Because iframe limits interactions to the same-origin policy (meaning I cannot access the document of the other page unless it was loaded from the same origin), I will be making a proxy page that processes the html and strips it of any js, and then serves it as if it were its own. This way, when I load the content in my iframe, I can load the document as if it were from my own domain. This presents a couple security problems, but hopefully they can be solved by restricting CORS or adding authentication to the page.

It is unfortunately going to be very impractical to completely replicate a webpage using my proxy page, because webpages these days come in so many pieces, and the links that refer the browser to them are often relative, and are scattered all throughout each others contents. To make a webpage rendered via proxy look exactly like the real thing, I would have to search through every asset file for relative links, and replace them on the server side, which is quite a hassle. The webpages look mostly similar, off except for a font or a broken image here or there, and that is good enough for my purposes.

looking back, it probably would have been a good idea to use some kind of framework, at least for the rss editor, because the code is getting very cluttered and hard to read...

Actually, once I refactored everything into classes, the code became a lot more readable and easier to work with. love that!

I decided to get rid of the option for the user to select the html attribute they want to be incorporated into the feed, because most of the time it will be textContent, or href for the article link. This does make it impossible to use in some edge cases, but I feel like this is a fair trade because it allows for the user to do the entire process without any knowledge of HTML/CSS. This will open the application up to a much larger userbase, as there are a good chunk of people who know what an rss feed is, but are not technically inclined and have little to no knowledge of html & css.

I opted to create a db initialization script instead of directly inclduing the db file inside the version control system, because I don't need a substantial amount of seed data, and I want to be able to use the system locally without messing up the repository.

For the llm, I originally decided to use google gemini's free api, but it was so slow (>10s per prompt) and lacked the ability to send concurrent requests so i decided to switch to openai.

The javascript inside the script tag for the editor page has grown to an unweildy length. I was debating about splitting it into multiple files, and calling them all in as separate script tags to make the code more readable, but nearly all of the code is very tightly coupled with the html of the page, and is not going to be re used at all, so I thought it would make more sense in this scenario to keep all of the relevant code in one file, and try to make it more readable with comments.

A username and password based auth system would be overkill for this app I think, so i will be using cookies instead of cooking up my own auth system and integration. This does mean that a user can only access their feeds from the same browser they were created in but it immensely simplifies matters for me, and simplifies the experience for the user as well. Of course, this would not be suitable for a fully fledged, user-facing application, and in that case, I would expect to have access to kagi's SSO provider to identify users, or to have the time to build my own authentication system.
