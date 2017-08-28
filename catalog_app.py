from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import session as login_session
from flask import make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Item, User
import json
import requests

app = Flask(__name__)


# Uncomment when developing authentication
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


# JSON format
@app.route('/catalog/JSON')
def catalogJSON():
    allItems = session.query(Item).all()
    return jsonify(items=[j.serialize for j in allItems])


# Front page
@app.route('/')
@app.route('/catalog/')
def showItemsMain():
    cat = session.query(Item).group_by(Item.catagory).order_by(Item.catagory)
    latest = session.query(Item).order_by(Item.timeCreated)
    return render_template('latest_list.html', catagories=cat, items=latest)


# Individual item
@app.route('/catalog/<string:item_catagory>/<string:item_name>/')
def showItem(item_catagory, item_name):
    item_result = session.query(Item).filter_by(catagory=item_catagory,
                                                name=item_name).one()
    return render_template('item.html', item=item_result)


# List of all items in specific catagory
@app.route('/catalog/<string:item_catagory>/items/')
def showCatagory(item_catagory):
    cat = session.query(Item).group_by(Item.catagory).order_by(Item.catagory)
    cat_items = session.query(Item).filter_by(catagory=item_catagory)
    return render_template('catagory_list.html', catagories=cat,
                                                    items=cat_items)

# Run the server on localhost
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
