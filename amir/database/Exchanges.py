from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode, Float
from sqlalchemy.ext.declarative import declarative_base

from amir.database import get_declarative_base
Base = get_declarative_base()

## \defgroup DataBase
## @{

#Version 0.2 tables
class Exchanges(Base):
    __tablename__ = "exchanges"
    exchngId        = Column(   Integer,        primary_key = True                      )
    exchngNo        = Column(   Integer,        nullable = False                        )
    exchngProduct   = Column(   Integer,        ForeignKey('products.id')               )
    exchngQnty      = Column(   Float,          ColumnDefault(0),   nullable = False    )
    exchngUntPrc    = Column(   Float,          ColumnDefault(0),   nullable = False    )
    exchngUntDisc   = Column(   Unicode(30),    ColumnDefault("0"), nullable = False    )
    exchngTransId   = Column(   Integer,        ForeignKey('transactions.transId')      )
    exchngDesc      = Column(   Unicode(200),   nullable = True                         )

    def __init__( self, exchngNo, exchngProduct, exchngQnty,
                  exchngUntPrc, exchngUntDisc, exchngTransId, exchngDesc):

        self.exchngNo       = exchngNo
        self.exchngProduct  = exchngProduct
        self.exchngQnty     = exchngQnty
        self.exchngUntPrc   = exchngUntPrc
        self.exchngUntDisc  = exchngUntDisc
        self.exchngTransId  = exchngTransId
        self.exchngDesc     = exchngDesc

## @}
