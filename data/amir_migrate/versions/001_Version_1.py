from sqlalchemy import *
from migrate import *
import logging

meta = MetaData()

#New tables (version 1):
subject = Table('subject', meta,
    Column('id', Integer, primary_key=True),
    Column('code', String(20), nullable=False),
    Column('name', Unicode(60), nullable=False),
    Column('parent_id', Integer, ColumnDefault(0), ForeignKey('subject.id'), nullable=False),
    Column('lft', Integer, nullable=False),
    Column('rgt', Integer, nullable=False),
    Column('type', Integer)
)

bill = Table('bill', meta,
    Column('id', Integer, primary_key=True),
    Column('number', Integer, nullable = False),
    Column('creation_date', Date, nullable = False),
    Column('lastedit_date', Date, nullable = False),
    Column('date', Date, nullable = False),
    Column('permanent', Boolean, ColumnDefault(False), nullable = False)
)

notebook = Table('notebook', meta,
    Column('id', Integer, primary_key=True),
    Column('subject_id', Integer, ForeignKey('subject.id')),
    Column('bill_id', Integer, ForeignKey('bill.id')),
    Column('desc', Unicode, ColumnDefault("")),
    Column('value', Integer, ColumnDefault(0), nullable = False)
)

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata
    meta.bind = migrate_engine
    
    subject.create(checkfirst=True)
    bill.create(checkfirst=True)
    notebook.create(checkfirst=True)
    
    logging.debug("upgrade to 1")
   

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    logging.debug("downgrade to 0")
