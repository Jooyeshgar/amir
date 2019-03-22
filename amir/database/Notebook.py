from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, UnicodeText, Float
from sqlalchemy.ext.declarative import declarative_base

from amir.database import get_declarative_base
Base = get_declarative_base()

## \defgroup DataBase
## @{

#Version 0.1 tables
class Notebook(Base):
    __tablename__ = "notebook"
    id            = Column(Integer, primary_key=True)
    subject_id    = Column(Integer, ForeignKey('subject.id'))
    bill_id       = Column(Integer, ForeignKey('bill.id'))
    desc          = Column(UnicodeText, ColumnDefault(""))
    value         = Column(Float, ColumnDefault(0), nullable = False)
    factorId      = Column(Integer, ColumnDefault(0), nullable = False)
    chqId         = Column(Integer, ForeignKey('Cheque.chqId'))

    def __init__(self, subject_id, bill_id, value, desc , factorId=0 ,chqId=0,id=1):
        self.subject_id = subject_id
        self.bill_id = bill_id
        self.value = value
        self.desc = desc
        self.factorId = factorId
        self.chqId = chqId

## @}
