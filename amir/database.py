from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
 
# metadata = MetaData(bind=engine)
 
# create tables in database
# metadata.create_all
Base = declarative_base()
 
class Subject(Base):
    __tablename__ = "subject"
    id = Column(Integer, primary_key=True)
    code = Column(String(20), nullable=False)
    name = Column(Unicode(60), nullable=False)
    parent_id = Column(Integer, ColumnDefault(0), ForeignKey('subject.id'), nullable=False)
    lft = Column(Integer, nullable=False)
    rgt = Column(Integer, nullable=False)
    type = Column(Integer)      # 0 for Debtor, 1 for Creditor, 2 for both
    
    def __init__(self, code, name, parent_id, left, right, type):
        self.code = code
        self.name = name
        self.parent_id = parent_id
        self.lft = left
        self.rgt = right
        self.type = type

class Bill(Base):
    __tablename__ = "bill"
    id = Column(Integer, primary_key=True)
    number = Column(Integer, nullable = False)
    creation_date = Column(Date, nullable = False)
    lastedit_date = Column(Date, nullable = False)
    date = Column(Date, nullable = False)   #date of transactions in the bill
    
    def __init__(self, number, creation_date, lastedit_date, date):
        self.number = number
        self.creation_date = creation_date
        self.lastedit_date = lastedit_date
        self.date = date    
    
class Notebook(Base):
    __tablename__ = "notebook"
    id = Column(Integer, primary_key=True)
    subject_id = Column(None, ForeignKey('subject.id'))
    bill_id = Column(None, ForeignKey('bill.id'))
    desc = Column(Unicode, ColumnDefault(""))
    value = Column(Integer, ColumnDefault(0), nullable = False)
    
    def __init__(self, subject_id, bill_id, value, desc):
        self.subject_id = subject_id
        self.bill_id = bill_id
        self.value = value
        self.desc = desc

class Database:
    def __init__(self, file, echoresults):
        
        self.dbfile = file
        engine = create_engine('sqlite:///%s' % file , echo=echoresults)
        
        metadata = Base.metadata
        metadata.create_all(engine)
    
        Session = sessionmaker(engine)
        self.session = Session()
