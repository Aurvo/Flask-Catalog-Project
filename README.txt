#Prerequisites and Background Information

-The app is meant to be run on a Linux server using Appache2. I ran it using an Amazon Lightsail server instance.

#Relevant Software Iinstalled: -Postgresql -Apache2 -libapache2-mod-wsgi, -SQLAlchemy -Python 2.7 (all the following are Python related)
-pip -Flask 0.9 -Flask-Login 0.1.3 -oauth2client -requests -httplib2

#Relevent Server Configurations: -both the Lightsail and server (ufw) firewalls were configured to only listen on ports 80, 123, and 2200. 
UFW was explicitly configured to deny port 22. Ufw was configured to allow all outgoing transmissions. -the /etc/apache2/sites-enabled/000-
default.conf file was configured to allow apache2 to look for the app (a wsgi app) in /var/www/html -The /etc/apache2/envars file has been 
modified to make apache2 run as ubuntu (default Amazon Lightsail superuser); many of the files' permissions have been modified to allow 
apache2 to use them properly as ubuntu -Lightsail already seems to have its time zone configured to UTC, so there was no need to edit that.

#What this App Does

-This is a simple app that allows users to examine, store, edit, and delete items in an item catalog. The user must log in using his/her 
Google Accunts ID to do anything beyond examining the catalog.
