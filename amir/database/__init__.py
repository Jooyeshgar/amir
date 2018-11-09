from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from migrate.versioning import api
# metadata = MetaData(bind=engine)

## \defgroup DataBase
## @{

Base = declarative_base()

def get_declarative_base():
    return Base
 
# create tables in database
# metadata.create_all
from BankNames import BankNames
from BankAccounts import BankAccounts
from Bill import Bill
from Cheque import Cheque
from ChequeHistory import ChequeHistory
from Config import Config
from CustGroups import CustGroups
from Customers import Customers
from FactorItems import FactorItems
from Notebook import Notebook
from Payment import Payment
from ProductGroups import ProductGroups
from Products import Products
from Subject import Subject
from Factors import Factors
from User import Users
from Permission import Permissions
import re

class Database:
    def __init__(self, file, repository, echoresults):
        
        #for backward compatibelity
        if re.match('^\w+://', file) == None:
            file = 'sqlite:///'+file   
        
        self.version = 3
        self.dbfile = file
        self.repository = repository
             
        
        #migrate code
        try:
            dbversion = api.db_version(file, self.repository)
            #print dbversion
        except :  # if no previous database found => first installing
            dbversion = 0
            api.version_control(file, self.repository, dbversion)
        
        versioningDone = False

        if dbversion < self.version:
            api.upgrade(file, self.repository, self.version)
            versioningDone = True
        elif  dbversion > self.version:
            api.downgrade(file, self.repository, self.version)
            versioningDone = True
                     
        engine = create_engine(file , echo=False)#edit by hassan : echoresults to True
        self.engine = engine
        
        metadata = Base.metadata
        metadata.create_all(engine)
    
        Session = sessionmaker(engine)
        self.session = Session()  
        if versioningDone:
           self.rebuild_nested_set(0 , 0) 
              
        
    def rebuild_nested_set(self, parent=0, left=0): 
        right = left+1;
        # get all children of this node  
        result = self.session.query(Subject.id).select_from(Subject).filter(Subject.parent_id == parent).all()
        for a in result :
            right = self.rebuild_nested_set(a[0], right);
 
        self.session.query(Subject).filter(Subject.id == parent).update(values = dict(lft = left,rgt = right))
        self.session.commit()
        
        return right+1;

## @}
