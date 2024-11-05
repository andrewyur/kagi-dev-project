# Kagi Full Stack Demo Project

By: Andrew Yurovchak

## How to run

visit the link: <link-here>

OR

clone this repo, and run `docker command`

## Design Outline

The frontend will likely use HTMX, as it is a simple framework that would minimize the amount of js shipped to the user

The majority of the function of this app will happen on the backend. I will be using python & flask for the backend of this project for 4 reasons:

- It is easy to write, and easy to read (for simple code)
- This is not an application where performance is critical
- I already know python, and how to use Flask
- It is fun to write

This application may need some way to persist data. A database will complicate matters a lot, so I will try to stick to a JSON file or something similar

I will likely be hosting this on google cloud run, as I am comfortable with making docker containers, and I have a good amount of familiarity with the platform.

## Development Notes

The point and click element selector will probably be the most difficult part of this project for me. The way it is described it seems very similar to the devtools present in various browsers, maybe I can leverage this. There also may be some obscure JS API that could be useful here.

I do think I will be using an LLM (via an API) to try and build the initial RSS feed because it would be very hard/impossible to create an algorithm that would do it correctly. However, I will be trying to minimize the amount I depend on it because it could get very pricey if the service scales

I really like how 12ft.io allows you to input a website by just prepending 12ft.io/ to the webpage's URL. it leads to a very smooth UX, and I think I could do something similar here
