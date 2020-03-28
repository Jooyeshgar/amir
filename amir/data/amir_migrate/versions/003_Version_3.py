#!/usr/bin/env python3

from sqlalchemy import *
from migrate import *
import logging
# from migrate.changeset.constraint import ForeignKeyConstraint


meta = MetaData()

permissions = Table('permissions', meta,
    Column('id', Integer, primary_key = True ),
    Column('name', Unicode(50), nullable = False),
    Column('value', Unicode(20), nullable = True),
    mysql_charset='utf8'
)

factors = Table('factors', meta,
    Column('Id', Integer, primary_key=True),
    Column('Code', Integer, nullable=False),
    Column('tDate', Date, nullable=False),
    Column('Bill', Integer, ColumnDefault(0)),
    Column('Cust', Integer, ForeignKey('customers.custId')),
    Column('Addition', Float, ColumnDefault(0), nullable=False),
    Column('Subtraction', Float, ColumnDefault(0), nullable=False),
    Column('VAT', Float, ColumnDefault(0), nullable=False),
    Column('Fee', Float, ColumnDefault(0), nullable=False),
    Column('PayableAmnt', Float, ColumnDefault(0), nullable=False),
    Column('CashPayment', Float, ColumnDefault(0), nullable=False),
    Column('ShipDate', Date, nullable=True),
    Column('Delivery', Unicode(50), nullable=True),
    Column('ShipVia', Unicode(100), nullable=True),
    Column('Permanent', Boolean, ColumnDefault(0)),
    Column('Desc', Unicode(200), nullable=True),
    Column('Sell', Integer,  nullable=False),
    Column('LastEdit', Date, nullable=True),
    Column('Activated', Boolean, ColumnDefault(0), nullable=False),
    mysql_charset='utf8'
)

factorItems = Table('factorItems', meta,
    Column('id', Integer, primary_key = True),
    Column('number', Integer, nullable = False),
    Column('productId', Integer, ForeignKey('products.id')),
    Column('qnty', Float, ColumnDefault(0),   nullable = False),
    Column('untPrc', Float, ColumnDefault(0),   nullable = False),
    Column('untDisc', Unicode(30), ColumnDefault("0"), nullable = False),
    Column('factorId', Integer),
    Column('desc', Unicode(200), nullable = True),
    mysql_charset='utf8'
)

def _2to3digits(num):
    _3digit = ""
    i = 0
    while i< len(num )- 1 :
        _3digit = "0" + num[len(num) - i - 2 ] + num [len(num) - i - 1] + _3digit
        i += 2
    return _3digit

