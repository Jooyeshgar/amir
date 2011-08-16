from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode, Float
from sqlalchemy.ext.declarative import declarative_base

from amir.database import get_declarative_base
Base = get_declarative_base()

## \defgroup DataBase
## @{

#Version 0.2 tables
class Config(Base):
    __tablename__  = "config"
    cfgId          = Column(Integer, primary_key = True)
    cfgKey         = Column(Unicode(100), nullable = False, unique = True)
    cfgValue       = Column(Unicode(100), nullable = False)
    cfgDesc        = Column(Unicode(100), nullable = True)
    cfgType        = Column(Integer     , nullable = True)
    cfgCat         = Column(Integer     , nullable = True)
    
    def __init__(self, cfgKey, cfgValue, cfgDesc, cfgType, cfgCat):
        self.cfgKey   = cfgKey
        self.cfgValue = cfgValue
        self.cfgDesc  = cfgDesc
        self.cfgType  = cfgType
        self.cfgCat   = cfgCat

## @}
