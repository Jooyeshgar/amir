from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode, Float
from sqlalchemy.ext.declarative import declarative_base

from amir.database import get_declarative_base
Base = get_declarative_base()

## \defgroup DataBase
## @{

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True)
    name = Column(Unicode(60), nullable=False)
    parent_id = Column(Integer, ColumnDefault(0), ForeignKey('users.id'), nullable=False)
    lft = Column(Integer, nullable=False)
    rgt = Column(Integer, nullable=False)
    type = Column(Integer)      # 0 for Debtor, 1 for Creditor, 2 for both

    def __init__(self, code, name, parent_id, left, right, type):
        self.code = code
        self.name = name
        self.parent_id = parent_id
        self.lft = left
        self.rgt = right
        self.type = type

## @}
