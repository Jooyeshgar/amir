from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode, Float
from sqlalchemy.ext.declarative import declarative_base

from amir.database import get_declarative_base
Base = get_declarative_base()

## \defgroup DataBase
## @{

#Version 0.2 tables

class ChequeHistory(Base):
    __tablename__ = "ChequeHistory"
    Id       = Column(Integer,      primary_key = True)
    ChequeId   = Column(Integer, ForeignKey('Cheque.chqId'))
    Amount   = Column(Float,        ColumnDefault(0), nullable = False)
    WrtDate  = Column(Date,         nullable = False)
    DueDate  = Column(Date,         nullable = False)
    Serial   = Column(Unicode(50),  nullable = False)
    Status   = Column(Integer,      ColumnDefault(0), nullable = False)
    Cust     = Column(Integer,      ForeignKey('customers.custId'))
    Account  = Column(Integer,      ForeignKey('bankAccounts.accId'), nullable = True)
    TransId  = Column(Integer,      ColumnDefault(0)) #Transaction id is zero for non-invoice cheques.
    Desc     = Column(Unicode(200), nullable = True)
    Date     = Column(Date, nullable=False)
    Delete   = Column(Boolean)

    def __init__( self, ChequeId, Amount, WrtDate, DueDate, Serial,
                  Status, Cust, Account, TransId, Desc, Date, Delete = False):
        self.ChequeId = ChequeId
        self.Amount   = Amount
        self.WrtDate  = WrtDate
        self.DueDate  = DueDate
        self.Serial   = Serial
        self.Status   = Status
        self.Cust     = Cust
        self.Account  = Account
        self.TransId  = TransId
        self.Desc     = Desc
        self.Date     = Date
        self.Delete   = Delete

## @}

