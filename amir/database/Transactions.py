from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode, Float
from sqlalchemy.ext.declarative import declarative_base

from amir.database import get_declarative_base
Base = get_declarative_base()

## \defgroup DataBase
## @{

#Version 0.2 tables
class Transactions(Base):
    __tablename__ = "transactions"
    transId         = Column( Integer,      primary_key = True                      )
    transCode       = Column( Unicode(50),  nullable = False                        )
    transDate       = Column( Date,         nullable = False                        ) 
    transBill       = Column( Integer,      ColumnDefault(0)                        ) #Bill id is zero for temporary transactions
    transCust       = Column( Integer,      ForeignKey('customers.custId')          )
    transAddition   = Column( Float,        ColumnDefault(0),   nullable = False    )
    transSubtraction= Column( Float,        ColumnDefault(0),   nullable = False    )
    transTax        = Column( Float,        ColumnDefault(0),   nullable = False    )
    transPayableAmnt= Column( Float,        ColumnDefault(0),   nullable = False    )
    transCashPayment= Column( Float,        ColumnDefault(0),   nullable = False    )
    transShipDate   = Column( Date,         nullable = True                         )
    transFOB        = Column( Unicode(50),  nullable = True                         )
    transShipVia    = Column( Unicode(100), nullable = True                         )
    transPermanent  = Column( Boolean,      ColumnDefault(0)                        )
    transDesc       = Column( Unicode(200), nullable = True                         )
    transSell       = Column( Boolean,      ColumnDefault(0),   nullable = False    )
#    transLastEdit   = Column( Date,         nullable = True                         )

    def __init__( self, transCode, transDate, transBill, transCust, transAdd, transSub, 
                  transTax,transPayableAmnt, transCash, transShpDate, transFOB, transShipVia, transPrmnt, 
                  transDesc, transSell ):#, transSell, transLastEdit ):

        self.transCode          = transCode
        self.transDate          = transDate
        self.transBill          = transBill
        self.transCust          = transCust
        self.transAddition      = transAdd
        self.transSubtraction   = transSub
        self.transTax           = transTax
        self.transPayableAmnt   = transPayableAmnt
        self.transCashPayment   = transCash
        self.transShipDate      = transShpDate
        self.transFOB           = transFOB
        self.transShipVia       = transShipVia
        self.transPermanent     = transPrmnt
        self.transDesc          = transDesc
        self.transSell          = transSell
#        self.transLastEdit      = transLastEdit

## @}
