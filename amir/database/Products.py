from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode, Float
from sqlalchemy.ext.declarative import declarative_base

from amir.database import get_declarative_base
Base = get_declarative_base()

## \defgroup DataBase
## @{

#Version 0.2 tables
class Products(Base):
    __tablename__ = "products"
    id              = Column(   Integer,                            primary_key = True      )
    code            = Column(   Unicode(20),                        nullable    = False     )
    name            = Column(   Unicode(60),                        nullable    = False     )
    accGroup        = Column(   Integer,                            ForeignKey('productGroups.id') )
    location        = Column(   Unicode(50),                        nullable    = True      )
    quantity        = Column(   Float,          ColumnDefault(0),   nullable    = False     )
    qntyWarning     = Column(   Float,          ColumnDefault(0),   nullable    = True      )
    oversell        = Column(   Boolean,        ColumnDefault(0)                            )
    purchacePrice   = Column(   Float,          ColumnDefault(0),   nullable    = False     )
    sellingPrice    = Column(   Float,          ColumnDefault(0),   nullable    = False     )
    discountFormula = Column(   Unicode(100),                       nullable    = True      )
    productDesc     = Column(   Unicode(200),                       nullable    = True      )
    uMeasurement    = Column(   Unicode(30),                        nullable    = True)

    def __init__(   self,   code,   name,   qntyWarning,   oversell,   location,
                    quantity,   purchacePrice,   sellingPrice,   accGroup,   productDesc,   discountFormula,   uMeasurement  ,id=1  ):
        self.code       = code
        self.name       = name
        self.oversell   = oversell
        self.location   = location
        self.quantity   = quantity
        self.accGroup   = accGroup
        self.productDesc    = productDesc
        self.qntyWarning    = qntyWarning
        self.sellingPrice       = sellingPrice
        self.purchacePrice      = purchacePrice
        self.discountFormula    = discountFormula
        self.uMeasurement       = uMeasurement

## @}
