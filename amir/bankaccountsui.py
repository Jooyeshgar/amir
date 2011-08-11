# -*- coding: utf-8 -*-
import class_bankaccounts
import customers
import helpers
from amirconfig import config
from database import Customers

import glib
import gtk

class BankAccountsUI:
    def __init__(self, background):
        self.main_window_background = background

        self.bank_names_count = 0
        self.owner_id = -1

        self.builder = helpers.get_builder('bankaccounts')
        self.builder.connect_signals(self)

        self.bankaccounts_class = class_bankaccounts.BankAccountsClass()
        
        combo = self.builder.get_object('bank_names_combo')
        model = gtk.ListStore(str)
        combo.set_model(model)

        cell = gtk.CellRendererText()
        combo.pack_start(cell)
        combo.add_attribute(cell, 'text', 0)

        for item in self.bankaccounts_class.get_bank_names():
            iter = model.append()
            model.set(iter, 0, item.Name)
            self.bank_names_count+=1

        combo = self.builder.get_object('account_types_combo')
        model = gtk.ListStore(str)
        combo.set_model(model)

        cell = gtk.CellRendererText()
        combo.pack_start(cell)
        combo.add_attribute(cell, 'text', 0)

        for item in ('جاری', 'حساب پس انداز'):
            iter = model.append()
            model.set(iter, 0, item)

    def show_accounts(self):
        window = self.builder.get_object('general_window')
        window.show_all()

    def add_account(self):
        self.builder.get_object('account_name').set_text('')
        self.builder.get_object('account_number').set_text('')
        self.builder.get_object('account_owner').set_text('')
        self.builder.get_object('account_types_combo').set_active(-1)
        self.builder.get_object('bank_names_combo').set_active(-1)
        self.builder.get_object('bank_branch').set_text('')
        self.builder.get_object('bank_address').set_text('')
        self.builder.get_object('bank_phone').set_text('')
        self.builder.get_object('bank_webpage').set_text('')
        self.builder.get_object('desc').set_text('')

        window = self.builder.get_object('add_window')
        window.resize(600, 1)
        window.show_all()

    def on_add_account_clicked(self, sender):
        self.add_account()

    def on_general_window_destroy(self, window):
        self.builder.get_object('general_window').destroy()

    def on_add_bank_clicked(self, sender):
        dialog = gtk.Dialog(None, None,
                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                     (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                      gtk.STOCK_OK, gtk.RESPONSE_OK))
        label = gtk.Label('Bank Name:')
        entry = gtk.Entry()
        dialog.vbox.pack_start(label, False, False)
        dialog.vbox.pack_start(entry, False, False)
        dialog.show_all()
        result = dialog.run()
        text = entry.get_text()
        if result == gtk.RESPONSE_OK and len(text) != 0:
                combo = self.builder.get_object('bank_names_combo')
                model = combo.get_model()

                iter = model.append()
                model.set(iter, 0, text)
                self.bank_names_count+=1
                combo.set_active(self.bank_names_count-1)
                #TODO add to database
        dialog.destroy()

    def on_add_window_destroy(self, window):
        window.hide()

    def on_save_clicked(self, button):
        msg = ''
        account_name = self.builder.get_object('account_name').get_text()
        account_number = self.builder.get_object('account_number').get_text()
        account_type = self.builder.get_object('account_types_combo').get_active()
        account_owner = self.builder.get_object('account_owner').get_text()
        bank_name = self.builder.get_object('bank_names_combo').get_active_text()

        if len(account_name) == 0:
            msg+= 'Account Name Can not be empty\n'
        if len(account_number) == 0:
            msg+= 'Account Number Can not be empty\n'
        if len(account_owner) == 0:
            msg+= 'Account Owner Can not be empty\n'
        if account_type == -1:
            msg+= 'Select an account type\n'
        if bank_name == None:
            msg+= 'Select a Bank\n'

        if len(msg):
            dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, msg)
            dialog.run()
            dialog.destroy()
            return

        result = self.bankaccounts_class.add_account(account_name,
                                                     account_number,
                                                     account_type,
                                                     account_owner,
                                                     bank_name,
                                                     self.builder.get_object('bank_branch').get_text(),
                                                     self.builder.get_object('bank_address').get_text(),
                                                     self.builder.get_object('bank_phone').get_text(),
                                                     self.builder.get_object('bank_webpage').get_text(),
                                                     self.builder.get_object('desc').get_text())
        if result:
            window = self.builder.get_object('add_window').hide()
            infobar = gtk.InfoBar()
            label = gtk.Label('successfully added.')
            infobar.get_content_area().add(label)
            width , height = self.main_window_background.window.get_size()
            infobar.set_size_request(width, -1)
            self.main_window_background.put(infobar ,0 , 0)
            infobar.show_all()

            glib.timeout_add_seconds(3, lambda w: w.destroy(), infobar)


