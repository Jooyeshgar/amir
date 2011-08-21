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
    ## ForeignKey Cheque::Cheque::chqId
    ChequeId   = Column(Integer,  nullable = False, ForeignKey('Cheque.chqId'))
    Status   = Column(Integer,      ColumnDefault(0), nullable = False)
    #Cust     = Column( Integer,      ForeignKey('customers.custId'))
    #Account  = Column(Integer,      ForeignKey('bankAccounts.accId'), nullable = True)
    From = None
    To = None
    TransId  = Column(Integer,      ColumnDefault(0)) #Transaction id is zero for non-invoice cheques.
    BillId   = Column(Integer,      ColumnDefault(0)) #Bill id is zero for temporary transactions.
    Order    = Column(Integer,      ColumnDefault(0), nullable = False)
    EditDate     = Column(Date)

    def __init__( self, Id, ChequeSerial, Status, Cust, Account, TransId, BillId, Order, EditDate):
        self.Id = Id
        self.ChequeSerial = ChequeSerial
        self.Status = Status
        self.Cust = Cust
        self.Account = Account
        self.TransId = TransId
        self.BillId = BillId
        self.Order = Order
        self.EditDate = EditDate

## @}

