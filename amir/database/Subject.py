from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode, Float
from sqlalchemy.ext.declarative import declarative_base

from amir.database import get_declarative_base
Base = get_declarative_base()

## \defgroup DataBase
## @{

#Version 0.1 tables
class Subject(Base):
    __tablename__ = "subject"
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True)
    name = Column(String(60), nullable=False)
    parent_id = Column(Integer, ColumnDefault(0), ForeignKey('subject.id'), nullable=False)
    lft = Column(Integer, nullable=False)
    rgt = Column(Integer, nullable=False)
    type = Column(Integer)      # 0 for Debtor, 1 for Creditor, 2 for both
    permanent = Column(Boolean, ColumnDefault(False))

    def __init__(self, code=0, name='', parent_id=0, lft=0, rgt=0, type=0 , permanent=0,id=1):
        self.code = code
        self.name = name
        self.parent_id = parent_id
        self.lft = lft
        self.rgt = rgt
        self.type = type
        self.permanent = permanent
## @}
