#!/usr/bin/python2
# -*- coding: utf-8 -*-

from sqlalchemy import *
from migrate import *
import logging

meta = MetaData()

#subject table (version 1 and 2):
subject = Table('subject', meta,
    Column('id', Integer, primary_key=True),
    Column('code', Unicode(20), nullable=False, unique=True),
    Column('name', Unicode(60), nullable=False),
    Column('parent_id', Integer, ColumnDefault(0), ForeignKey('subject.id'), nullable=False),
    Column('lft', Integer, nullable=False),
    Column('rgt', Integer, nullable=False),
    Column('type', Integer),
    mysql_charset='utf8'
)

#New tables (version 2):
products = Table('products', meta,
    Column('id',              Integer,                            primary_key = True      ),
    Column('code',            Unicode(20),                        nullable    = False     ),
    Column('name',            Unicode(60),                        nullable    = False     ),
    Column('accGroup',        Integer,        ForeignKey('productGroups.id')                     ),
    Column('location',        Unicode(50),                        nullable    = True      ),
    Column('quantity',        Float,          ColumnDefault(0),   nullable    = False     ),
    Column('qntyWarning',     Float,          ColumnDefault(0),   nullable    = True      ),
    Column('oversell',        Boolean,        ColumnDefault(0)                            ),
    Column('purchacePrice',   Float,          ColumnDefault(0),   nullable    = False     ),
    Column('sellingPrice',    Float,          ColumnDefault(0),   nullable    = False     ),
    Column('discountFormula', Unicode(100),                       nullable    = True      ),
    Column('productDesc',     Unicode(200),                       nullable    = True      ),
    mysql_charset='utf8'
)

productGroups = Table('productGroups', meta,
    Column('id',           Integer,        primary_key = True      ),
    Column('code',         String(20),     nullable    = False     ),
    Column('name',         Unicode(60),    nullable    = False     ),
    Column('buyId',        Integer,        ForeignKey('subject.id')),
    Column('sellId',       Integer,        ForeignKey('subject.id')),
    mysql_charset='utf8'
)
    
transactions = Table('transactions', meta,
    Column('transId',            Integer,      primary_key = True                      ),
    Column('transCode',          Unicode(50),       nullable = False                        ),
    Column('transDate',          Date,         nullable = False                        ),
    Column('transBill',          Integer,      ColumnDefault(0)                        ),
    Column('transCust',          Integer,      ForeignKey('customers.custId')          ),
    Column('transAddition',      Float,        ColumnDefault(0),   nullable = False    ),
    Column('transSubtraction',   Float,        ColumnDefault(0),   nullable = False    ),
    Column('transTax',           Float,        ColumnDefault(0),   nullable = False    ),
    Column('transCashPayment',   Float,        ColumnDefault(0),   nullable = False    ),
    Column('transShipDate',      Date,         nullable = True                         ),
    Column('transFOB',           Unicode(50),  nullable = True                         ),
    Column('transShipVia',       Unicode(100), nullable = True                         ),
    Column('transPermanent',     Boolean,      ColumnDefault(0)                        ),
    Column('transDesc',          Unicode(200), nullable = True                         ),
    Column('transSell',          Boolean,      ColumnDefault(0)                        ),
#    Column('transLastEdit',      Date,         nullable = True                         )
    mysql_charset='utf8'
)

exchanges = Table('exchanges', meta,
    Column('exchngId',          Integer,        primary_key = True                      ),
    Column('exchngNo',          Integer,        nullable = False                        ),
    Column('exchngProduct',     Integer,        ForeignKey('products.id')               ),
    Column('exchngQnty',        Float,          ColumnDefault(0),   nullable = False    ),
    Column('exchngUntPrc',      Float,          ColumnDefault(0),   nullable = False    ),
    Column('exchngUntDisc',     Unicode(30),    ColumnDefault("0"), nullable = False    ),
    Column('exchngTransId',     Integer,        ForeignKey('transactions.transId')      ),
    Column('exchngDesc',        Unicode(200),   nullable = True                         ),
    mysql_charset='utf8'
)

