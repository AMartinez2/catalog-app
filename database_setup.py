from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine


Base = declarative_base()


# User table
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Returning object data in easily serializable format"""
        return {
            'id'        : self.id,
            'username'  : self.username,
            'email'     : self.email,
        }


# Catagories table
class Catagory(Base):
    __tablename__ = 'catagory'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Returning object data in easily serializable format"""
        return {
            'id'    : self.id,
            'name'  : self.name,
        }
        

# Items table
class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(500), nullable=True)
    timeCreated = Column(String(250), nullable=False)
    catagory = Column(String(250), ForeignKey('catagory.name'), nullable=False)
    cat = relationship(Catagory)
    user_email = Column(Integer, ForeignKey('user.email'))
    user = relationship(User)

    @property
    def serialize(self):
        """Returning object data in easily serializable format"""
        return {
            'id'            : self.id,
            'name'          : self.name,
            'catagory'      : self.catagory,
            'description'   : self.description,
            'timeCreated'   : self.timeCreated,
        }


# Needs to be at the end of the file
engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
