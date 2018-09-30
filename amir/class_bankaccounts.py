# -*- coding: utf-8 -*-
import class_subject
import dbconfig
from share import share
from database import BankAccounts
from database import BankNames

from sqlalchemy.orm.util import outerjoin
from sqlalchemy.orm.query import aliased
from sqlalchemy.sql.functions import *
from gi.repository import Gtk

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
        return config.db.session.query(BankNames).select_from(BankNames).filter(BankNames.Name == unicode(name)).first().Id

    def get_bank_name(self, id):
        return config.db.session.query(BankNames).select_from(BankNames).filter(BankNames.Id == id).first().Name

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

        #bank_id = config.db.session.query(BankNames).select_from(BankNames).filter(BankNames.Name == bank).first().Id
        bank_id = bank

        if id == -1:
            bank_account = BankAccounts(name, number, type, owner, bank_id, branch, address, phone, webpage, desc)
            config.db.session.add(bank_account)
            sub = class_subject.Subjects()
            dbconf = dbconfig.dbConfig()
            sub.add(dbconf.get_int('bank'), name, str(bank_account.accId).rjust(2, '0'))
        else:
            query = config.db.session.query(BankAccounts).filter(BankAccounts.accId == id)
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
