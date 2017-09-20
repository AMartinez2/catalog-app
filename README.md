# UDACITY Project 3 Catalog App

A simple catalog application allowing users to view items in a catalog, as well as create and edit new or existing items. This app uses Google+ sign in to allow user functionality. 

## Requirements

This project was built in a vagrant machine running `Vagrant 1.9.7`.

Running the code requires `Python 2.7`, `Sqlalchemy 1.1.11`, and `Flask 0.9`. Versions can differ, but no testing was done on later versions.

Install python [here](https://www.python.org/downloads/).

Flask and Sqlalchemy can be installed using Python's pip module.

``` sh
$ pip install flask
$ pip install sqlalchemy
```

## Setup

If you want the database to be empty and start off with an empty site, simply run

```$ python database_setup.py``` to create the database.

Then run
```$ python catalog_app.py``` to start the app.

Connect to `localhost:5000` to access the site.

If you don't want an empty site, the `populatedatabase.py` file has some catalog entries already filled out. Simply run `populatedatabase.py` after creating the database to add items to the catalog. So in order,

``` sh
$ python database_setup.py
$ python populatedatabase.py
$ python catalog_app.py
```

Then connect to `localhost:5000`.
