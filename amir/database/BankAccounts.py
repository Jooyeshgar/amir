from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode, Float
from sqlalchemy.ext.declarative import declarative_base

from amir.database import get_declarative_base
Base = get_declarative_base()

## \defgroup DataBase
## @{

#Version 0.2 tables
class BankAccounts(Base):
    __tablename__   = "bankAccounts"
    accId           = Column( Integer,      primary_key = True  )
    accName         = Column( Unicode(100), nullable = False    )
    accNumber       = Column( Unicode(40) , nullable = False, unique=True)
    accType         = Column( Integer,       nullable = True     )
    accOwner        = Column( Unicode(50),  nullable = True     )
    accBank         = Column( Integer,  ForeignKey('BankNames.Id'), nullable = True     )
    accBankBranch   = Column( Unicode(50),  nullable = True     )
    accBankAddress  = Column( Unicode(100), nullable = True     )
    accBankPhone    = Column( Unicode(40),  nullable = True     )
    accBankWebPage  = Column( Unicode(100),       nullable = True     )
    accDesc         = Column( Unicode(200), nullable = True     )

    def __init__( self, accName, accNumber, accType, accOwner, accBank, accBankBranch,
                  accBankAddress, accBankPhone, accBankWebPage, accDesc , accId=1 ):

        self.accName        = accName
        self.accNumber      = accNumber
        self.accType        = accType
        self.accOwner       = accOwner
        self.accBank        = accBank
        self.accBankBranch  = accBankBranch
        self.accBankAddress = accBankAddress
        self.accBankPhone   = accBankPhone
        self.accBankWebPage = accBankWebPage   #TODO change to unicode
        self.accDesc        = accDesc

## @}
