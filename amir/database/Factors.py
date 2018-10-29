from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode, Float
from sqlalchemy.ext.declarative import declarative_base

from amir.database import get_declarative_base
Base = get_declarative_base()

# \defgroup DataBase
# @{

# Version 0.2 tables


class Factors (Base):
    __tablename__ = "factors"
    Id = Column(Integer, primary_key=True)
    Code = Column(Integer, nullable=False)
    tDate = Column(Date, nullable=False)
    Bill = Column(Integer, ColumnDefault(0)) # Bill id is zero for temporary
    Cust = Column(Integer, ForeignKey('customers.custId'))
    Addition = Column(Float, ColumnDefault(0), nullable=False)
    Subtraction = Column(Float, ColumnDefault(0), nullable=False)
    VAT = Column(Float, ColumnDefault(0), nullable=False)
    Fee = Column(Float, ColumnDefault(0), nullable=False)
    PayableAmnt = Column(Float, ColumnDefault(0), nullable=False)
    CashPayment = Column(Float, ColumnDefault(0), nullable=False)
    ShipDate = Column(Date, nullable=True)
    Delivery = Column(Unicode(50), nullable=True) #Place of delivery
    ShipVia = Column(Unicode(100), nullable=True)
    Permanent = Column(Boolean, ColumnDefault(0))
    Desc = Column(Unicode(200), nullable=True)
    Sell = Column(Integer,  nullable=False)
    LastEdit = Column(Date, nullable=True)
    Activated = Column(Boolean, ColumnDefault(0), nullable=False)

    def __init__(self, Code, Date, Bill, Cust, Add, Sub, VAT, Fee, 
                 PayableAmnt, Cash, ShpDate, Delivery, ShipVia, Prmnt,
                 Desc, Sell, LastEdit, Activated):

        self.Code = Code
        self.tDate = Date
        self.Bill = Bill
        self.Cust = Cust
        self.Addition = Add
        self.Subtraction = Sub
        self.VAT = VAT
        self.Fee = Fee
        self.PayableAmnt = PayableAmnt
        self.CashPayment = Cash
        self.ShipDate = ShpDate
        self.Delivery = Delivery
        self.ShipVia = ShipVia
        self.Permanent = Prmnt
        self.Desc = Desc
        self.Sell = Sell
        self.LastEdit = LastEdit
        self.Activated = Activated

# @}
