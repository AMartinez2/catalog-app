from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from database_setup import User, Item, Base

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the declaratives
#   can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all the conversations with the database
#   and represents a "staging zone" for allthe objects loaded into the database
#   session object/ Any change made against the objects in the session won't
#   be persisted into the database until you call session.commit(). If you're
#   not happy about the changes, you can revert all of them back to the last
#   commit by calling session.rollback()
session = DBSession()

# name = table-item-name(column = data,...)
# session.add(name)
# session.commit()

def addItem(name, catagory, description, email):
    time = str(datetime.now())
    item = Item(name=name, catagory=catagory, description=description, timeCreated=time, user_email=email)
    session.add(item)
    session.commit()

# # add files here # #

user = User(username="test", email="test@mail.com")
session.add(user)
session.commit()

name = "USB Keyboard"
catagory = "Electronics"
description = "Standard 104 key USB 2.0 keyboard. (US layout)"
email = "test@mail.com"
addItem(name, catagory, description, email)

name="USB Mouse"
catagory="Electronics"
description="Standard USB 2.0 computer mouse. 3100 dpi."
email = "test@mail.com"
addItem(name, catagory, description, email)

name="4 Person Tent"
catagory="Outdoors"
description="This stong and sturdy tent can hold up to 4 people. Perfect for outdoors lovers."
email = "test@mail.com"
addItem(name, catagory, description, email)

name="Sleeping Bag"
catagory="Outdoors"
description="One person sleeping bag; Wind protection, multiple colors, and can widthstand temperatures of -20 degrees F."
email = "test@mail.com"
addItem(name, catagory, description, email)

name="Multitool"
catagory="EDC"
description="Expandable and portable, this multitool is perfect for the everyday craftsman or for a hobbyist. Your choice of attatchments and metal type."
email = "test@mail.com"
addItem(name, catagory, description, email)

name="Backpack"
catagory="Outdoors"
description="For hiking trips or general traveling, this backack can carry what you need when you need it. It comes in multiple colors and sizes fitting your style and needs."
email = "test@mail.com"
addItem(name, catagory, description, email)



print "Database updated!"
