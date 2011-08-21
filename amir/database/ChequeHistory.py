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
    Id = Column(Integer,      primary_key = True)
    ChequeId = Column(Unicode(50),  nullable = False, primary_key('Cheque.chqId')
    Account  = Column(Integer  ,      ForeignKey('bankAccounts.accId'), nullable = True)
    Cust     = Column( Integer,      ForeignKey('customers.custId'))
    TransId  = Column(Integer,      ColumnDefault(0)) #Transaction id is zero for non-invoice cheques.
    BillId   = Column(Integer,      ColumnDefault(0)) #Bill id is zero for temporary transactions.
    Status   = Column(Integer,      ColumnDefault(0), nullable = False)
    Order    = Column(Integer,      ColumnDefault(0), nullable = False)
    UpdateDate = Column(Date, nullable=False)

    def __init__( self, ChequeId, Account, Cust, TransId, BillId, Status, Order, UpdateDate):
        self.ChequeId = ChequeId
        self.Account = Account
        self.Cust = Cust
        self.TransId = TransId
        self.BillId = BillId
        self.Status = Status
        self.Order - Order
        self.UpdateDate = UpdateDate

## @}