def upgrade(migrate_engine):
    from sqlalchemy.orm import sessionmaker, scoped_session
    meta.bind = migrate_engine

    customers = Table('customers' , meta , autoload =True)
    products  = Table('products' , meta , autoload =True)
    subject   = Table('subject', meta, autoload=True)

    factors.create(checkfirst=True)
    factorItems.create(checkfirst=True)

    Session = scoped_session(sessionmaker(bind=migrate_engine))
    s = Session()

    try:
        Table('payment', meta, autoload=True).drop()
        Table('exchanges', meta, autoload=True).drop()
        Table('transactions', meta, autoload=True).drop()
    except:
        pass

    subject = Table('subject' , meta , autoload=True)
    colPer = Column('permanent', Boolean, default=False)
    colPer.create(subject,  populate_default=True)
    assert colPer is subject.c.permanent

   # s.query(subject).update({subject.c.code: _2to3digits(subject.c.code)})      #TODO try this instead of raw sql command
    query = s.query(subject)
    al = query.all()
    for subj in al :
       # query.filter(subject.c.id == subj.id).first().update({subject.c.code : _2to3digits(subj.code)})    # TODO       try this instead of raw sql command
        s.execute("UPDATE subject set code = '" + _2to3digits(subj.code) + "' where id =" + str(subj.id) + ";")


    al = s.query(customers).all()
    for cust in al:
        s.execute("UPDATE customers set custCode='" + _2to3digits(cust.custCode) + "' WHERE custId  = " + str(cust.custId))

    # s.execute('INSERT INTO factors (Id, Code, tDate, Bill, Cust, Addition, Subtraction, VAT, CashPayment, ShipDate, Permanent, `Desc`, Sell, Activated, Fee, PayableAmnt, LastEdit)\
    #            SELECT transId, transCode, transDate, transBill, transCust, transAddition, transSubtraction, transTax, transCashPayment, transShipDate, transPermanent,  transDesc, transSell, 0, 0, 0, 0 FROM transactions;')
    # s.execute('INSERT INTO factorItems (exchngId, exchngNo, exchngProduct, exchngQnty, exchngUntPrc, exchngUntDisc, exchngTransId, exchngDesc)\
    #            SELECT exchngId, exchngNo, exchngProduct, exchngQnty, exchngUntPrc, exchngUntDisc, exchngTransId, exchngDesc FROM exchanges;')
    # s.execute('DROP TABLE exchanges;')

    s.execute('ALTER TABLE `Cheque` ADD COLUMN `chqDelete` Boolean;')

    s.execute('DROP TABLE users;')

    s.execute('DELETE FROM config')

    s.execute('ALTER TABLE `products` ADD COLUMN `uMeasurement`  Text;')
    s.commit()

    notebook = Table('notebook', meta, autoload=True)
    colFactor = Column('factorId' , Integer, default =0)
    colFactor.create(notebook ,  populate_default=True)
    assert colFactor is notebook.c.factorId
    colChq = Column('chqId' , Integer, default =0)
    colChq.create(notebook ,  populate_default=True)
    assert colChq is notebook.c.chqId
    notebook.c.value.alter(type=Float)
    assert notebook.c.value.type


    # factorItems = Table('factorItems', meta, autoload=True)
    # factorItems.c.exchngId.alter(name='id')
    # factorItems.c.exchngNo.alter(name='number')
    # factorItems.c.exchngProduct.alter(name='productId')
    # factorItems.c.exchngQnty.alter(name='qnty')
    # factorItems.c.exchngUntPrc.alter(name='untPrc')
    # factorItems.c.exchngUntDisc.alter(name='untDisc')
    # factorItems.c.exchngTransId.alter(name='factorId')
    # factorItems.c.exchngDesc.alter(name='desc')

    permissions.create(checkfirst=True)

    cheque = Table('Cheque', meta, autoload=True)
    # factors = Table('factors', meta, autoload=True)
    # cons = ForeignKeyConstraint ([cheque.c.chqTransId] , [factors.c.Id])
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
        {'cfgId' : 1, 'cfgType' : 1, 'cfgCat' : 0, 'cfgKey' : 'co-name'       , 'cfgValue' : 'نام شرکت', 'cfgDesc' : 'نام شرکت شما'},
        {'cfgId' : 2, 'cfgType' : 0, 'cfgCat' : 0, 'cfgKey' : 'co-logo'       , 'cfgValue' : '', 'cfgDesc' : 'لوگوی شرکت خود را انتخاب نمایید'},
        {'cfgId' : 3, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : 'custSubject'   , 'cfgValue' : '4',  'cfgDesc' : 'طرف حساب ها'},
        {'cfgId' : 4, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : 'bank'          , 'cfgValue' : '1',  'cfgDesc' : 'بانک ها'},
        {'cfgId' : 5, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : 'cash'          , 'cfgValue' : '14',  'cfgDesc' : 'نقدی'},
        # {'cfgId' : 6, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : 'buy'           , 'cfgValue' : '17', 'cfgDesc':'Enter here'},
        {'cfgId' : 7, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : 'buy-discount'  , 'cfgValue' : '53', 'cfgDesc':'تخفیفات خرید'},
        # {'cfgId' : 8, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : 'sell'          , 'cfgValue' : '18', 'cfgDesc':'Enter here'},
        {'cfgId' : 9, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : 'sell-discount' , 'cfgValue' : '55', 'cfgDesc':'تخفیفات فروش'},
        {'cfgId' :10, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : 'sell-vat'      , 'cfgValue' : '41', 'cfgDesc':'مالیات فروش'},
        {'cfgId' :11, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : 'buy-vat'       , 'cfgValue' : '40', 'cfgDesc':'مالیات خرید'},
        {'cfgId' :12, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : 'sell-fee'      , 'cfgValue' : '57', 'cfgDesc':'عوارض فروش'},
        {'cfgId' :13, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : 'buy-fee'       , 'cfgValue' : '56', 'cfgDesc':'عوارض خرید'},
        {'cfgId' :14, 'cfgType' : 1, 'cfgCat' : 1, 'cfgKey' : 'vat-rate'      , 'cfgValue' : '6',  'cfgDesc':'درصد مالیات'},
        {'cfgId' :15, 'cfgType' : 1, 'cfgCat' : 1, 'cfgKey' : 'fee-rate'      , 'cfgValue' : '3',  'cfgDesc':'درصد عوارض'},
        {'cfgId' :16, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : 'partners'      , 'cfgValue' : '8',  'cfgDesc':'شرکا'},
        {'cfgId' :17, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : 'cost'          , 'cfgValue' : '2',  'cfgDesc':'هزینه ها'},
        {'cfgId' :18, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : 'bank-wage'     , 'cfgValue' : '31', 'cfgDesc':'کارمزد بانک'},
        {'cfgId' :19, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : 'our_cheque'    , 'cfgValue' : '46', 'cfgDesc':'اسناد پرداختنی'},
        {'cfgId' :20, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : 'other_cheque'  , 'cfgValue' : '44',  'cfgDesc':'اسناد دریافتنی'},
        {'cfgId' :21, 'cfgType' : 3, 'cfgCat' : 1, 'cfgKey' : 'income'        , 'cfgValue' : '81', 'cfgDesc':'درآمد'},
        {'cfgId' :22, 'cfgType' : 1, 'cfgCat' : 0, 'cfgKey' : 'co-address'    , 'cfgValue' : 'نشانی شرکت (قابل تنظیم در تنظیمات->پیکربندی',  'cfgDesc':'نشانی شرکت شما'},
        {'cfgId' :23, 'cfgType' : 1, 'cfgCat' : 0, 'cfgKey' : 'co-economical-code'     , 'cfgValue' : 'کد اقتصادی',  'cfgDesc':'کد اقتصادی شما'},
        {'cfgId' :24, 'cfgType' : 1, 'cfgCat' : 0, 'cfgKey' : 'co-national-code'       , 'cfgValue' : 'کد ملی',  'cfgDesc':'کد ملی شما'},
        {'cfgId' :25, 'cfgType' : 1, 'cfgCat' : 0, 'cfgKey' : 'co-postal-code'         , 'cfgValue' : 'کد پستی',  'cfgDesc':'کد پستی شما'},
        {'cfgId' :26, 'cfgType' : 1, 'cfgCat' : 0, 'cfgKey' : 'co-phone-number'        , 'cfgValue' : 'شماره تلفن',  'cfgDesc':'شماره تلفن شما'},
        {'cfgId' :27, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : 'sell-adds'              , 'cfgValue' : '36',  'cfgDesc':'اضافات فروش'},
        {'cfgId' :28, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : 'buy-adds'               , 'cfgValue' : '32',  'cfgDesc':'اضافات خرید'},
        {'cfgId' :29, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : 'inventories'            , 'cfgValue' : '70',  'cfgDesc':'موجودی اولیه'},
        {'cfgId' :30, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : 'fund'                   , 'cfgValue' : '21',  'cfgDesc':'سرمایه اولیه'},
        {'cfgId' :31, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : 'float'                  , 'cfgValue' : '68',  'cfgDesc':'اسناد در جریان وصول'},
        {'cfgId' :32, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : 'purchase-return'        , 'cfgValue' : '42',  'cfgDesc':'برگشت از خرید'},
        {'cfgId' :33, 'cfgType' : 2, 'cfgCat' : 1, 'cfgKey' : 'sale-return'            , 'cfgValue' : '43',  'cfgDesc':'برگشت از فروش'}
    )

def downgrade(migrate_engine):
    logging.error("Downgrade to 2 is not possible!")


