from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode, Float
from sqlalchemy.ext.declarative import declarative_base

from amir.database import get_declarative_base
Base = get_declarative_base()

## \defgroup DataBase
## @{

#Version 0.2 tables

class Cheque(Base):
    __tablename__ = "Cheque"
    chqId       = Column(Integer,      primary_key = True)
    chqAmount   = Column(Float,        ColumnDefault(0), nullable = False)
    chqWrtDate  = Column(Date,         nullable = False)
    chqDueDate  = Column(Date,         nullable = False)
    chqSerial   = Column(Unicode(50),  nullable = False)
    ## an integer describes cheque status
    #
    # 1 Pardakhti, Vosol nashode
    # 2 Pardakhti, Vosol shode
    # 3 Daryafti, Vosol shode
    # 4 Daryafti, Vosol nashode
    # 5 Kharj shode
    # 6 Odat az moshtari shode
    # 7 Odat be moshtari shode
    # 8 Bargasht shode
    
    chqStatus     = Column(Integer,      ColumnDefault(0), nullable = False)
    #chqOwnerName  = Column(Unicode(200),  nullable=True)
    chqCust       = Column(Integer,      ForeignKey('customers.custId'), nullable=True)    
    chqAccount    = Column(Integer,      ForeignKey('bankAccounts.accId'), nullable = True)
    chqTransId    = Column(Integer,      ColumnDefault(0), ForeignKey('factors.Code')) #Transaction id is zero for non-invoice cheques.
    chqNoteBookId = Column(Integer,      ColumnDefault(0), ForeignKey('notebook.id'))
    chqDesc       = Column(Unicode(200), nullable = True)
    chqHistoryId  = Column(Integer)
    chqBillId     = Column(Integer,      ColumnDefault(0)) #Bill id is zero for temporary transactions.
    chqOrder      = Column(Integer ,     nullable=False)
    chqDelete     = Column(Boolean)

    def __init__( self, chqAmount, chqWrtDate, chqDueDate, chqSerial,
                  chqStatus, chqCust , chqAccount, chqTransId, chqNoteBookId, chqDesc,chqHistoryId ,chqBillId,chqOrder=0,chqDelete=False , chqId=0) :
        if chqId != 0:
            self.chqId = chqId
        self.chqAmount   = chqAmount
        self.chqWrtDate  = chqWrtDate
        self.chqDueDate  = chqDueDate
        self.chqSerial   = chqSerial
        self.chqStatus   = chqStatus
        #self.chqOwnerName= chqOwnerName
        self.chqCust     = chqCust
        self.chqAccount  = chqAccount
        self.chqTransId  = chqTransId
        self.chqNoteBookId = chqNoteBookId
        self.chqDesc     = chqDesc
        self.chqHistoryId = chqHistoryId
        self.chqBillId   = chqBillId
        self.chqOrder    =  chqOrder
        self.chqDelete    =  chqDelete
## @}

