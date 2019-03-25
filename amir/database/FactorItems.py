from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode, Float
from sqlalchemy.ext.declarative import declarative_base

from amir.database import get_declarative_base
Base = get_declarative_base()

## \defgroup DataBase
## @{

# Version 0.2 tables


class FactorItems(Base):
    __tablename__ = "factorItems"
    id = Column(Integer,                              primary_key=True)
    number = Column(Integer,                          nullable=False)
    productId = Column(Integer, ForeignKey('products.id'))
    qnty = Column(Float, ColumnDefault(0),            nullable=False)
    untPrc = Column(Float, ColumnDefault(0),          nullable=False)
    untDisc = Column(Unicode(30), ColumnDefault("0"), nullable=False)
    factorId = Column(Integer)
    desc = Column(Unicode(200),                       nullable=True)

    def __init__(self, number, productId, qnty,
                 untPrc, untDisc, factorId, desc, id=1):

        self.number = number
        self.productId = productId
        self.qnty = qnty
        self.untPrc = untPrc
        self.untDisc = untDisc
        self.factorId = factorId
        self.desc = desc

## @}
