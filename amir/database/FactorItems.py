from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode, Float
from sqlalchemy.ext.declarative import declarative_base

from amir.database import get_declarative_base
Base = get_declarative_base()

## \defgroup DataBase
## @{

#Version 0.2 tables
class FactorItems(Base):
    __tablename__ = "factorItems"
    factorItemId        = Column(   Integer,        primary_key = True                      )
    factorItemNo        = Column(   Integer,        nullable = False                        )
    factorItemProduct   = Column(   Integer,        ForeignKey('products.id')               )
    factorItemQnty      = Column(   Float,          ColumnDefault(0),   nullable = False    )
    factorItemUntPrc    = Column(   Float,          ColumnDefault(0),   nullable = False    )
    factorItemUntDisc   = Column(   Unicode(30),    ColumnDefault("0"), nullable = False    )
    factorItemTransId   = Column(   Integer                                                 )
    factorItemDesc      = Column(   Unicode(200),   nullable = True                         )

    def __init__( self, factorItemNo, factorItemProduct, factorItemQnty,
                  factorItemUntPrc, factorItemUntDisc, factorItemTransId, factorItemDesc):

        self.factorItemNo       = factorItemNo
        self.factorItemProduct  = factorItemProduct
        self.factorItemQnty     = factorItemQnty
        self.factorItemUntPrc   = factorItemUntPrc
        self.factorItemUntDisc  = factorItemUntDisc
        self.factorItemTransId  = factorItemTransId
        self.factorItemDesc     = factorItemDesc

## @}
