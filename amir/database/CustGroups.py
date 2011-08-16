from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode, Float
from sqlalchemy.ext.declarative import declarative_base

from amir.database import get_declarative_base
Base = get_declarative_base()

## \defgroup DataBase
## @{

#Version 0.2 tables
class CustGroups(Base):
    __tablename__ = "custGroups"
    custGrpId   = Column( Integer,      primary_key = True  )
    custGrpCode = Column( String(20),       nullable = False    )
    custGrpName = Column( Unicode(50),  nullable = False    )
    custGrpDesc = Column( Unicode(200), nullable = True     )

    def __init__( self, custGrpCode, custGrpName, custGrpDesc    ):

        self.custGrpCode    = custGrpCode
        self.custGrpName    = custGrpName
        self.custGrpDesc    = custGrpDesc

## @}
