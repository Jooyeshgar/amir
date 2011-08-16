from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, ColumnDefault
from sqlalchemy import Integer, String, Date, Boolean, Unicode, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from migrate.versioning import exceptions,api
# metadata = MetaData(bind=engine)
 
# create tables in database
# metadata.create_all
Base = declarative_base()

## \defgroup Database
## @{

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True)
    name = Column(Unicode(60), nullable=False)
    parent_id = Column(Integer, ColumnDefault(0), ForeignKey('users.id'), nullable=False)
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
        
#Version 0.1 tables
class Subject(Base):
    __tablename__ = "subject"
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True)
    name = Column(String(60), nullable=False)
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

#Version 0.2 tables
class Products(Base):
    __tablename__ = "products"
    id              = Column(   Integer,                            primary_key = True      )
    code            = Column(   Unicode(20),                        nullable    = False     )
    name            = Column(   Unicode(60),                        nullable    = False     )
    accGroup        = Column(   Integer,                            ForeignKey('productGroups.id') )
    location        = Column(   Unicode(50),                        nullable    = True      )
    quantity        = Column(   Float,          ColumnDefault(0),   nullable    = False     ) #TODO change to float
    qntyWarning     = Column(   Float,          ColumnDefault(0),   nullable    = True      )
    oversell        = Column(   Boolean,        ColumnDefault(0)                            )
    purchacePrice   = Column(   Float,          ColumnDefault(0),   nullable    = False     )
    sellingPrice    = Column(   Float,          ColumnDefault(0),   nullable    = False     )
    discountFormula = Column(   Unicode(100),                       nullable    = True      )
    productDesc     = Column(   Unicode(200),                       nullable    = True      )

    def __init__(   self,   code,   name,   warn,   over,   pLoc,
                    qnty,   purc,   sell,   accg,   desc,   disc    ):
        self.code       = code
        self.name       = name
        self.oversell   = over
        self.location   = pLoc
        self.quantity   = qnty
        self.accGroup   = accg
        self.productDesc    = desc
        self.qntyWarning    = warn
        self.sellingPrice       = sell
        self.purchacePrice      = purc
        self.discountFormula    = disc
        

class ProductGroups(   Base    ):
    __tablename__ = "productGroups"
    id      = Column(   Integer,        primary_key = True          )
    code    = Column(   Unicode(20),    nullable    = False         )
    name    = Column(   Unicode(60),    nullable    = False         )
    buyId   = Column(   Integer,        ForeignKey('subject.id')    )
    sellId  = Column(   Integer,        ForeignKey('subject.id')    )

    def __init__(   self,   code,   name,   buyId,  sellId  ):
        self.code   = code
        self.name   = name
        self.buyId  = buyId
        self.sellId = sellId
        

class Transactions(Base):
    __tablename__ = "transactions"
    transId         = Column( Integer,      primary_key = True                      )
    transCode       = Column( String,       nullable = False                        )
    transDate       = Column( Date,         nullable = False                        ) 
    transBill       = Column( Integer,      ColumnDefault(0)                        ) #Bill id is zero for temporary transactions
    transCust       = Column( Integer,      ForeignKey('customers.custId')          )
    transAddition   = Column( Float,        ColumnDefault(0),   nullable = False    )
    transSubtraction= Column( Float,        ColumnDefault(0),   nullable = False    )
    transTax        = Column( Float,        ColumnDefault(0),   nullable = False    )
    transCashPayment= Column( Float,        ColumnDefault(0),   nullable = False    )
    transShipDate   = Column( Date,         nullable = True                         )
    transFOB        = Column( Unicode(50),  nullable = True                         )
    transShipVia    = Column( Unicode(100), nullable = True                         )
    transPermanent  = Column( Boolean,      ColumnDefault(0)                        )
    transDesc       = Column( Unicode(200), nullable = True                         )
    transSell       = Column( Boolean,      ColumnDefault(0),   nullable = False    )
#    transLastEdit   = Column( Date,         nullable = True                         )

    def __init__( self, transCode, transDate, transBill, transCust, transAdd, transSub, 
                  transTax, transCash, transShpDate, transFOB, transShipVia, transPrmnt, 
                  transDesc, transSell ):#, transSell, transLastEdit ):

        self.transCode          = transCode
        self.transDate          = transDate
        self.transBill          = transBill
        self.transCust          = transCust
        self.transAddition      = transAdd
        self.transSubtraction   = transSub
        self.transTax           = transTax
        self.transCashPayment   = transCash
        self.transShipDate      = transShpDate
        self.transFOB           = transFOB
        self.transShipVia       = transShipVia
        self.transPermanent     = transPrmnt
        self.transDesc          = transDesc
        self.transSell          = transSell
