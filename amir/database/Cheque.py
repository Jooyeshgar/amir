from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode, Float
from sqlalchemy.ext.declarative import declarative_base

from amir.database import get_declarative_base
Base = get_declarative_base()

## \defgroup DataBase
## @{

#Version 0.2 tables

## TODO: Problems!
class Cheque(Base):
    __tablename__ = "cheque"
    chqId       = Column(Integer,      primary_key = True)
    chqAmount   = Column(Float,        ColumnDefault(0), nullable = False)
    chqWrtDate = Column(Date,         nullable = False)
    chqDueDate  = Column(Date,         nullable = False)
    chqAccount  = Column(Integer,      ForeignKey('bankAccounts.accId'), nullable = True)
    chqSerial   = Column(Unicode(50),  nullable = False)
    chqStatus   = Column(Integer,      ColumnDefault(0), nullable = False)
    chqCust     = Column( Integer,      ForeignKey('customers.custId'))
    chqTransId  = Column(Integer,      ColumnDefault(0)) #Transaction id is zero for non-invoice cheques.
    chqBillId   = Column(Integer,      ColumnDefault(0)) #Bill id is zero for temporary transactions.
    chqDesc     = Column(Unicode(200), nullable = True)
    chqOrder    = Column(Integer,      ColumnDefault(0), nullable = False)

    def __init__( self, chqAmount, chqWrtDate, chqDueDate, chqSerial,
                  chqStatus, chqCust, chqTransId, chqBillId, chqDesc, chqOrder):

        self.chqAmount   = chqAmount
        self.chqWrtDate  = chqWrtDate
        self.chqDueDate  = chqDueDate
        #self.chqBank     = chqBank
        self.chqSerial   = chqSerial
        self.chqStatus   = chqStatus
        #self.chqPaid     = chqPaid
        self.chqCust     = chqCust
        #self.chqSpent    = chqSpent
        self.chqTransId  = chqTransId
        self.chqBillId   = chqBillId
        self.chqDesc     = chqDesc
        self.chqOrder    = chqOrder

## @}
