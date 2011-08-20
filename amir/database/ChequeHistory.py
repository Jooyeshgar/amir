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
class ChequeHistroy(Base):
    __tablename__ = "cheque"
    chqId       = Column(Integer,      primary_key = True)
    chqSerial   = Column(Unicode(50),  nullable = False)
    chqAccount  = Column(Integer,      ForeignKey('bankAccounts.accId'), nullable = True)
    chqCust     = Column( Integer,      ForeignKey('customers.custId'))
    chqTransId  = Column(Integer,      ColumnDefault(0)) #Transaction id is zero for non-invoice cheques.
    chqBillId   = Column(Integer,      ColumnDefault(0)) #Bill id is zero for temporary transactions.
    chqStatus   = Column(Integer,      ColumnDefault(0), nullable = False)
    chqOrder    = Column(Integer,      ColumnDefault(0), nullable = False)
    chqUpdateDate = Column(Date, nullable=False)

    def __init__( self, chqAmount, chqWrtDate, chqDueDate, chqSerial,
                  chqStatus, chqCust, chqTransId, chqBillId, chqDesc, chqOrder):
        self.chqAmount   = chqAmount
        self.chqSerial   = chqSerial
        self.chqAccount  = chqAccount
        self.chqCust     = chqCust
        self.chqStatus   = chqStatus
        self.chqTransId  = chqTransId
        self.chqBillId   = chqBillId
        self.chqOrder    = chqOrder
        self.chqUpdateDate = chqUpdateDate

## @}