#        self.transLastEdit      = transLastEdit


class Exchanges(Base):
    __tablename__ = "exchanges"
    exchngId        = Column(   Integer,        primary_key = True                      )
    exchngNo        = Column(   Integer,        nullable = False                        )
    exchngProduct   = Column(   Integer,        ForeignKey('products.id')               )
    exchngQnty      = Column(   Float,          ColumnDefault(0),   nullable = False    )
    exchngUntPrc    = Column(   Float,          ColumnDefault(0),   nullable = False    )
    exchngUntDisc   = Column(   Unicode(30),    ColumnDefault("0"), nullable = False    )
    exchngTransId   = Column(   Integer,        ForeignKey('transactions.transId')      )
    exchngDesc      = Column(   Unicode(200),   nullable = True                         )

    def __init__( self, exchngNo, exchngProduct, exchngQnty,
                  exchngUntPrc, exchngUntDisc, exchngTransId, exchngDesc):

        self.exchngNo       = exchngNo
        self.exchngProduct  = exchngProduct
        self.exchngQnty     = exchngQnty
        self.exchngUntPrc   = exchngUntPrc
        self.exchngUntDisc  = exchngUntDisc
        self.exchngTransId  = exchngTransId
        self.exchngDesc     = exchngDesc


class Payment(Base):
    __tablename__ = "payment"
    paymntId        = Column( Integer,      primary_key = True                )
    paymntDueDate   = Column( Date,         nullable = False                  )
    paymntBank      = Column( Unicode(100), nullable = True                   )
    paymntSerial    = Column( Unicode(50),  nullable = True                   )
    paymntAmount    = Column( Float,        ColumnDefault(0), nullable = False)
    paymntPayer     = Column( Integer,      ForeignKey('customers.custId')    )
    paymntWrtDate   = Column( Date,         nullable = True                   )
    paymntDesc      = Column( Unicode(200), nullable = True                   )
    paymntTransId   = Column( Integer,      ColumnDefault(0)                  ) #Transaction id is zero for non-invoice payments.
    paymntBillId    = Column( Integer,      ColumnDefault(0)                  ) #Bill id is zero for temporary transactions.
    paymntTrckCode  = Column( Unicode,      nullable = True                   )
    paymntOrder     = Column( Integer,      ColumnDefault(0), nullable = False)
#    paymntChq       = Column( Integer,      ForeignKey('cheques.chqId')             )

    def __init__( self, paymntDueDate, paymntBank, paymntSerial, paymntAmount,
                  paymntPayer, paymntWrtDate, paymntDesc, paymntTransId, paymntBillId, 
                  paymntTrckCode, paymntOrder):

        #self.paymntNo        = paymntNo
        self.paymntDueDate   = paymntDueDate
        self.paymntBank      = paymntBank
        self.paymntSerial    = paymntSerial
        self.paymntAmount    = paymntAmount
        self.paymntPayer     = paymntPayer
        self.paymntWrtDate   = paymntWrtDate
        self.paymntDesc      = paymntDesc
        self.paymntTransId   = paymntTransId
        self.paymntBillId    = paymntBillId
        self.paymntTrckCode  = paymntTrckCode
        self.paymntOrder     = paymntOrder
        

