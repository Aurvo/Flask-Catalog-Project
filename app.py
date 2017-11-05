from flask import Flask, render_template, request, redirect, url_for
from flask import flash, jsonify, make_response
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import UnmappedInstanceError
from db_setup import Base, Category, Item, DB_STRING
import datetime
import random
import string
import requests
import httplib2
import json
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import sys

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # needed for message flashing

engine = create_engine(DB_STRING)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(
    open('/var/www/html/client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Udacity Catalog App"

# Helper Functions

def getFirstCategory():
    return session.query(Category).first()


def getCategory(category_id):
    return session.query(Category).filter_by(id=category_id).first()


def getAllCategories():
    return session.query(Category).all()


def getItem(item_id):
    return session.query(Item).filter_by(id=item_id).first()


def getAllItems(category_id):
    return session.query(Item).filter_by(category_id=category_id).all()


def doDelete():
    try:
        session.delete(getItem(int(request.form['itemID'])))
        session.commit()
    except UnmappedInstanceError:
        # if there's an error here, it's likely because the user hit the back
        # or refresh button and ended up resubmitting a deletion form for an
        # item that's alreay deleted. In this case, the deletion process
        # should stop and the page should be loaded as normal.
        return
    flash("Deletion successful")

# Routing Functions


@app.route('/')
@app.route('/catalog/', methods=['GET', 'POST'])
def catalogHome():
    newItems = (session.query(Item).order_by(Item.last_updated.desc())
                .limit(10))
    # handle deletes - can't delete items if not logged in
    if request.method == 'POST' and 'username' in login_session:
        doDelete()
    elif request.method == 'POST':
        flash("Deletion Failed - not logged in")
    # render page
    return render_template('catalog.html',
                           categories=getAllCategories(),
                           category=getFirstCategory(),
                           recentItems=newItems,
                           STATE=generateNewLoginState(),
                           isLoggedIn='username' in login_session)


@app.route('/catalog/<int:category_id>/items/',
           methods=['GET', 'POST'])
def catalogItems(category_id):
    # handle deletes - can't delete items if not logged in
    if request.method == 'POST' and 'username' in login_session:
        doDelete()
    elif request.method == 'POST':
        flash("Deletion failed - not logged in")
    # render page
    return render_template('catalogItems.html',
                           categories=getAllCategories(),
                           category=getCategory(category_id),
                           catalogItems=getAllItems(category_id,),
                           STATE=generateNewLoginState(),
                           isLoggedIn='username' in login_session)


@app.route('/catalog/<int:category_id>/add/',
           methods=['GET', 'POST'])
def addItem(category_id):
    # can't get or post to this page if not logged in
    if 'username' not in login_session:
        flash("Cannot add item - not logged in")
        return redirect(url_for('catalogItems', category_id=category_id))
    if request.method == 'POST':
        itemName = request.form['name']
        session.add(Item(name=itemName,
                         description=request.form['description'],
                         category_id=request.form['category']))
        session.commit()
        flash("%s successfully added" % itemName)
        return redirect(url_for('catalogItems', category_id=category_id))
    else:
        return render_template('addItem.html',
                               categories=getAllCategories(),
                               category=getCategory(category_id),
                               STATE=generateNewLoginState(),
                               isLoggedIn='username' in login_session)


@app.route('/catalog/<int:category_id>/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    # can't get or post to this page if not logged in
    if 'username' not in login_session:
        flash("Cannot edit item - not logged in")
        return redirect(url_for('catalogItems', category_id=category_id))
    item = getItem(item_id)
    if request.method == 'POST':
        itemName = request.form['name']
        item.name = itemName
        item.description = request.form['description']
        item.category_id = request.form['category']
        item.last_updated = datetime.datetime.now()
        session.add(item)
        session.commit()
        flash("%s successfully edited" % itemName)
        return redirect(url_for('catalogItems', category_id=category_id))
    else:
        return render_template('editItem.html',
                               categories=getAllCategories(),
                               category=getCategory(category_id),
                               item=item,
                               STATE=generateNewLoginState(),
                               isLoggedIn='username' in login_session)

# LOGIN/LOGOUT


def generateNewLoginState():
    # Generates and returns a random state token of capital letters and
    # digits. Used by all the webpages for logging the user in.
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return state


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Ensure state token passed to gconnect request = state passed to client
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Confirm the code passed to client from Google = code passed
        # to this server by the client. The confirmation is done by
        # passing the code to the Google Oauth server and leting it confirm
        # they're the same. It will then give us a credentials object.
        oauth_flow = flow_from_clientsecrets('/var/www/html/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
	return response
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already\
connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' "style = width: 300px; height: 300px;border-radius: 150px;\
-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    # Sometimes, the Google username may not be present.
    # Flash a welcome message containg the user's Google username if
    # ppresent. Else, flash a generic welcome message.
    uname = login_session['username']
    if uname and uname != "":
        flash("You are now logged in as %s" % uname)
    else:
        flash("You are now logged in. Welcome!")
    # return
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    # make sure user had an access token - generate error page if not
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # logout requests for the Google Oath 2.0 API go to this URL
    url = 'https://accounts.google.com/o/oauth2/revoke?token=\
%s' % login_session['access_token']
    h = httplib2.Http()
    # send GET request to logout url
    result = h.request(url, 'GET')[0]
    # if request returns a status of 200, destroy login session info
    # flash message confirming logout, else generate an error page
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        flash("You are now logged out.")
        return redirect(url_for('catalogHome'))
    else:
        response = make_response(json.dumps('Failed to revoke token for \
given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# JSON Endpoints


@app.route('/catalog/menu/<int:item_id>/JSON/')
def getJSONMenuItem(item_id):
    item = getItem(item_id)
    return jsonify(Catalog_Item=item.serialize)

# SERVER STARTUP


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'  # needed for message flashing
    app.run(host='0.0.0.0', port=80)
