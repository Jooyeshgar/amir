from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode, Float
from sqlalchemy.ext.declarative import declarative_base
from passlib.hash import bcrypt

from amir.database import get_declarative_base
Base = get_declarative_base()

## \defgroup DataBase
## @{

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(60), nullable=False)
    username = Column(Unicode(60), nullable=False)
    password = Column(String(300), nullable=False)

    def __init__(self, name, username, password):
    	self.name = name
        self.username = username
        self.password = bcrypt.encrypt(password)

    def validate_password(self, password):
        return bcrypt.verify(password, self.password)


## @}