class Cheque(Base):
    __tablename__ = "cheque"
    chqId       = Column(Integer,      primary_key = True)
    chqAmount   = Column(Float,        ColumnDefault(0), nullable = False)
    chqWritDate  = Column(Date,         nullable = False)
    chqDueDate  = Column(Date,         nullable = False)
    #chqBank    = Column( Unicode(50),  nullable = True)
    chqAccount  = Column(Integer,      ForeignKey('bankAccounts.accId'), nullable = True)
    chqSerial   = Column(Unicode(50),  nullable = False)
    chqStatus   = Column(Integer,      ColumnDefault(0), nullable = False)
    #chqPaid    = Column( Boolean,      ColumnDefault(0),   nullable = False)
    chqCust     = Column( Integer,      ForeignKey('customers.custId'))
    #chqSpen    = Column( Boolean,      ColumnDefault(0),   nullable = False)
    chqTransId  = Column(Integer,      ColumnDefault(0)) #Transaction id is zero for non-invoice cheques.
    chqBillId   = Column(Integer,      ColumnDefault(0)) #Bill id is zero for temporary transactions.
    chqDesc     = Column(Unicode(200), nullable = True)
    chqOrder    = Column(Integer,      ColumnDefault(0), nullable = False)

    def __init__( self, chqAmount, chqWrtDate, chqDueDate, chqSerial,
                  chqStatus, chqCust, chqTransId, chqBillId, chqDesc, chqOrder):

        self.chqAmount   = chqAmount
        self.chqWrtDate  = chqWrtDate
        self.chqDueDate  = chqDueDate
        #self.chqBank     = chqBank
        self.chqSerial   = chqSerial
        self.chqStatus   = chqStatus
        #self.chqPaid     = chqPaid
        self.chqCust     = chqCust
        #self.chqSpent    = chqSpent
        self.chqTransId  = chqTransId
        self.chqBillId   = chqBillId
        self.chqDesc     = chqDesc
        self.chqOrder    = chqOrder


class CustGroups(Base):
    __tablename__ = "custGroups"
    custGrpId   = Column( Integer,      primary_key = True  )
    custGrpCode = Column( String(20),       nullable = False    )
    custGrpName = Column( Unicode(50),  nullable = False    )
    custGrpDesc = Column( Unicode(200), nullable = True     )

    def __init__( self, custGrpCode, custGrpName, custGrpDesc    ):

        self.custGrpCode    = custGrpCode
        self.custGrpName    = custGrpName
        self.custGrpDesc    = custGrpDesc

class Customers(Base):
    __tablename__ = "customers"
    custId          = Column( Integer,      primary_key = True  )
    custCode        = Column( Unicode(15),  nullable = False    )
    custName        = Column( Unicode(100), nullable = False    )
    custSubj        = Column( Integer,      ForeignKey('subject.id'))
    custPhone       = Column( Unicode(15),  nullable = True     )
    custCell        = Column( Unicode(15),  nullable = True     )
    custFax         = Column( Unicode(15),  nullable = True     )
    custAddress     = Column( Unicode(100), nullable = True     )
    custPostalCode  = Column( Unicode(15),  nullable = True     )
    custEmail       = Column( Unicode(15),  nullable = True     )
    custEcnmcsCode  = Column( Unicode(20),  nullable = True     )
    custPersonalCode= Column( Unicode(15),  nullable = True     )
    custWebPage     = Column( Unicode(50),  nullable = True     )
    custResposible  = Column( Unicode(50),  nullable = True     )
    custConnector   = Column( Unicode(50),  nullable = True     )
    custGroup       = Column( Integer,      ForeignKey('custGroups.custGrpId'))
    custDesc        = Column( Unicode(200), nullable = True     )
    custBalance     = Column( Float,        ColumnDefault(0),   nullable = False    )
    custCredit      = Column( Float,        ColumnDefault(0),   nullable = False    )
    custRepViaEmail = Column( Boolean,      ColumnDefault(False),   nullable = False)
    custAccName1    = Column( Unicode(50),  nullable = True)
    custAccNo1      = Column( Unicode(30),  nullable = True)
    custAccBank1    = Column( Unicode(50),  nullable = True)
    custAccName2    = Column( Unicode(50),  nullable = True)
    custAccNo2      = Column( Unicode(30),  nullable = True)
    custAccBank2    = Column( Unicode(50),  nullable = True)
    custTypeBuyer   = Column( Boolean,      ColumnDefault(True),   nullable = False)
    custTypeSeller  = Column( Boolean,      ColumnDefault(True),   nullable = False)
    custTypeMate    = Column( Boolean,      ColumnDefault(False),  nullable = False)
    custTypeAgent   = Column( Boolean,      ColumnDefault(False),  nullable = False)
    custIntroducer  = Column( Integer,      ForeignKey('customers.custId'))
    custCommission  = Column( Unicode(15),  nullable = True )
    custMarked      = Column( Boolean,      ColumnDefault(False),  nullable = False)
    custReason      = Column( Unicode(200), nullable = True )
    custDiscRate    = Column( Unicode(15),  nullable = True )

    def __init__( self, custCode, custName, custSubj, custPhone, custCell, custFax, custAddress,
                  custEmail, custEcnmcsCode, custWebPage, custResposible, custConnector, 
                  custGroup, custPostalCode="", custPersonalCode="", custDesc="", custBalance=float(0), custCredit=float(0), 
                  custRepViaEmail=False, custAccName1="", custAccNo1="", custAccBank1="", custAccName2="", custAccNo2="", 
                  custAccBank2="", custTypeBuyer=True, custTypeSeller=True, custTypeMate=False, custTypeAgent=False, 
                  custIntroducer="", custCommission="", custMarked=False, custReason="", custDiscRate="" ):

        self.custCode        = custCode
        self.custName        = custName    
        self.custSubj        = custSubj
        self.custPhone       = custPhone
        self.custCell        = custCell
        self.custFax         = custFax
        self.custAddress     = custAddress
        self.custPostalCode  = custPostalCode
        self.custEmail       = custEmail
        self.custEcnmcsCode  = custEcnmcsCode
        self.custPersonalCode = custPersonalCode
        self.custWebPage     = custWebPage
        self.custResposible  = custResposible
        self.custConnector   = custConnector
        self.custGroup       = custGroup
        self.custDesc        = custDesc
        self.custBalance     = custBalance
        self.custCredit      = custCredit
        self.custRepViaEmail = custRepViaEmail
        self.custAccName1    = custAccName1
        self.custAccNo1      = custAccNo1
        self.custAccBank1    = custAccBank1
        self.custAccName2    = custAccName2
        self.custAccNo2      = custAccNo2
        self.custAccBank2    = custAccBank2
        self.custTypeBuyer   = custTypeBuyer
        self.custTypeSeller  = custTypeSeller
        self.custTypeMate    = custTypeMate
        self.custTypeAgent   = custTypeAgent
        self.custIntroducer  = custIntroducer
        self.custCommission  = custCommission
        self.custMarked      = custMarked
        self.custReason      = custReason
        self.custDiscRate    = custDiscRate
        
