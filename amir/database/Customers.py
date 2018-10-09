from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode, Float
from sqlalchemy.ext.declarative import declarative_base

from amir.database import get_declarative_base

Base = get_declarative_base()

## \defgroup DataBase
## @{

#Version 0.2 tables
class Customers(Base):
    __tablename__ = "customers"
    custId          = Column( Integer,      primary_key = True  )
    custCode        = Column( Unicode(15),  unique=True,  nullable = False   )
    custName        = Column( Unicode(100), nullable = False    )
    custSubj        = Column( Integer,      ForeignKey('subject.id'))
    custPhone       = Column( Unicode(15),  nullable = True     )
    custCell        = Column( Unicode(15),  nullable = True     )
    custFax         = Column( Unicode(15),  nullable = True     )
    custAddress     = Column( Unicode(100), nullable = True     )
    custPostalCode  = Column( Unicode(15),  nullable = True     )
    custEmail       = Column( Unicode(15),  nullable = True     )
    custEcnmcsCode  = Column( Unicode(20),  nullable = True     )
    custPersonalCode= Column( Unicode(15),  nullable = True     )
    custWebPage     = Column( Unicode(50),  nullable = True     )
    custResposible  = Column( Unicode(50),  nullable = True     )
    custConnector   = Column( Unicode(50),  nullable = True     )
    custGroup       = Column( Integer,      ForeignKey('custGroups.custGrpId'))
    custDesc        = Column( Unicode(200), nullable = True     )
    custBalance     = Column( Float,        ColumnDefault(0),   nullable = False    )
    custCredit      = Column( Float,        ColumnDefault(0),   nullable = False    )
    custRepViaEmail = Column( Boolean,      ColumnDefault(False),   nullable = False)
    custAccName1    = Column( Unicode(50),  nullable = True)
    custAccNo1      = Column( Unicode(30),  nullable = True)
    custAccBank1    = Column( Unicode(50),  nullable = True)
    custAccName2    = Column( Unicode(50),  nullable = True)
    custAccNo2      = Column( Unicode(30),  nullable = True)
    custAccBank2    = Column( Unicode(50),  nullable = True)
    custTypeBuyer   = Column( Boolean,      ColumnDefault(True),   nullable = False)
    custTypeSeller  = Column( Boolean,      ColumnDefault(True),   nullable = False)
    custTypeMate    = Column( Boolean,      ColumnDefault(False),  nullable = False)
    custTypeAgent   = Column( Boolean,      ColumnDefault(False),  nullable = False)
    custIntroducer  = Column( Integer,      ForeignKey('customers.custId'))
    custCommission  = Column( Unicode(15),  nullable = True )
    custMarked      = Column( Boolean,      ColumnDefault(False),  nullable = False)
    custReason      = Column( Unicode(200), nullable = True )
    custDiscRate    = Column( Unicode(15),  nullable = True )

    def __init__( self, custCode, custName, custSubj, custPhone, custCell, custFax, custAddress,
                  custEmail, custEcnmcsCode, custWebPage, custResposible, custConnector, 
                  custGroup, custPostalCode="", custPersonalCode="", custDesc="", 
                  custRepViaEmail=False, custAccName1="", custAccNo1="", custAccBank1="", custAccName2="", custAccNo2="", 
                  custAccBank2="", custTypeBuyer=True, custTypeSeller=True, custTypeMate=False, custTypeAgent=False, 
                  custIntroducer="", custCommission="", custMarked=False, custReason="", custDiscRate="" , custBalance=float(0), custCredit=float(0)):

        self.custCode        = custCode
        self.custName        = custName    
        self.custSubj        = custSubj
        self.custPhone       = custPhone
        self.custCell        = custCell
        self.custFax         = custFax
        self.custAddress     = custAddress
        self.custPostalCode  = custPostalCode
        self.custEmail       = custEmail
        self.custEcnmcsCode  = custEcnmcsCode
        self.custPersonalCode = custPersonalCode
        self.custWebPage     = custWebPage
        self.custResposible  = custResposible
        self.custConnector   = custConnector
        self.custGroup       = custGroup
        self.custDesc        = custDesc
        self.custBalance     = custBalance
        self.custCredit      = custCredit
        self.custRepViaEmail = custRepViaEmail
        self.custAccName1    = custAccName1
        self.custAccNo1      = custAccNo1
        self.custAccBank1    = custAccBank1
        self.custAccName2    = custAccName2
        self.custAccNo2      = custAccNo2
        self.custAccBank2    = custAccBank2
        self.custTypeBuyer   = custTypeBuyer
        self.custTypeSeller  = custTypeSeller
        self.custTypeMate    = custTypeMate
        self.custTypeAgent   = custTypeAgent
        self.custIntroducer  = custIntroducer
        self.custCommission  = custCommission
        self.custMarked      = custMarked
        self.custReason      = custReason
        self.custDiscRate    = custDiscRate

## @}
