from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import session as login_session
from flask import make_response
from sqlalchemy import create_engine, asc, func
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Item, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from datetime import datetime
import httplib2
import json
import requests
import random
import string


app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Project"


# Connect to the database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# JSON format
@app.route('/catalog/JSON/')
@app.route('/catalog/json/')
def catalogJSON():
    allItems = session.query(Item).all()
    return jsonify(items=[j.serialize for j in allItems])


# Front page
@app.route('/')
@app.route('/catalog/')
def showItemsMain():
    cat = session.query(Item).group_by(
                            func.upper(Item.catagory)).order_by(Item.catagory)
    latest = session.query(Item).order_by(Item.timeCreated.desc())
    return render_template('latest_list.html', catagories=cat, items=latest)


# Individual item
@app.route('/catalog/<string:item_catagory>/<string:item_name>/')
def showItem(item_catagory, item_name):
    item_result = session.query(Item).filter_by(catagory=item_catagory,
                                                name=item_name).one()
    return render_template('item.html', item=item_result)


@app.route('/catalog/<string:item_catagory>/<string:item_name>/JSON/')
@app.route('/catalog/<string:item_catagory>/<string:item_name>/json/')
def itemJSON(item_catagory, item_name):
    item_result = session.query(Item).filter_by(catagory=item_catagory,
                                                name=item_name).one()
    return jsonify(items=[item_result.serialize])


# List of all items in specific catagory
@app.route('/catalog/<string:item_catagory>/items/')
def showCatagory(item_catagory):
    cat = session.query(Item).group_by(func.upper(
        Item.catagory)).order_by(Item.catagory)
    cat_items = session.query(Item).filter_by(catagory=item_catagory)
    return render_template('catagory_list.html', catagories=cat,
                           items=cat_items)


@app.route('/catalog/<string:item_catagory>/items/JSON/')
@app.route('/catalog/<string:item_catagory>/items/json/')
def catagoryJSON(item_catagory):
    cat_items = session.query(Item).filter_by(catagory=item_catagory)
    return jsonify(items=[j.serialize for j in cat_items])


# Edit specific items
@app.route('/catalog/<string:item_catagory>/<string:item_name>/edit/',
           methods=['GET', 'POST'])
def editItem(item_catagory, item_name):
    # In case not logged in user accesses site using the url
    if 'username' not in login_session:
        return redirect(url_for('loginPage'))

    item_result = session.query(Item).filter_by(catagory=item_catagory,
                                                name=item_name).one()
    if request.method == 'POST':
        if request.form['name']:
            item_result.name = request.form['name']
        if request.form['description']:
            item_result.description = request.form['description']
        if request.form['catagory']:
            item_result.catagory = request.form['catagory']
        session.add(item_result)
        session.commit()
        return redirect(url_for('showItemsMain'))
    else:
        return render_template('edit-item.html', item=item_result)


# Add new Item
@app.route('/catalog/newitem/', methods=['GET', 'POST'])
def createItem():
    if 'username' not in login_session:
        return redirect(url_for('loginPage'))

    if request.method == 'POST':
        if request.form['name'] and request.form[
                'description'] and request.form['catagory']:
            time = str(datetime.now())
            item1 = Item(name=request.form['name'],
                         catagory=request.form['catagory'],
                         description=request.form['description'],
                         timeCreated=time)
            session.add(item1)
            session.commit()
            return redirect(url_for('showItemsMain'))
    else:
        return render_template('add-item.html')


# Delete specific item
@app.route('/catalog/<string:item_catagory>/<string:item_name>/delete/',
           methods=['GET', 'POST'])
def deleteItem(item_catagory, item_name):
    if 'username' not in login_session:
        return redirect(url_for('loginPage'))

    result_item = session.query(Item).filter_by(
                                catagory=item_catagory, name=item_name).one()
    if request.method == 'POST':
        session.delete(result_item)
        session.commit()
        return redirect(url_for('showItemsMain'))
    else:
        return render_template('delete-item.html', item=result_item)


# Login page
@app.route('/login/')
def loginPage():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # Uncomment next line and comment line after to see session state #
    # return "The current session state is %s" % login_session['state']
    return render_template('login_page.html', STATE=state)


# Logout page
@app.route('/disconnect/')
def disconnect():
    if 'provider' in login_session:
        gdisconnect()
        return redirect(url_for('showItemsMain'))
    else:
        return redirect(url_for('showItemsMain'))


def getUserId(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    try:
        user = session.query(User).filter_by(id=user_id).one()
        return user
    except:
        return None


def createUser(login_session):
    newUser = User(username=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Function provided by UDACITY
# Google accounts
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
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
        response = make_response(json.dumps(
                                 'Current user is already connected.'), 200)
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
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserId(data['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    return "<h1>Done</h1>"


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect/')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
                                'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Run the server on localhost
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
