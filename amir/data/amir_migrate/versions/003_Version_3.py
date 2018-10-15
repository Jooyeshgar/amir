#!/usr/bin/python2
# -*- coding: utf-8 -*-

from sqlalchemy import *
from migrate import *
import logging
from migrate.changeset.constraint import ForeignKeyConstraint


def _2to3digits(num):
    _3digit = ""
    i = 0 
    while i< len(num )- 1 :
        _3digit = "0" + num[len(num) - i - 2 ] + num [len(num) - i - 1] + _3digit
        i += 2
    return _3digit

meta = MetaData()
permissions = Table('permissions', meta,
    Column('id',            Integer,      primary_key = True                      ),
    Column('name',          Unicode(50),       nullable = False                   ),
    Column('value',           Unicode(20),  nullable = True                       ),
    mysql_charset='utf8'
)

def upgrade(migrate_engine):
    # meta = MetaData(bind=migrate_engine)
    meta.bind = migrate_engine
    from sqlalchemy.orm import sessionmaker, scoped_session
    Session = scoped_session(sessionmaker(bind=migrate_engine))
    s = Session()

    subject = Table('subject', meta, autoload=True)    
   # s.query(subject).update({subject.c.code: _2to3digits(subject.c.code)})      #TODO try this instead of raw sql command
    query = s.query(subject)
    al = query.all()
    for subj in al :       
        #query.filter(subject.c.id == subj.id).update({subject.c.code : _2to3digits(subj.code)})    # TODO       try this instead of raw sql command
        s.execute("update subject set code = '"+ str(_2to3digits(subj.code))+"' where id ="+str(subj.id) + ";")
    s.commit()

    s.execute('CREATE TABLE factors (\
                "Id" INTEGER NOT NULL, \
                "Code" VARCHAR(50) NOT NULL, \
                "tDate" DATE NOT NULL, \
                "Bill" INTEGER, \
                "Cust" INTEGER, \
                "Addition" FLOAT NOT NULL, \
                "Subtraction" FLOAT NOT NULL, \
                "VAT" FLOAT NOT NULL, \
                "CashPayment" FLOAT NOT NULL, \
                "ShipDate" DATE, \
                "Delivery" VARCHAR(50), \
                "ShipVia" VARCHAR(100), \
                "Permanent" BOOLEAN, \
                "Desc" VARCHAR(200), \
                "Sell" BOOLEAN, \
                "Activated" BOOLEAN DEFAULT 0, \
                "Fee" FLOAT DEFAULT 0, \
                "PayableAmnt" FLOAT DEFAULT 0, \
                "LastEdit" DATE, \
                PRIMARY KEY ("Id"), \
                CHECK ("Permanent" IN (0, 1)), \
                CHECK ("Sell" IN (0, 1)), \
                CHECK ("Activated" IN (0, 1)), \
                FOREIGN KEY("Cust") REFERENCES customers ("custId") \
            );')
    s.commit()
    s.execute('INSERT INTO factors (Id, Code, tDate, Bill, Cust, Addition, Subtraction, VAT, CashPayment, ShipDate, Permanent, `Desc`, Sell, Activated, Fee, PayableAmnt, LastEdit)\
               SELECT transId, transCode, transDate, transBill, transCust, transAddition, transSubtraction, transTax, transCashPayment, transShipDate, transPermanent,  transDesc, transSell, 0, 0, 0, 0 FROM transactions;')
    s.execute('DROP TABLE transactions;')
    s.commit()

    s.execute('CREATE TABLE factorItems ( \
                "exchngId" INTEGER NOT NULL, \
                "exchngNo" INTEGER NOT NULL, \
                "exchngProduct" INTEGER, \
                "exchngQnty" FLOAT NOT NULL, \
                "exchngUntPrc" FLOAT NOT NULL, \
                "exchngUntDisc" VARCHAR(30) NOT NULL, \
                "exchngTransId" INTEGER, \
                "exchngDesc" VARCHAR(200), \
                PRIMARY KEY ("exchngId"), \
                FOREIGN KEY("exchngProduct") REFERENCES products (id), \
                FOREIGN KEY("exchngTransId") REFERENCES factors ("Id")\
            );')
    s.commit()
    s.execute('INSERT INTO factorItems (exchngId, exchngNo, exchngProduct, exchngQnty, exchngUntPrc, exchngUntDisc, exchngTransId, exchngDesc)\
               SELECT exchngId, exchngNo, exchngProduct, exchngQnty, exchngUntPrc, exchngUntDisc, exchngTransId, exchngDesc FROM exchanges;')
    s.execute('DROP TABLE exchanges;')
    s.commit()

    s.execute('ALTER TABLE `Cheque` ADD COLUMN `chqDelete` Boolean;')
    s.commit()
    # s.execute('ALTER TABLE `chequehistory` ADD COLUMN `Delete` Boolean;')
    # s.commit()
    s.execute('DROP TABLE users;')
    s.commit()
    s.execute('DELETE FROM config')
    s.commit()

    s.execute('ALTER TABLE `products` ADD COLUMN `uMeasurement`  Text;')

    notebook = Table('notebook', meta, autoload=True)
    colFactor = Column('factorId' , Integer, default =0)
    colFactor.create(notebook ,  populate_default=True)
    assert colFactor is notebook.c.factorId
    colChq = Column('chqId' , Integer, default =0)
    colChq.create(notebook ,  populate_default=True)
    assert colChq is notebook.c.chqId
    notebook.c.value.alter(type=Float)
    assert notebook.c.value.type

    factorItems = Table('factorItems', meta, autoload=True)
    factorItems.c.exchngId.alter(name='id')
    factorItems.c.exchngNo.alter(name='number')
    factorItems.c.exchngProduct.alter(name='productId')
    factorItems.c.exchngQnty.alter(name='qnty')
    factorItems.c.exchngUntPrc.alter(name='untPrc')
    factorItems.c.exchngUntDisc.alter(name='untDisc')
    factorItems.c.exchngTransId.alter(name='factorId')
    factorItems.c.exchngDesc.alter(name='desc')

    permissions.create(checkfirst=True)

    cheque = Table('cheque', meta, autoload=True)
    factors = Table('factors', meta, autoload=True)    
    cons = ForeignKeyConstraint ([cheque.c.chqTransId] , [factors.c.Id])
    notebook = Table('notebook', meta , autoload=True)
    cons = ForeignKeyConstraint ([notebook.c.chqId] , [cheque.c.chqId])

    config = Table('config', meta, autoload=True)
    op = config.insert()
    op.execute(
        # cfg Cat
        # 0 : Company
        # 1 : Subjects
        # 2 : others
        #
        # cfg Type
        # 0 : File Chooser
        # 1 : Entry
        # 2 : Entry (Single Int from Subjects)
        # 3 : Entry (Multi  Int from Subjects)
        {'cfgId' : 1, 'cfgType' : 1, 'cfgCat' : 0, 'cfgKey' : u'co-name'       , 'cfgValue' : u'Company Name', 'cfgDesc' : u'Your company name'},
        {'cfgId' : 2, 'cfgType' : 0, 'cfgCat' : 0, 'cfgKey' : u'co-logo'       , 'cfgValue' : u'', 'cfgDesc' : u'Select your company logo'},
        {'cfgId' : 3, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : u'custSubject'   , 'cfgValue' : u'4',  'cfgDesc' : u'Enter here'},
        {'cfgId' : 4, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'bank'          , 'cfgValue' : u'1',  'cfgDesc' : u'Enter here'},
        {'cfgId' : 5, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'cash'          , 'cfgValue' : u'14',  'cfgDesc' : u'Enter here'},
        {'cfgId' : 6, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'buy'           , 'cfgValue' : u'17', 'cfgDesc':u'Enter here'},
        {'cfgId' : 7, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : u'buy-discount'  , 'cfgValue' : u'53', 'cfgDesc':u'Enter here'},
        {'cfgId' : 8, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'sell'          , 'cfgValue' : u'18', 'cfgDesc':u'Enter here'},
        {'cfgId' : 9, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : u'sell-discount' , 'cfgValue' : u'55', 'cfgDesc':u'Enter here'},
        {'cfgId' :10, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : u'sell-vat'      , 'cfgValue' : u'41', 'cfgDesc':u'Accounting code of sell VAT'},
        {'cfgId' :11, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : u'buy-vat'       , 'cfgValue' : u'40', 'cfgDesc':u'Accounting code of buy VAT'},
        {'cfgId' :12, 'cfgType' : 1, 'cfgCat' : 1, 'cfgKey' : u'vat-rate'      , 'cfgValue' : u'6',  'cfgDesc':u'Percentage of VAT'},
        {'cfgId' :13, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : u'sell-fee'      , 'cfgValue' : u'57', 'cfgDesc':u'Accounting code of sell fee'},
        {'cfgId' :14, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : u'buy-fee'       , 'cfgValue' : u'56', 'cfgDesc':u'Accounting code of buy fee'},
        {'cfgId' :15, 'cfgType' : 1, 'cfgCat' : 1, 'cfgKey' : u'fee-rate'      , 'cfgValue' : u'3',  'cfgDesc':u'Percentage of fee'},
        {'cfgId' :16, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'partners'      , 'cfgValue' : u'8',  'cfgDesc':u'Enter here'},
        {'cfgId' :17, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'cost'          , 'cfgValue' : u'2',  'cfgDesc':u'Enter here'},
        {'cfgId' :18, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : u'bank-wage'     , 'cfgValue' : u'31', 'cfgDesc':u'Enter here'},
        {'cfgId' :19, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'our_cheque'    , 'cfgValue' : u'22', 'cfgDesc':u'Enter here'},
        {'cfgId' :20, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'other_cheque'  , 'cfgValue' : u'6',  'cfgDesc':u'Enter here'},
        {'cfgId' :21, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'income'        , 'cfgValue' : u'83', 'cfgDesc':u'Enter here'},
        {'cfgId' :22, 'cfgType' : 1, 'cfgCat' : 0, 'cfgKey' : u'co-address'    , 'cfgValue' : u'company address (set from settings->confug) ',  'cfgDesc':u'your company address'},
        {'cfgId' :23, 'cfgType' : 1, 'cfgCat' : 0, 'cfgKey' : u'co-economical-code'     , 'cfgValue' : u'economical code ',  'cfgDesc':u'Your economical code'},
        {'cfgId' :24, 'cfgType' : 1, 'cfgCat' : 0, 'cfgKey' : u'co-national-code'       , 'cfgValue' : u'national code ',  'cfgDesc':u'Your national code'},
        {'cfgId' :25, 'cfgType' : 1, 'cfgCat' : 0, 'cfgKey' : u'co-postal-code'         , 'cfgValue' : u'postal code ',  'cfgDesc':u'Your postal code'},
        {'cfgId' :26, 'cfgType' : 1, 'cfgCat' : 0, 'cfgKey' : u'co-phone-number'        , 'cfgValue' : u'phone number ',  'cfgDesc':u'Your phone number'},
        {'cfgId' :27, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : u'sell-adds'              , 'cfgValue' : u'36',  'cfgDesc':u'Additions when selling'},
        {'cfgId' :28, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : u'buy-adds'               , 'cfgValue' : u'32',  'cfgDesc':u'Additions when buying'},
        {'cfgId' :29, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : u'inventories'            , 'cfgValue' : u'69',  'cfgDesc':u'Initial inventory'},
        {'cfgId' :30, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : u'fund'                   , 'cfgValue' : u'21',  'cfgDesc':u'Share capital'}
    )



def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine
    # TODO 

    logging.debug("downgrade to 2")
    

