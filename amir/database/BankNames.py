from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode, Float
from sqlalchemy.ext.declarative import declarative_base

import sys
for i in sys.path:
    print i

from amir.database import get_declarative_base
Base = get_declarative_base()

## \defgroup DataBase
## @{

#Version 0.2 tables
class BankNames(Base):
    __tablename__ = 'BankNames'
    Id   = Column(Integer    , primary_key=True)
    Name = Column(Unicode(50), nullable=False)

    def __init__(self, name):
        self.Name = name

## @}
