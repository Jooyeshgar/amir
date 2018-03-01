# Should be moved to migrate scripts

import sys
import os
import getopt
import re
import logging
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode
from sqlalchemy import exc
from sqlalchemy.sql import select
from sqlalchemy.orm import outerjoin, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import calverter

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
    permanent = Column(Boolean, ColumnDefault(False), nullable = False)
    
    def __init__(self, number, creation_date, lastedit_date, date, permanent):
        self.number = number
        self.creation_date = creation_date
        self.lastedit_date = lastedit_date
        self.date = date
        self.permanent = permanent  
    
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
    def __init__(self, file):
        
        logging.info(file)
        engine = create_engine('sqlite:///%s' % file , echo=True)
        
        metadata = Base.metadata
        metadata.create_all(engine)
        Session = sessionmaker(engine)
        self.session = Session()

def checkInputDb(inputfile):
    try:
        engine = create_engine('sqlite:///%s' % inputfile, echo=True)
    except exc.DatabaseError:
        logging.error(sys.exc_info()[0])
        return -2
    metadata = MetaData(bind=engine)
    
    try:
        table = Table('ledger', metadata, autoload=True)
        table = Table('sub_ledger', metadata, autoload=True)
        table = Table('moin', metadata, autoload=True)
    
    except exc.DatabaseError:
        logging.error(sys.exc_info()[0])
        return -2
    except exc.NoSuchTableError:
        return -1
    return 0
    
def update(inputfile, outputfile):
        
    engine = create_engine('sqlite:///%s' % inputfile, echo=True)
    metadata = MetaData(bind=engine)
    
    outdb =  Database(outputfile)
    outsession = outdb.session
    
    ledger = Table('ledger', metadata,
        Column('id', Integer, primary_key = True),
        Column('name', String),
        Column('type', Integer),
    )
    
    subledger = Table('sub_ledger', metadata,
        Column('ledger', Integer),
        Column('name', String),
        Column('id', Integer, primary_key = True),
        Column('bed', Integer),
        Column('bes', Integer),
    )
    
    moin = Table('moin', metadata,
        Column('sub_name', String),
        Column('ledger', Integer),
        Column('name', String),
        Column('sub', Integer),
        Column('number', Integer),
        Column('date', String),
        Column('des', String),
        Column('bed', Integer),
        Column('bes', Integer),
        Column('mondeh', Integer),
        Column('tashkhis', String),
    )
    metadata.create_all()
    
    
    query = outsession.query(Subject.code).select_from(Subject).order_by(Subject.id.desc())
    code = query.filter(Subject.parent_id == 0).first()
    if code == None :
        lastcode = 0
    else :
        lastcode = int(code[0][-2:])
    
    s = outerjoin(ledger, subledger, ledger.c.id == subledger.c.ledger).select().order_by(ledger.c.id)
    result = s.execute()
    
    parent_id = 0
    pid = 0
    sid = 0
    pcode = ""
    mainids = {}   #stores tuples like (oldid:newid) pairs to have old subject ids for later use
    subids = {}    #stores tuples like (oldid:newid) pairs to have old subject ids for later use
    
    for row in result:
        if row[0] != parent_id:
            lastcode += 1
            if lastcode > 99:
                logging.error("Ledgers with numbers greater than %d are not imported to the new database" \
                      "Because you can have just 99 Ledgers (level one subject)" % row[0])
                break
            pcode = "%02d" % lastcode
            parentsub = Subject(pcode, row[1], 0, 2)
            childcode = 0
            outsession.add(parentsub)
            if pid == 0:
                outsession.commit()
                sid = parentsub.id
            else:
                sid += 1
            pid = sid
            parent_id = row[0]
            mainids[row[0]] = pid
            
        if row[3] != None:
            childcode += 1
            if childcode > 99:
                logging.error("SubLedgers with number %d is not imported to the new database" \
                      "Because you can have just 99 subjects per level" % row[5])
                continue 
            childsub = Subject(pcode + "%02d" % childcode, row[4], pid, 2)
            outsession.add(childsub)
            sid += 1
            subids[row[5]] = sid
     
    outsession.commit()      
        
    s = moin.select().order_by(moin.c.number)
    result = s.execute()
    
    bnumber = 0
    bid = 0
    value = 0
    cal = calverter.calverter()
    
    for row in result:
        if row.number != bnumber:
            
            fields = re.split(r"[:-]+",row.date)
            jd = cal.jalali_to_jd(int(fields[0]), int(fields[1]), int(fields[2]))
            (gyear, gmonth, gday) = cal.jd_to_gregorian(jd)
            ndate = date(gyear, gmonth, gday)
            
            bill = Bill(row.number, ndate, ndate, ndate)
            outsession.add(bill)
            if bid == 0:
                outsession.commit()
                bid = bill.id
            else:
                bid += 1
            bnumber = row.number
        
        if row.sub == 0:
            subid = mainids[row.ledger]
        else:
            subid = subids[row.sub]
        if row.bed == 0:
            value = row.bes
        else:
            value = -(row.bed) 
        n = Notebook(subid, bid, value, row.des)
        outsession.add(n)
    outsession.commit()
        
def main(argv):
    
    inputfile = ""
    outputfile = ""
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["help", "inputfile=", "outputfile="])
    except getopt.GetoptError:
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-i", "--inputfile"):
            inputfile = arg         
        elif opt in ("-o", "--outputfile"):
            outputfile = arg
        elif opt in ("-h", "--help"):
            print("This script converts amir 0.5 databases to the new schema.")
            print("Usage: upgrade.py -i <old database file> -o <new database file>.")
            print("\t Example: upgrade.py -i old.amirdb -o /home/myhome/newdb")
            print("If output file already exists, the script appends new data to it.")
            sys.exit(0)
    
    if inputfile == "":
        #inputfile = "../../1389_01_31.amirdb"
        logging.error("you sholud specify an input database")
        sys.exit(2)
        
    if outputfile == "":
        (filepath, filename) = os.path.split(inputfile)
        outputfile = "../data/" + filename
        logging.info("output file: " + outputfile)
        
    flag = checkInputDb(inputfile)
    if flag < 0:
        logging.error("input database is not compatible with amir v0.5")
        sys.exit(2)
    result = update(inputfile, outputfile)
        
         
        
if __name__ == "__main__":
    
    main(sys.argv[1:])
    