class BankNames(Base):
    __tablename__ = 'BankNames'
    Id   = Column(Integer    , primary_key=True)
    Name = Column(Unicode(50), nullable=False)

    def __init__(self, name):
        self.Name = name

class BankAccounts(Base):
    __tablename__   = "bankAccounts"
    accId           = Column( Integer,      primary_key = True  )
    accName         = Column( Unicode(100), nullable = False    )
    accNumber       = Column( Unicode(40) , nullable = False    )
    accType         = Column( Integer,       nullable = True     )
    accOwner        = Column( Unicode(50),  nullable = True     )
    accBank         = Column( Integer,  ForeignKey('BankNames.Id'), nullable = True     )
    accBankBranch   = Column( Unicode(50),  nullable = True     )
    accBankAddress  = Column( Unicode(100), nullable = True     )
    accBankPhone    = Column( Unicode(40),  nullable = True     )
    accBankWebPage  = Column( Unicode(100),       nullable = True     )
    accDesc         = Column( Unicode(200), nullable = True     ) 
    
    def __init__( self, accName, accNumber, accType, accOwner, accBank, accBankBranch, 
                  accBankAddress, accBankPhone, accBankWebPage, accDesc ):

        self.accName        = accName
        self.accNumber      = accNumber
        self.accType        = accType
        self.accOwner       = accOwner
        self.accBank        = accBank
        self.accBankBranch  = accBankBranch
        self.accBankAddress = accBankAddress
        self.accBankPhone   = accBankPhone
        self.accBankWebPage = accBankWebPage   #TODO change to unicode
        self.accDesc        = accDesc

class Config(Base):
    __tablename__  = "config"
    cfgId          = Column(Integer, primary_key = True)
    cfgKey         = Column(Unicode(100), nullable = False, unique = True)
    cfgValue       = Column(Unicode(100), nullable = False)
    cfgDesc        = Column(Unicode(100), nullable = True)
    cfgType        = Column(Integer     , nullable = True)
    cfgCat         = Column(Integer     , nullable = True)
    
    def __init__(self, cfgKey, cfgValue, cfgDesc, cfgType, cfgCat):
        self.cfgKey   = cfgKey
        self.cfgValue = cfgValue
        self.cfgDesc  = cfgDesc
        self.cfgType  = cfgType
        self.cfgCat   = cfgCat
        

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
