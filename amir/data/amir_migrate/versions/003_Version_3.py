#!/usr/bin/python2
# -*- coding: utf-8 -*-

from sqlalchemy import *
from migrate import *
import logging

meta = MetaData()
permissions = Table('permissions', meta,
    Column('id',            Integer,      primary_key = True                      ),
    Column('name',          Unicode(50),       nullable = False                   ),
    Column('value',           Unicode(20),  nullable = True                       ),
    mysql_charset='utf8'
)
user = Table('users', meta,
    Column('id',        Integer, primary_key=True),
    Column('code',      String(20), unique=True),
    Column('name',      Unicode(60), nullable=False),
    Column('parent_id',     Integer, ColumnDefault(0), ForeignKey('users.id'), nullable=False),
    Column('lft',       Integer, nullable=False),
    Column('rgt',       Integer, nullable=False),
    Column('type',      Integer),      # 0 for Debtor, 1 for Creditor, 2 for both
    mysql_charset='utf8'
)
def upgrade(migrate_engine):
    # meta = MetaData(bind=migrate_engine)
    meta.bind = migrate_engine
    permissions.create(checkfirst=True)
    

    from sqlalchemy.orm import sessionmaker, scoped_session
    Session = scoped_session(sessionmaker(bind=migrate_engine))
    s = Session()

    s.execute('ALTER TABLE `transactions` RENAME TO `factors`')
    s.execute('ALTER TABLE `factors` ADD COLUMN `Acivated` Boolean DEFAULT 0;')
    s.execute('ALTER TABLE `factors` ADD COLUMN `transPayableAmnt` Float DEFAULT 0;')
    s.execute('ALTER TABLE `factors` ADD COLUMN `PayableAmnt` Float DEFAULT 0;')
    s.execute('ALTER TABLE `factors` ADD COLUMN `LastEdit` Date;')

    factors = Table('factors', meta, autoload=True)
    factors.c.transId.alter(name='Id')
    factors.c.transCode.alter(name='Code')
    factors.c.transDate.alter(name='tDate')
    factors.c.transBill.alter(name='Bill')
    factors.c.transCust.alter(name='Cust')
    factors.c.transAddition.alter(name='Addition')
    factors.c.transSubtraction.alter(name='Subtraction')
    factors.c.transTax.alter(name='VAT')
    factors.c.transCashPayment.alter(name='CashPayment')
    factors.c.transShipDate.alter(name='ShipDate')
    factors.c.transShipVia.alter(name='ShipVia')
    factors.c.transPermanent.alter(name='Permanent')
    factors.c.transDesc.alter(name='Desc')
    factors.c.transSell.alter(name='Sell')
    factors.c.transPayableAmnt.alter(name='Fee')
    factors.c.transFOB.alter(name='Delivery')

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
    s.execute('INSERT INTO factorItems (exchngId, exchngNo, exchngProduct, exchngQnty, exchngUntPrc, exchngUntDisc, exchngTransId, exchngDesc)\
               SELECT exchngId, exchngNo, exchngProduct, exchngQnty, exchngUntPrc, exchngUntDisc, exchngTransId, exchngDesc FROM exchanges;')
    s.execute('DROP TABLE exchanges;')


    factorItems = Table('factorItems', meta, autoload=True)
    factorItems.c.exchngId.alter(name='id')
    factorItems.c.exchngNo.alter(name='number')
    factorItems.c.exchngProduct.alter(name='productId')
    factorItems.c.exchngQnty.alter(name='qnty')
    factorItems.c.exchngUntPrc.alter(name='untPrc')
    factorItems.c.exchngUntDisc.alter(name='untDisc')
    factorItems.c.exchngTransId.alter(name='factorId')
    factorItems.c.exchngDesc.alter(name='desc')

    s.execute('ALTER TABLE `payment` ADD COLUMN `paymntNamePayer` Text;')

    s.execute('ALTER TABLE `Cheque` ADD COLUMN `chqBillId` Integer;')
    s.execute('ALTER TABLE `Cheque` ADD COLUMN `chqOrder` Integer;')
    s.execute('ALTER TABLE `Cheque` ADD COLUMN `chqDelete` Boolean;')

    s.execute('ALTER TABLE `chequehistory` ADD COLUMN `Delete` Boolean;')


    factorItems = Table('factorItems', meta, autoload=True)
    factorItems.c.exchngId.alter(name='id')
    factorItems.c.exchngNo.alter(name='number')

    permissions.create(checkfirst=True)

    s.execute('DROP TABLE users;')
    permissions.create(checkfirst=True)

    s.execute('DELETE FROM config')
    s.commit()
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
        {'cfgId' : 1, 'cfgType' : 1, 'cfgCat' : 0, 'cfgKey' : u'co-name'       , 'cfgValue' : u'Enter Company Name', 'cfgDesc' : u'Enter Company name here'},
        {'cfgId' : 2, 'cfgType' : 0, 'cfgCat' : 0, 'cfgKey' : u'co-logo'       , 'cfgValue' : u'', 'cfgDesc' : u'Select Company logo'},
        {'cfgId' : 3, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : u'custSubject'   , 'cfgValue' : u'4',  'cfgDesc' : u'Enter here'},
        {'cfgId' : 4, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'bank'          , 'cfgValue' : u'1',  'cfgDesc' : u'Enter here'},
        {'cfgId' : 5, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'cash'          , 'cfgValue' : u'3',  'cfgDesc' : u'Enter here'},
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
        {'cfgId' :22, 'cfgType' : 1, 'cfgCat' : 0, 'cfgKey' : u'co-address'    , 'cfgValue' : u'Enter your company address',  'cfgDesc':u'Enter here'},
        {'cfgId' :23, 'cfgType' : 1, 'cfgCat' : 0, 'cfgKey' : u'co-economical-code'    , 'cfgValue' : u'Enter your economical code',  'cfgDesc':u'Enter here'},
        {'cfgId' :24, 'cfgType' : 1, 'cfgCat' : 0, 'cfgKey' : u'co-national-code'    , 'cfgValue' : u'Enter your national code',  'cfgDesc':u'Enter here'},
        {'cfgId' :25, 'cfgType' : 1, 'cfgCat' : 0, 'cfgKey' : u'co-postal-code'    , 'cfgValue' : u'Enter your postal code',  'cfgDesc':u'Enter here'},
        {'cfgId' :26, 'cfgType' : 1, 'cfgCat' : 0, 'cfgKey' : u'co-phone-number'    , 'cfgValue' : u'Enter your phone number',  'cfgDesc':u'Enter here'}
        #{'cfgId' :11, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'fund'          , 'cfgValue' : u'??', 'cfgDesc':u'Enter here'},  #TODO cfgKey
        #{'cfgId' :12, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'acc-receivable', 'cfgValue' : u'??', 'cfgDesc':u'Enter here',}, #TODO cfgKey
        #{'cfgId' :13, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' :u'commission'     , 'cfgValue' : u'??', 'cfgDesc':u'Enter here'}   #TODO cfgKey
    )

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine

    # products.drop()
    # productGroups.drop()
    # factors.drop()
    # factorItems.drop()
    # payments.drop()

    # cheques.drop()
    # custGroups.drop()
    # customers.drop()
    # bankAccounts.drop()
    # config.drop()
    print("downgrade to 2")
    