payments = Table('payment', meta,
    Column('paymntId',          Integer,      primary_key = True                      ),
    #Column('paymntNo',          Integer,      nullable = False                        ),
    Column('paymntDueDate',     Date,         nullable = False                        ),
    Column('paymntBank',        Unicode(100), nullable = True                         ),
    Column('paymntSerial',      Unicode(50),  nullable = True                         ),
    Column('paymntAmount',      Float,        ColumnDefault(0),   nullable = False    ),
    Column('paymntPayer',       Integer,      ForeignKey('customers.custId')          ),
    Column('paymntWrtDate',     Date,         nullable = True                         ),
    Column('paymntDesc',        Unicode(200), nullable = True                         ),
    Column('paymntTransId',     Integer,      ColumnDefault(0)                        ),
    Column('paymntBillId',      Integer,      ColumnDefault(0)                        ),
    Column('paymntTrckCode',    Unicode(50),  nullable = True                         ),
    Column('paymntOrder',       Integer,      ColumnDefault(0),   nullable = False    ),
#    Column('paymntChq',         Unicode,      nullable = True                         )
    mysql_charset='utf8'
)

cheque = Table('Cheque', meta,
    Column('chqId',          Integer,      primary_key = True                      ),
    Column('chqAmount',      Float,        ColumnDefault(0),                  nullable = False ),
    Column('chqWrtDate',     Date,         nullable = False                        ),
    Column('chqDueDate',     Date,         nullable = False                        ),
    Column('chqSerial',      Unicode(50),  nullable = False                        ),
    Column('chqStatus',      Integer,      ColumnDefault(0),   nullable = False    ),
    Column('chqCust',        Integer,      ForeignKey('customers.custId')          ),
    Column('chqAccount',     Integer,      ForeignKey('bankAccounts.accId'),  nullable = True  ),
    Column('chqTransId',     Integer,      ColumnDefault(0)                        ),
    Column('chqNoteBookId', Integer, ColumnDefault(0), ForeignKey('notebook.id')),
    Column('chqDesc',        Unicode(200), nullable = True                         ),
    Column('chqHistoryId',   Integer,      nullable = True                         ),
    mysql_charset='utf8'
)
    
custGroups = Table('custGroups', meta,
    Column('custGrpId',      Integer,      primary_key = True  ),
    Column('custGrpCode',    Unicode(50),  nullable = False    ),
    Column('custGrpName',    Unicode(50),  nullable = False    ),
    Column('custGrpDesc',    Unicode(200), nullable = True     ),
    mysql_charset='utf8'
)

customers = Table('customers', meta,
    Column('custId',           Integer,      primary_key = True  ),
    Column('custCode',         Unicode(15),  nullable = False    ),
    Column('custName',         Unicode(100), nullable = False    ),
    Column('custSubj',         Integer      ,ForeignKey('subject.id')),
    Column('custPhone',        Unicode(15),  nullable = True     ),
    Column('custCell',         Unicode(15),  nullable = True     ),
    Column('custFax',          Unicode(15),  nullable = True     ),
    Column('custAddress',      Unicode(100), nullable = True     ),
    Column('custPostalCode',   String(15),   nullable = True     ),
    Column('custEmail',        Unicode(15),  nullable = True     ),
    Column('custEcnmcsCode',   Unicode(20),  nullable = True     ),
    Column('custPersonalCode', String(15),   nullable = True     ),
    Column('custWebPage',      Unicode(50),  nullable = True     ),
    Column('custResposible',   Unicode(50),  nullable = True     ),
    Column('custConnector',    Unicode(50),  nullable = True     ),
    Column('custGroup',        Integer,      ForeignKey('custGroups.custGrpId')),
    Column('custDesc',         Unicode(200), nullable = True     ),
    Column('custBalance',      Float,        ColumnDefault(0),      nullable = False  ),
    Column('custCredit',       Float,        ColumnDefault(0),      nullable = False  ),
    Column('custRepViaEmail',  Boolean,      ColumnDefault(False),  nullable = False  ),
    Column('custAccName1',     Unicode(50),  nullable = True     ),
    Column('custAccNo1',       Unicode(50),  nullable = True     ),
    Column('custAccBank1',     Unicode(50),  nullable = True     ),
    Column('custAccName2',     Unicode(50),  nullable = True     ),
    Column('custAccNo2',       Unicode(50),  nullable = True     ),
    Column('custAccBank2',     Unicode(50),  nullable = True     ),
    Column('custTypeBuyer',    Boolean,      ColumnDefault(True),   nullable = False  ),
    Column('custTypeSeller',   Boolean,      ColumnDefault(True),   nullable = False  ),
    Column('custTypeMate',     Boolean,      ColumnDefault(False),  nullable = False  ),
    Column('custTypeAgent',    Boolean,      ColumnDefault(False),  nullable = False  ),
    Column('custIntroducer',   Unicode(50),  nullable = True     ),
    Column('custCommission',   Unicode(15),  nullable = True     ),
    Column('custMarked',       Boolean,      ColumnDefault(False),  nullable = False  ),
    Column('custReason',       Unicode(200), nullable = True     ),
    Column('custDiscRate',     Unicode(14),  nullable = True     ),
    mysql_charset='utf8'
)

