from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode, Float
from sqlalchemy.ext.declarative import declarative_base

from amir.database import get_declarative_base
Base = get_declarative_base()

## \defgroup DataBase
## @{

#Version 0.1 tables
class Bill(Base):
    __tablename__ = "bill"
    id              = Column(Integer, primary_key=True)
    number          = Column(Integer, nullable = False)
    creation_date   = Column(Date, nullable = False)
    lastedit_date   = Column(Date, nullable = False)
    date            = Column(Date, nullable = False)   #date of transactions in the bill
   # TotalCost       = Column(Float,nullable=False);
    permanent       = Column(Boolean, ColumnDefault(False), nullable = False)
    
    
    def __init__(self, number, creation_date, lastedit_date, date , permanent , id=1 ):
        self.number = number
        self.creation_date = creation_date
        self.lastedit_date = lastedit_date
        self.date = date
        self.permanent = permanent  
      #  self.TotalCost = TotalCost

## @}
