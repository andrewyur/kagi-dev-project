# Kagi Full Stack Demo Project

By: Andrew Yurovchak

## How to run

visit the link: <link-here>

OR

clone this repo, and run `docker command`

## Design Outline

The frontend will likely use HTMX, as it is a simple framework that would minimize the amount of js shipped to the user. However, a small amount of JS will likely be needed for session management, and for this i will probably be using just basic js.

The majority of the function of this app will happen on the backend. I will be using python & flask for the backend of this project for 4 reasons:

- It is easy to write, and easy to read (for simple code)
- This is not an application where performance is critical
  - If I write my code well it will be fast enough
- I already know python, and how to use Flask
- It is fun to write

To persist data, I will likely be using a self hosted instance of PocketBase, which is a free, open-source NoSQL database with built in authentication. I will be running this locally inside the same docker image as my backend, which eliminates the hassle of cross-container communication.

To deploy it, I will be creating a nix environment, and running it on a cloud vm (likely nixos on a google compute instance). I already have a domain I can use under google cloud provider, so I will provision a subdomain for it to use.

## Development Notes

The point and click element selector will probably be the most difficult part of this project for me. The way it is described it seems very similar to the devtools present in various browsers, maybe I can leverage this. There also may be some obscure JS API that could be useful here.

I do think I will be using an LLM (via an API) to try and build the initial RSS feed because it would be very hard/impossible to create an algorithm that would do it correctly. However, I will be trying to minimize the amount I depend on it because it could get very pricey if the service scales

I really like how 12ft.io allows you to input a website by just prepending 12ft.io/ to the webpage's URL. it leads to a very smooth UX, and I think I could do something similar here

For the user to manage RSS feeds, this means there has to be some way to keep track of users, and of user data. Traditionally, what this means is that I would need to implement an authentication system, and a database to store user credentials and feeds. Unfortunately it looks like there is no way around either of these: we will need some sort of database for user data, and the alternatives for email/password authentication either add additional dependencies or make the UX worse. Pocketbase seems like a relatively painless way to do this.
