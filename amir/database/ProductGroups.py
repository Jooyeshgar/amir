from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode, Float
from sqlalchemy.ext.declarative import declarative_base

from amir.database import get_declarative_base
Base = get_declarative_base()

## \defgroup DataBase
## @{

# Version 0.2 tables


class ProductGroups(Base):
    __tablename__ = "productGroups"
    id = Column(Integer,       primary_key=True)
    code = Column(Unicode(20), nullable=False)
    name = Column(Unicode(60), nullable=False)
    buyId = Column(Integer, ForeignKey('subject.id'))
    sellId = Column(Integer, ForeignKey('subject.id'))

    def __init__(self,   code,   name,   buyId,  sellId, id=1):
        self.code = code
        self.name = name
        self.buyId = buyId
        self.sellId = sellId

## @}
