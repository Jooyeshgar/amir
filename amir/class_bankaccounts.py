# -*- coding: utf-8 -*-
from . import class_subject
from . import dbconfig
from .share import share
from .database import BankAccounts
from .database import BankNames
from .database import Subject

from sqlalchemy.orm.util import outerjoin
from sqlalchemy.orm.query import aliased
from sqlalchemy.sql.functions import *
from gi.repository import Gtk

import sys
if sys.version_info > (3,):
    unicode = str

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
        return config.db.session.query(BankAccounts).select_from(BankAccounts).all()

    def get_bank_id(self, name):
        bank = config.db.session.query(BankNames).select_from(BankNames).filter(BankNames.Name == unicode(name)).first()
        bank_id  = None
        if bank:
            bank_id = bank.Id
        return bank_id

    def get_bank_name(self, id):
        bank = config.db.session.query(BankNames).select_from(BankNames).filter(BankNames.Id == id).first()
        bank_name = None
        if bank:
            bank_name = bank.Name
        return bank_name

    def add_bank(self, bank_name):
        bank_name = unicode(bank_name)
        query = config.db.session.query(BankNames).select_from(BankNames).filter(BankNames.Name == bank_name).first()
        if query == None:
            config.db.session.add(BankNames(bank_name))
            config.db.session.commit()

    def addNewBank (self , model):
        dialog = Gtk.Dialog(None, None,
                     Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                     (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                      Gtk.STOCK_OK, Gtk.ResponseType.OK))
        label = Gtk.Label(label='Bank Name:')
        entry = Gtk.Entry()
        dialog.vbox.pack_start(label, False, False,0)
        dialog.vbox.pack_start(entry, False, False,0)
        dialog.show_all()
        result = dialog.run()
        bank_name = entry.get_text()
        if result == Gtk.ResponseType.OK and len(bank_name) != 0:
                iter = model.append()
                model.set(iter, 0, bank_name)
                self.add_bank(bank_name)

        dialog.destroy()
    def add_account(self, id, name, number="", type=0, owner="", bank=1, branch="", address="", phone="", webpage="", desc=""):
        name    = unicode(name)
        number  = unicode(number)
        owner   = unicode(owner)
        bank    = unicode(bank)
        branch  = unicode(branch)
        address = unicode(address)
        phone   = unicode(phone)
        webpage = unicode(webpage)
        desc    = unicode(desc)

        bank_id = bank
        dbconf = dbconfig.dbConfig()
        if id == -1:
            bank_account = BankAccounts(name, number, type, owner, bank_id, branch, address, phone, webpage, desc)
            config.db.session.add(bank_account)
            config.db.session.commit()
            sub = class_subject.Subjects()
            # accountId = str(bank_account.accId)
            # accSubjectCode = accountId.rjust(3 - len(accountId)+1 , '0')
            sub.add(dbconf.get_int('bank'), name)
        else:
            query = config.db.session.query(BankAccounts).filter(BankAccounts.accId == id)
            prevName = query.first().accName
            q = config.db.session.query(Subject).filter(Subject.parent_id== (dbconf.get_int('bank')) ).filter(Subject.name==prevName)
            if q:
                q.update({Subject.name:name})
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


        if id == -1 and bank_account:
            return bank_account.accId
        return id

    ## Delete account from databaSE
    #
    ## @param Integer bank account id
    def delete_account(self, id):
        query = config.db.session.query(BankAccounts).filter(BankAccounts.accId == id).first()
        if query:
            accName = query.accName
        query.delete()
        bankSubject = dbconfig.dbConfig().get_int('bank')
        config.db.session.query(Subject).filter(Subject.parent_id==bankSubject).filter(Subject.name== accName).delete()
        config.db.session.commit()

## @}
