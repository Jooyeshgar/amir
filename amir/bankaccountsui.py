# -*- coding: utf-8 -*-
from . import class_bankaccounts
from . import customers
from . import helpers
from .share import share
from .database import BankAccounts
from .database import Customers

import glib
from gi.repository import Gtk

import sys
if sys.version_info > (3,):
    unicode = str

config = share.config

## \defgroup UserInterface
## @{

## User Interface for create/edit/select a bank account.
class BankAccountsUI:
    ## initialize
    #
    # @param background GtkFixed
    def __init__(self, background):
        self.main_window_background = background

        self.bank_names_count = 0
        self.owner_id = -1

        self.builder = helpers.get_builder('bankaccounts')
        self.builder.connect_signals(self)

        self.bankaccounts_class = class_bankaccounts.BankAccountsClass()

        combo = self.builder.get_object('bank_names_combo')
        model = Gtk.ListStore(str)
        combo.set_model(model)

        cell = Gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 0)

        for item in self.bankaccounts_class.get_bank_names():
            iter = model.append()
            model.set(iter, 0, item.Name)
            self.bank_names_count+=1

        combo = self.builder.get_object('account_types_combo')
        model = Gtk.ListStore(str)
        combo.set_model(model)

        cell = Gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 0)

        for item in (_("Current Account"), _("Savings Account")):
            iter = model.append()
            model.set(iter, 0, item)

        treeview = self.builder.get_object('treeview')
        model = Gtk.ListStore(str, str, str, str, str, str)
        treeview.set_model(model)

        column = Gtk.TreeViewColumn(_('Id'), Gtk.CellRendererText(), text=0)
        treeview.append_column(column)
        column = Gtk.TreeViewColumn(_('Account Name'), Gtk.CellRendererText(), text=1)
        treeview.append_column(column)
        column = Gtk.TreeViewColumn(_('Number'), Gtk.CellRendererText(), text=2)
        treeview.append_column(column)
        column = Gtk.TreeViewColumn(_('Owner'), Gtk.CellRendererText(), text=3)
        treeview.append_column(column)
        column = Gtk.TreeViewColumn(_('Type'), Gtk.CellRendererText(), text=4)
        treeview.append_column(column)
        column = Gtk.TreeViewColumn(_('Bank Name'), Gtk.CellRendererText(), text=5)
        treeview.append_column(column)

    ## List all accounts in a window
    #
    # User can add/delete/edit accounts from here
    def show_accounts(self):
        window = self.builder.get_object('general_window')
        window.resize(600, 400)

        accounts = self.bankaccounts_class.get_all_accounts()
        model = self.builder.get_object('treeview').get_model()
        model.clear()
        for account in accounts:
            iter = model.append()
            if account.accType == 0:
                accType = _("Current Account")
            else:
                accType = _("Savings Account")
            accBank = self.bankaccounts_class.get_bank_name(account.accBank)
            model.set(iter, 0, unicode(account.accId), 1, account.accName, 2, unicode(account.accNumber), 3, account.accOwner, 4, accType, 5, accBank)
        window.show_all()
    #add acount
    def add_account(self, id=-1):
        if id > 0:
            account = self.bankaccounts_class.get_account(id)
        else:
            account = BankAccounts('', '', 0, '', 1, '', '', '', '', '')
        self.builder.get_object('account_name').set_text(account.accName)
        self.builder.get_object('account_number').set_text(account.accNumber)
        self.builder.get_object('account_owner').set_text(account.accOwner)
        self.builder.get_object('bank_branch').set_text(account.accBankBranch)
        self.builder.get_object('bank_address').set_text(account.accBankAddress)
        self.builder.get_object('bank_phone').set_text(account.accBankPhone)
        self.builder.get_object('bank_webpage').set_text(account.accBankWebPage)
        self.builder.get_object('desc').set_text(account.accDesc)
        self.builder.get_object('account_types_combo').set_active(account.accType)
        self.builder.get_object('bank_names_combo').set_active(account.accBank-1)
        # else:
        #     c = 0
        #     bank_name = self.bankaccounts_class.get_bank_name(account.accBank)
        #     combo_box = self.builder.get_object('bank_names_combo')
        #     combo_box.set_active(c)
        #     model = combo_box.get_model()
        #     iter  = combo_box.get_active_iter()
        #     while iter != None:
        #         if model.get_value(iter, 0) == bank_name:
        #             break
        #         else:
        #             c+=1
        #             self.builder.get_object('bank_names_combo').set_active(c)
        #             iter  = combo_box.get_active_iter()

        self.selected_id = id
        window = self.builder.get_object('add_window')
        window.resize(600, 1)
        window.show_all()

    def on_add_account_clicked(self, sender):
        self.add_account()

    def on_delete_account_clicked(self, sender):
        treeview = self.builder.get_object('treeview')
        selection = treeview.get_selection()
        model, iter = selection.get_selected()
        if iter == None:
            return
        id = model.get_value(iter, 0)
        model.remove(iter)
        self.bankaccounts_class.delete_account(id)

    def on_edit_account_clicked(self, sender):
        treeview = self.builder.get_object('treeview')
        selection = treeview.get_selection()
        model, iter = selection.get_selected()
        if iter == None:
            return
        id = model.get_value(iter, 0)
        self.add_account(id)

    def on_treeview_row_activated(self, treeview, path, column):
        selection = treeview.get_selection()
        model, iter = selection.get_selected()
        if iter == None:
            return
        id = model.get_value(iter, 0)
        self.add_account(id)

    def on_general_window_destroy(self, window):
        self.builder.get_object('general_window').hide()

    def on_add_bank_clicked(self, sender):
        model = self.builder.get_object('bank_names_combo').get_model()
        self.bankaccounts_class.addNewBank(model)


    def on_add_window_delete_event(self, window, event):
        window.hide()
        return True

    def on_save_clicked(self, button):
        id = self.selected_id

        msg = ''
        account_name = self.builder.get_object('account_name').get_text()
        account_number = self.builder.get_object('account_number').get_text()
        account_type = self.builder.get_object('account_types_combo').get_active()
        account_owner = self.builder.get_object('account_owner').get_text()
        bank_id = self.builder.get_object('bank_names_combo').get_active()    # bankName Id

        if len(account_name) == 0:
            msg+= 'Account Name Can not be empty\n'
        if len(account_number) == 0:
            msg+= 'Account Number Can not be empty\n'
        if len(account_owner) == 0:
            msg+= 'Account Owner Can not be empty\n'
        if account_type == -1:
            msg+= 'Select an account type\n'
        if bank_id == None:
            msg+= 'Select a Bank\n'

        if len(msg):
            dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, msg)
            dialog.run()
            dialog.destroy()
            return

        bank_id += 1
        result = self.bankaccounts_class.add_account(id,
                account_name,
                account_number,
                account_type,
                account_owner,
                bank_id,
                self.builder.get_object('bank_branch').get_text(),
                self.builder.get_object('bank_address').get_text(),
                self.builder.get_object('bank_phone').get_text(),
                self.builder.get_object('bank_webpage').get_text(),
                self.builder.get_object('desc').get_text())
        if result > 0:
            config.db.session.commit()
            window = self.builder.get_object('add_window').hide()
            share.mainwin.silent_daialog(_('successfully added.') )
            # infobar = Gtk.InfoBar()
            # label = Gtk.Label(label='successfully added.')
            # infobar.get_content_area().add(label)
            # width , height = self.main_window_background.window.get_size()
            # infobar.set_size_request(width, -1)
            # self.main_window_background.put(infobar ,0 , 0)
            # infobar.show_all()

            model = self.builder.get_object('treeview').get_model()
            if id == -1:
                iter = model.append()
            else:
                iter = model.get_iter_first()
                while iter != None:
                    if model.get_value(iter, 0) == id:
                        break
                    else:
                        iter = model.iter_next(iter)
            if account_type == 0:
                accType = 'جاری'
            else:
                accType = 'حساب پس انداز'
            bank_name= self.bankaccounts_class.get_bank_name(bank_id)
            model.set(iter, 0, unicode(result), 1, account_name, 2, account_number, 3, account_owner, 4, accType, 5, bank_name)
           # glib.timeout_add_seconds(3, lambda w: w.destroy(), infobar)
        else:
            config.db.session.rollback()
## @}

