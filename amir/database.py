from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean
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
    name = Column(String(60), nullable=False)
    parent_id = Column(Integer, ColumnDefault(0), ForeignKey('subject.id'), nullable=False)
    type = Column(Integer)      # 0 for Debtor, 1 for Creditor, 2 for both
    
    def __init__(self, code, name, parent_id, type):
        self.code = code
        self.name = name
        self.parent_id = parent_id
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
    desc = Column(String, ColumnDefault(""))
    value = Column(Integer, ColumnDefault(0), nullable = False)
    
    def __init__(self, subject_id, bill_id, value, desc):
        self.subject_id = subject_id
        self.bill_id = bill_id
        self.value = value
        self.desc = desc

class Database:
    def __init__(self):
        print ("db constructed")
        engine = create_engine('sqlite:///../data/tutorial.db', echo=True)
        metadata = Base.metadata
        metadata.create_all(engine)
    #--------------------------------------------------------------------------
    # create a database connection
    # conn = engine.connect()
    # add user to database by executing SQL
    # conn.execute(users_table.insert(), [
    #    {"name": "Ted", "age":10, "password":"dink"},
    #    {"name": "Asahina", "age":25, "password":"nippon"},
    #    {"name": "Evan", "age":40, "password":"macaca"}
    #])
    
        Session = sessionmaker(engine)
        self.session = Session()
        
        #=======================================================================
        # user_goli = User("goli",18,"nmvcn")
        # self.session.add(user_goli)
        # self.session.commit()
        # 
        # user_sheri = User("shahrzad", 24, "fhkss")
        # self.session.add(user_sheri)
        # 
        # all_users = self.session.query(User).all()
        # for user in all_users :
        #    user.age = user.age + 3;
        #    
        # self.session.commit()
        #=======================================================================
        # s = select([users_table.c.name], users_table.c.age>10)
        # res = conn.execute(s)
        # rows = res.fetchall()
        # for row in rows :
        #     print row.name, "is old enough."
try:
    db
except NameError:
    db = Database()

