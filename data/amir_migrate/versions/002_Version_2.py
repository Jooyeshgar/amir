from sqlalchemy import *
from migrate import *
import logging

meta = MetaData()

#subject table (version 1 and 2):
subject = Table('subject', meta,
    Column('id', Integer, primary_key=True),
    Column('code', String(20), nullable=False),
    Column('name', Unicode(60), nullable=False),
    Column('parent_id', Integer, ColumnDefault(0), ForeignKey('subject.id'), nullable=False),
    Column('lft', Integer, nullable=False),
    Column('rgt', Integer, nullable=False),
    Column('type', Integer)
)

#New tables (version 2):
products = Table('products', meta,
    Column('id',              Integer,                            primary_key = True      ),
    Column('code',            String,                             nullable    = False     ),
    Column('name',            Unicode(60),                        nullable    = False     ),
    Column('accGroup',        Integer,        ForeignKey('groups.id')                     ),
    Column('location',        Unicode(50),                        nullable    = True      ),
    Column('quantity',        Integer,        ColumnDefault(0),   nullable    = False     ),
    Column('qntyWarning',     Integer,        ColumnDefault(0),   nullable    = True      ),
    Column('oversell',        Boolean,        ColumnDefault(0)                            ),
    Column('purchacePrice',   Integer,        ColumnDefault(0),   nullable    = False     ),
    Column('sellingPrice',    Integer,        ColumnDefault(0),   nullable    = False     ),
    Column('discountFormula', Unicode(100),                       nullable    = True      ),
    Column('productDesc',     Unicode(200),                       nullable    = True      )
)

groups = Table('groups', meta,
    Column('id',           Integer,        primary_key = True      ),
    Column('code',         String(20),     nullable    = False     ),
    Column('name',         Unicode(60),    nullable    = False     ),
    Column('buyId',        Integer,        ForeignKey('subject.id')),
    Column('sellId',       Integer,        ForeignKey('subject.id'))
)
    
transactions = Table('transactions', meta,
    Column('transId',            Integer,      primary_key = True                      ),
    Column('transCode',          String,       nullable = False                        ),
    Column('transDate',          Date,         nullable = False                        ),
    Column('transCust',          Integer,      ForeignKey('customers.custId')          ),
    Column('transAddition',      Float,        ColumnDefault(0),   nullable = False    ),
    Column('transSubtraction',   Float,        ColumnDefault(0),   nullable = False    ),
    Column('transTax',           Float,        ColumnDefault(0),   nullable = False    ),
    Column('transShipDate',      Date,         nullable = True                         ),
    Column('transFOB',           Unicode(50),  nullable = True                         ),
    Column('transShipVia',       Unicode(100), nullable = True                         ),
    Column('transPermanent',     Boolean,      ColumnDefault(0)                        ),
    Column('transDesc',          Unicode(200), nullable = True                         )
#    Column('transSell',          Boolean,      ColumnDefault(0)                        ),
#    Column('transLastEdit',      Date,         nullable = True                         )
)

exchanges = Table('exchanges', meta,
    Column('exchngId',          Integer,        primary_key = True                      ),
    Column('exchngNo',          Integer,        nullable = False                        ),
    Column('exchngProduct',     Integer,        ForeignKey('products.id')               ),
    Column('exchngQnty',        Float,          ColumnDefault(0),   nullable = False    ),
    Column('exchngUntPrc',      Float,          ColumnDefault(0),   nullable = False    ),
    Column('exchngUntDisc',     Float,          ColumnDefault(0),   nullable = False    ),
    Column('exchngTransId',     Integer,        ForeignKey('transactions.transId')      ),
    Column('exchngDesc',        Unicode(200),   nullable = True                         )
)

payments = Table('payments', meta,
    Column('paymntId',          Integer,      primary_key = True                      ),
    Column('paymntNo',          Integer,      nullable = False                        ),
    Column('paymntDueDate',     Date,         nullable = False                        ),
    Column('paymntBank',        Unicode(100), nullable = True                         ),
    Column('paymntSerial',      Unicode(50),  nullable = True                         ),
    Column('paymntAmount',      Float,        ColumnDefault(0),   nullable = False    ),
    Column('paymntPayer',       Integer,      ForeignKey('customers.custId')          ),
    Column('paymntWrtDate',     Date,         nullable = True                         ),
    Column('paymntDesc',        Unicode(200), nullable = True                         ),
    Column('paymntTransId',     Integer,      ForeignKey('transactions.transId')      ),
    Column('paymntTrckCode',    Unicode,      nullable = True                         )
#    Column('paymntChq',         Unicode,      nullable = True                         )
)

