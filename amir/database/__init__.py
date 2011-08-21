from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from migrate.versioning import exceptions,api
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
from Exchanges import Exchanges
from Notebook import Notebook
from Payment import Payment
from ProductGroups import ProductGroups
from Products import Products
from Subject import Subject
from Transactions import Transactions
from User import User

class Database:
    def __init__(self, file, repository, echoresults):
        self.version = 2
        self.dbfile = file
        self.repository = repository
        
        #migrate code
        try:
            dbversion = api.db_version('sqlite:///%s' % file, self.repository)
            #print dbversion
        except exceptions.DatabaseNotControlledError:
            dbversion = 0
            api.version_control('sqlite:///%s' % file, self.repository, dbversion)
        
        if dbversion < self.version:
            api.upgrade('sqlite:///%s' % file, self.repository, self.version)
        elif  dbversion > self.version:
            api.downgrade('sqlite:///%s' % file, self.repository, self.version)
        
        engine = create_engine('sqlite:///%s' % file , echo=echoresults)
        
        metadata = Base.metadata
        metadata.create_all(engine)
    
        Session = sessionmaker(engine)
        self.session = Session()            
        
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
