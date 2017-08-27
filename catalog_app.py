from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import session as login_session
from flask import make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Item, User
import json
import requests

app = Flask(__name__)

# implement when developing authentication
"""
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"
"""

# Connect to the database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Front page
@app.route('/')
@app.route('/catalog/')
def showItemsMain():
    cat = session.query(Item).group_by(Item.catagory).order_by(Item.catagory)
    latest = session.query(Item).order_by(Item.timeCreated)
    return render_template('list.html', catagories=cat, items=latest)

# Individual item
@app.route('/catalog/<string:item_catagory>/<string:item_name>/')
def showItem(item_catagory, item_name):
    item_result = session.query(Item).filter_by(catagory=item_catagory,
                                                name=item_name)
    return render_template('item.html', item=item_result)

# Run the server on localhost
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
