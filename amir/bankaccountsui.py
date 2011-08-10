# -*- coding: utf-8 -*-
import class_bankaccounts
import customers
import helpers
from amirconfig import config
from database import Customers

import gtk

class BankAccountsUI:
    def __init__(self):
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
        window = self.builder.get_object('add_window')
        window.resize(600, 1)
        window.show_all()

    def on_select_owner_clicked(self, sender):
        cust = customers.Customer()
        cust.connect('customer-selected', self.on_customer_selected)
        cust.viewCustomers(True)

    def on_customer_selected(self, customer, id, code):
        self.owner_id = id
        query = config.db.session.query(Customers).select_from(Customers)
        query = query.filter(Customers.custCode == code)
        self.builder.get_object('owner_entry').set_text(query.first().custName)
        customer.window.destroy()

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
                model.set(iter, 1, text)
                self.bank_names_count+=1
                combo.set_active(self.bank_names_count-1)
        dialog.destroy()

    def on_add_window_destroy(self, window):
        window.hide()

    def on_save_clicked(self, button):
        msg = ''
        account_name = self.builder.get_object('account_name').get_text()
        account_number = self.builder.get_object('account_number').get_text()
        account_type = self.builder.get_object('account_types_combo').get_active()
        bank_name = self.builder.get_object('bank_names_combo').get_active()

        if len(account_name) == 0:
            msg+= 'Account Name Can not be empty\n'
        if len(account_number) == 0:
            msg+= 'Account Number Can not be empty\n'
        if account_type == -1:
            msg+= 'Select an account type\n'
        if bank_name == -1:
            msg+= 'Select a Bank\n'
        if self.owner_id == -1:
            msg+= 'Select Account owner\n'

        if len(msg):
            dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, msg)
            dialog.run()
            dialog.destroy()