config = Table("config", meta,
    Column('cfgId'   , Integer     , primary_key = True),
    Column('cfgKey'  , Unicode(100), nullable = False, unique = True),
    Column('cfgValue', Unicode(100), nullable = False),
    Column('cfgDesc' , Unicode(100), nullable = True),
    Column('cfgType' , Integer     , nullable = True),
    Column('cfgCat'  , Integer     , nullable = True),
    mysql_charset='utf8'
)

banknames = Table("BankNames", meta,
    Column('Id'  , Integer    , primary_key=True),
    Column('Name', Unicode(50), nullable=False),
    mysql_charset='utf8'
)

bankAccounts = Table('bankAccounts', meta,
    Column('accId',           Integer,      primary_key = True  ),
    Column('accName',         Unicode(100), nullable = False    ),
    Column('accNumber',       Unicode(40),       nullable = False , unique=True   ),
    Column('accType',         Integer,       nullable = True     ),
    Column('accOwner',        Unicode(50),  nullable = True     ),
    Column('accBank',         Integer, ForeignKey('BankNames.Id'), nullable = True     ),
    Column('accBankBranch',   Unicode(50),  nullable = True     ),
    Column('accBankAddress',  Unicode(100), nullable = True     ),
    Column('accBankPhone',    Unicode(40),       nullable = True     ),
    Column('accBankWebPage',  Unicode(100),       nullable = True     ), #TODO change to unicode
    Column('accDesc',         Unicode(200), nullable = True     ),
    mysql_charset='utf8'
)

