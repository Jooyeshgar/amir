from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode, Float
from sqlalchemy.ext.declarative import declarative_base

from amir.database import get_declarative_base
Base = get_declarative_base()

## \defgroup DataBase
## @{


class Permissions(Base):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(60), nullable=False)
    value = Column(String(20), nullable=False)

    def __init__(self, name, value, id=1):
        self.name = name
        self.value = value

## @}
