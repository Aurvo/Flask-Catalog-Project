PREREQUISITE SOFTWARE:

This app is, in part, a web server, so you should make sure you intend to run it in
an environment that allows for that.

To run the app, your environment will need Python 2.7, SQLite 3 and the following
Python packages:

SQLAlchemy
Flask 0.9
Flask-Login 0.1.3
oauth2client
requests
httplib2

If the application is still producing errors after all this is installed, try running
these commnads in order (or their equivalents if you're not on Linux) before trying again:

sudo apt-get -qqy update
sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade
sudo apt-get -qqy install python-sqlalchemy
sudo apt-get -qqy install python-pip
sudo pip install --upgrade pip
sudo pip install werkzeug==0.8.3
sudo pip install flask==0.9
sudo pip install Flask-Login==0.1.3
sudo pip install oauth2client
sudo pip install requests
sudo pip install httplib2

RUNNING THE APP:

Simply run dp_populate.py to populate the database with data and then run app.py to start
running the server on port 8080. You should be able to access the home page by
going to http://localhost:8080/.

To see the JSON endpoint, go to http://localhost:8080/catalog/menu/#/JSON/ -- replacing
"#" with one of the catalog item IDs (a number from 1 through 11 if you have just
ran the db_populate.py file and have not edited the database in any other way).

REFEREBCES:

Much of my Python code is based off of samples from Udacity's Full Stack Foundations and Authentication
& Authorization: OAuth courses in my project--making alterations when necessary to accommodate
my own Catalog app instead of the Restauraunt Menu app used in those courses. Even the
Javascript and div with an ID of "login-btn" in the base.html template file as well as
that string of Linux commands mentioned earlier in this README are based an stuff from
Udacity's Git repository for the Oath course located at:

https://github.com/udacity/OAuth2.0

I'm pretty sure I used what a lot of us students were expected to use, here, but I just
wanted to mention this in case what I have in this folder isn't original enough.