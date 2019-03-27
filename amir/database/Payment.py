from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode, Float
from sqlalchemy.ext.declarative import declarative_base

from amir.database import get_declarative_base
Base = get_declarative_base()

## \defgroup DataBase
## @{

## Version 0.2 tables


class Payment(Base):
    __tablename__ = "payment"
    paymntId = Column(Integer,                      primary_key=True)
    paymntDueDate = Column(Date,                    nullable=False)
    paymntBank = Column(Unicode(100),               nullable=True)
    paymntSerial = Column(Unicode(50),              nullable=True)
    paymntAmount = Column(Float, ColumnDefault(0),  nullable=False)
#   paymntPayer     = Column( Integer,      ForeignKey('customers.custId')    )
    paymntNamePayer = Column(Unicode(50),           nullable=True)
    paymntWrtDate = Column(Date,                    nullable=True)
    paymntDesc = Column(Unicode(200),               nullable=True)
    # Transaction id is zero for non-invoice payments.
    paymntTransId = Column(Integer, ColumnDefault(0))
    # Bill id is zero for temporary transactions.
    paymntBillId = Column(Integer, ColumnDefault(0))
    paymntTrckCode = Column(Unicode(50),            nullable=True)
    paymntOrder = Column(Integer, ColumnDefault(0), nullable=False)
#    paymntChq       = Column( Integer,      ForeignKey('cheques.chqId')             )

    def __init__(self, paymntDueDate, paymntBank, paymntSerial, paymntAmount,
                 paymntNamePayer, paymntWrtDate, paymntDesc, paymntTransId, paymntBillId,
                 paymntTrckCode, paymntOrder, paymntId=1):

        #self.paymntNo        = paymntNo
        self.paymntDueDate = paymntDueDate
        self.paymntBank = paymntBank
        self.paymntSerial = paymntSerial
        self.paymntAmount = paymntAmount
        self.paymntNamePayer = paymntNamePayer
        self.paymntWrtDate = paymntWrtDate
        self.paymntDesc = paymntDesc
        self.paymntTransId = paymntTransId
        self.paymntBillId = paymntBillId
        self.paymntTrckCode = paymntTrckCode
        self.paymntOrder = paymntOrder

## @}