chequehistory = Table('ChequeHistory', meta,
    Column('Id',        Integer,    primary_key = True),
    Column('ChequeId',  Integer,    ForeignKey('Cheque.chqId')),
    Column('Amount',    Float,      ColumnDefault(0), nullable = False),
    Column('WrtDate',   Date,       nullable = False),
    Column('DueDate',   Date,       nullable = False),
    Column('Serial',    Unicode(50),nullable = False),
    Column('Status',    Integer,    ColumnDefault(0), nullable = False),
    Column('Cust',      Integer,    ForeignKey('customers.custId')),
    Column('Account',   Integer,    ForeignKey('bankAccounts.accId'), nullable = True),
    Column('TransId',   Integer,    ColumnDefault(0)), #Transaction id is zero for non-invoice cheques.
    Column('Desc',      Unicode(200),nullable = True),
    Column('Date',      Date,       nullable=False),
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
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata
    meta.bind = migrate_engine

    products.create(checkfirst=True)
    productGroups.create(checkfirst=True)
    transactions.create(checkfirst=True)
    exchanges.create(checkfirst=True)
    payments.create(checkfirst=True)
    notebook = Table('notebook' , meta, autoload=True)
    cheque.create(checkfirst=True)
    custGroups.create(checkfirst=True)
    customers.create(checkfirst=True)
    bankAccounts.create(checkfirst=True)
    config.create(checkfirst=True)
    banknames.create(checkfirst=True)
    notebook.create(checkfirst=True)
    chequehistory.create(checkfirst=True)
    user.create(checkfirst=True)
    logging.debug("upgrade to 2")

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
        {'cfgId' : 1, 'cfgType' : 1, 'cfgCat' : 0, 'cfgKey' : u'co-name'       , 'cfgValue' : u'Enter Company Name',
            'cfgDesc' : u'Enter Company name here'},
        {'cfgId' : 2, 'cfgType' : 0, 'cfgCat' : 0, 'cfgKey' : u'co-logo'       , 'cfgValue' : u'',
            'cfgDesc' : u'Select Colpany logo'},
        {'cfgId' : 3, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : u'custSubject'   , 'cfgValue' : u'4',
            'cfgDesc' : u'Enter here'},
        {'cfgId' : 4, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'bank'          , 'cfgValue' : u'1',
            'cfgDesc' : u'Enter here'},
        {'cfgId' : 5, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'cash'          , 'cfgValue' : u'3',
            'cfgDesc' : u'Enter here'},
        {'cfgId' : 6, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'buy'           , 'cfgValue' : u'17',
            'cfgDesc':u'Enter here'},
        {'cfgId' : 7, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'sell'          , 'cfgValue' : u'18',
            'cfgDesc':u'Enter here'},
        {'cfgId' : 8, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : u'sell-discount' , 'cfgValue' : u'25',
            'cfgDesc':u'Enter here'},
        {'cfgId' : 9, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'tax'           , 'cfgValue' : u'33',
            'cfgDesc':u'Enter here'},
        {'cfgId' :10, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'partners'      , 'cfgValue' : u'8',
            'cfgDesc':u'Enter here'},
        {'cfgId' :11, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'cost'          , 'cfgValue' : u'2',
            'cfgDesc':u'Enter here'},
        {'cfgId' :12, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : u'bank-wage'     , 'cfgValue' : u'31',
            'cfgDesc':u'Enter here'},
        {'cfgId' :13, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'our_cheque'    , 'cfgValue' : u'22',
            'cfgDesc' :u'Enter here'},
        {'cfgId' :14, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'other_cheque'    , 'cfgValue' : u'6',
            'cfgDesc' :u'Enter here'},
        {'cfgId' :15, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'income'     , 'cfgValue' : u'83',
            'cfgDesc':u'Enter here'}
        #{'cfgId' :11, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'fund'          , 'cfgValue' : u'??',
        #    'cfgDesc':u'Enter here'},  #TODO cfgKey
        #{'cfgId' :12, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : u'acc-receivable', 'cfgValue' : u'??',
        #    'cfgDesc':u'Enter here',}, #TODO cfgKey
        #{'cfgId' :13, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' :u'commission'     , 'cfgValue' : u'??',
        #    'cfgDesc':u'Enter here'}   #TODO cfgKey
     )
               
    op = banknames.insert()
    op.execute(
        { 'Id': 1, "Name":u"پارسیان"},
        { 'Id': 2, "Name":u"دی"},
        { 'Id': 3, "Name":u"سامان"},
        { 'Id': 4, "Name":u"سپه"},
        { 'Id': 5, "Name":u"سرمایه"},
        { 'Id': 6, "Name":u"صادرات"},
        { 'Id': 7, "Name":u"کشاورزی"},
        { 'Id': 8, "Name":u"ملت"},
        { 'Id': 9, "Name":u"ملی"}
    )
    op = custGroups.insert()
    op.execute(
        { 'custGrpId': 1, 'custGrpCode': 1, "custGrpName":u"عمومی", 'custGrpDesc': u"مشتریان عمومی"},
    )

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine

    products.drop()
    productGroups.drop()
    transactions.drop()
    exchanges.drop()
    payments.drop()

    cheques.drop()
    custGroups.drop()
    customers.drop()
    bankAccounts.drop()
    config.drop()
    print("downgrade to 1")
    