cheques = Table('cheques', meta,
    Column('chqId',          Integer,      primary_key = True                      ),
    Column('chqAmount',      Float,        ColumnDefault(0),                  nullable = False ),
    Column('chqWrtDate',     Date,         nullable = False                        ),
    Column('chqDueDate',     Date,         nullable = False                        ),
    Column('chqBank',        Unicode(50),  nullable = True                         ),
    Column('chqAccount',     Integer,      ForeignKey('bankAccounts.accId'),  nullable = True  ),
    Column('chqSerialNo',    String,       nullable = False                        ),
    Column('chqStatus',      String,       nullable = False                        ),
    Column('chqPaid',        Boolean,      ColumnDefault(0),   nullable = False    ),
    Column('chqCust',        Integer,      ForeignKey('customers.custId')          ),
    Column('chqSpent',       Boolean,      ColumnDefault(0),   nullable = False    ),
    Column('chqTransId',     Integer,      ForeignKey('transactions.transId')      ),
    Column('chqDesc',        Unicode(200), nullable = True                         )
)

custGroups = Table('custGroups', meta,
    Column('custGrpId',      Integer,      primary_key = True  ),
    Column('custGrpCode',    String,       nullable = False    ),
    Column('custGrpName',    Unicode(50),  nullable = False    ),
    Column('custGrpDesc',    Unicode(200), nullable = True     )
)

customers = Table('customers', meta,
    Column('custId',           Integer,      primary_key = True  ),
    Column('custCode',         String,       nullable = False    ),
    Column('custName',         Unicode(100), nullable = False    ),
    Column('custPhone',        String,       nullable = True     ),
    Column('custCell',         String,       nullable = True     ),
    Column('custFax',          String,       nullable = True     ),
    Column('custAddress',      Unicode(100), nullable = True     ),
    Column('custEmail',        String,       nullable = True     ),
    Column('custEcnmcsCode',   String,       nullable = True     ),
    Column('custWebPage',      String,       nullable = True     ),
    Column('custResposible',   Unicode(50),  nullable = True     ),
    Column('custConnector',    Unicode(50),  nullable = True     ),
    Column('custGroup',        Integer,      ForeignKey('custGroups.custGrpId')),
    Column('custDesc',         Unicode(200), nullable = True     ),
    Column('custBalance',      Float,        ColumnDefault(0),      nullable = False  ),
    Column('custCredit',       Float,        ColumnDefault(0),      nullable = False  ),
    Column('custRepViaEmail',  Boolean,      ColumnDefault(False),  nullable = False  ),
    Column('custAccName1',     Unicode(50),  nullable = True     ),
    Column('custAccNo1',       String,       nullable = True     ),
    Column('custAccBank1',     Unicode(50),  nullable = True     ),
    Column('custAccName2',     Unicode(50),  nullable = True     ),
    Column('custAccNo2',       String,       nullable = True     ),
    Column('custAccBank2',     Unicode(50),  nullable = True     ),
    Column('custTypeBuyer',    Boolean,      ColumnDefault(True),   nullable = False  ),
    Column('custTypeSeller',   Boolean,      ColumnDefault(True),   nullable = False  ),
    Column('custTypeMate',     Boolean,      ColumnDefault(False),  nullable = False  ),
    Column('custTypeAgent',    Boolean,      ColumnDefault(False),  nullable = False  ),
    Column('custIntroducer',   Unicode(50),  nullable = True     ),
    Column('custCommission',   String,       nullable = True     ),
    Column('custMarked',       Boolean,      ColumnDefault(False),  nullable = False  ),
    Column('custReason',       Unicode(200), nullable = True     ),
    Column('custDiscRate',     String,       nullable = True     )
)

bankAccounts = Table('bankAccounts', meta,
    Column('accId',           Integer,      primary_key = True  ),
    Column('accName',         Unicode(100), nullable = False    ),
    Column('accNumber',       String,       nullable = False    ),
    Column('accType',         String,       nullable = True     ),
    Column('accOwner',        Unicode(50),  nullable = True     ),
    Column('accBank',         Unicode(50),  nullable = True     ),
    Column('accBankBranch',   Unicode(50),  nullable = True     ),
    Column('accBankAddress',  Unicode(100), nullable = True     ),
    Column('accBankPhone',    String,       nullable = True     ),
    Column('accBankWebPage',  String,       nullable = True     ), #TODO change to unicode
    Column('accDesc',         Unicode(200), nullable = True     )
)

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata
    meta.bind = migrate_engine

    products.create(      checkfirst=True)
    groups.create(        checkfirst=True)
    transactions.create(  checkfirst=True)
    exchanges.create(     checkfirst=True)
    payments.create(      checkfirst=True)
    cheques.create(       checkfirst=True)
    custGroups.create(    checkfirst=True)
    customers.create(     checkfirst=True)
    bankAccounts.create(  checkfirst=True)
    logging.debug("upgrade to 2")

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine

    products.drop()
    groups.drop()
    transactions.drop()
    exchanges.drop()
    payments.drop()
    cheques.drop()
    custGroups.drop()
    customers.drop()
    bankAccounts.drop()
    print("downgrade to 1")
    

