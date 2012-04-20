# -*- coding: utf-8 -*-
import class_subject
import dbconfig
from share import share
from database import BankAccounts
from database import BankNames

from sqlalchemy.orm.util import outerjoin
from sqlalchemy.orm.query import aliased
from sqlalchemy.sql.functions import *

config = share.config
## \defgroup Controller
## @{

class BankAccountsClass:
    def __init__(self):
        pass

    def get_bank_names(self):
        return config.db.session.query(BankNames).select_from(BankNames).all()

    def get_account(self, id):
        return config.db.session.query(BankAccounts).select_from(BankAccounts).filter(BankAccounts.accId == id).first()

    def get_all_accounts(self):
        return config.db.session.query(BankAccounts).select_from(BankAccounts).order_by(BankAccounts.accBank).all()

    def get_bank_id(self, name):
        return config.db.session.query(BankNames).select_from(BankNames).filter(BankNames.Name == unicode(name)).first().Id

    def get_bank_name(self, id):
        return config.db.session.query(BankNames).select_from(BankNames).filter(BankNames.Id == id).first().Name

    def add_bank(self, bank_name):
        bank_name = unicode(bank_name)
        query = config.db.session.query(BankNames).select_from(BankNames).filter(BankNames.Name == bank_name).first()
        if query == None:
            config.db.session.add(BankNames(bank_name))
            config.db.session.commit()

    def add_account(self, id, name, number, type, owner, bank, branch, address, phone, webpage, desc):
        name    = unicode(name)
        number  = unicode(number)
        owner   = unicode(owner)
        bank    = unicode(bank)
        branch  = unicode(branch)
        address = unicode(address)
        phone   = unicode(phone)
        webpage = unicode(webpage)
        desc    = unicode(desc)

        bank_id = config.db.session.query(BankNames).select_from(BankNames).filter(BankNames.Name == bank).first().Id

        if id == -1:
            bank_account = BankAccounts(name, number, type, owner, bank_id, branch, address, phone, webpage, desc)
            config.db.session.add(bank_account)
            sub = class_subject.Subjects()
            dbconf = dbconfig.dbConfig()
            sub.add(dbconf.get_int('bank'), name, str(bank_account.accId).rjust(2, '0'))
        else:
            query = config.db.session.query(BankAccounts).select_from(BankAccounts)
            query = query.filter(BankAccounts.accId == id)
            query.update( {BankAccounts.accName        : name,
                           BankAccounts.accNumber      : number,
                           BankAccounts.accType        : type,
                           BankAccounts.accOwner       : owner,
                           BankAccounts.accBank        : bank_id,
                           BankAccounts.accBankBranch  : branch,
                           BankAccounts.accBankAddress : address,
                           BankAccounts.accBankPhone   : phone,
                           BankAccounts.accBankWebPage : webpage,
                           BankAccounts.accDesc        : desc})
        config.db.session.commit()

        if id == -1:
            return bank_account.accId
        return id

    ## Delete account from databaSE
    #
    ## @param Integer bank account id
    def delete_account(self, id):
        config.db.session.query(BankAccounts).filter(BankAccounts.accId == id).delete()
        config.db.session.commit()

## @}
