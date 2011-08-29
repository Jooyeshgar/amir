import class_bankaccounts
import dateentry
import decimalentry
import helpers
import customers
from amirconfig import config
from database import Customers

import gtk

## \defgroup UserInterface
## @{

class ChequeUI:
    def __init__(self, non_cash_label=None):
        ## A list contains information about new cheques
        self.new_cheques = []
        ## a list contains informations about selected cheques for spending
        self.spend_cheques = []

        self.non_cash_payment_label = non_cash_label

        self.mode = 'our'

        self.bank_accounts = class_bankaccounts.BankAccountsClass()

        # User Interface
        self.builder = helpers.get_builder('cheque')
        self.builder.connect_signals(self)

        self.amount_entry = decimalentry.DecimalEntry()
        self.write_date = dateentry.DateEntry()
        self.due_date = dateentry.DateEntry()
        
        add_table = self.builder.get_object('add_table')
        add_table.attach(self.amount_entry, 1, 2, 1, 2, gtk.EXPAND|gtk.FILL, gtk.SHRINK)
        add_table.attach(self.write_date , 1, 2, 3, 4, gtk.EXPAND|gtk.FILL, gtk.SHRINK)
        add_table.attach(self.due_date   , 1, 2, 4, 5, gtk.EXPAND|gtk.FILL, gtk.SHRINK)

        self.builder.get_object('list_cheque_window').resize(400, 1)
        self.builder.get_object('desc_frame').set_size_request(0, 100)

        model = gtk.ListStore(str, str, str, str, str, str)
        treeview = self.builder.get_object('list_cheque_treeview')
        treeview.set_model(model)

        column = gtk.TreeViewColumn("Customer"  , gtk.CellRendererText(), text=0)
        treeview.append_column(column)
        column = gtk.TreeViewColumn("Bank Account"  , gtk.CellRendererText(), text=1)
        treeview.append_column(column)
        column = gtk.TreeViewColumn("Bank/Branch"  , gtk.CellRendererText(), text=2)
        treeview.append_column(column)
        column = gtk.TreeViewColumn("Serial"  , gtk.CellRendererText(), text=3)
        treeview.append_column(column)
        column = gtk.TreeViewColumn("Amount"  , gtk.CellRendererText(), text=4)
        treeview.append_column(column)
        column = gtk.TreeViewColumn("Due Date", gtk.CellRendererText(), text=5)
        treeview.append_column(column)

        model = gtk.ListStore(str, str, str)
        combo = self.builder.get_object('bank_accounts')
        combo.set_model(model)

        cell = gtk.CellRendererText()
        cell.set_visible(False)
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 0)

        cell = gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 1)

        cell = gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 2)

    ## list cheques you are going to add/ or all cheques in database
    #
    # if you want to add a list of cheques (more than one) to database you should use this.
    # it shows a list of currently added cheques in a window.
    # there is an add button to append new cheques to the list.
    # remember to call ChequeUI::save to save to database or you will lose everything.
    # @param mode, 'our' -> if you want to add or show cheques created by you., 'other'
    def list_cheques(self, mode):
        self.mode = mode

        model = self.builder.get_object('list_cheque_treeview').get_model()
        model.clear()

        for info in self.new_cheques:
            iter = model.append()
            model.set(iter, 0, info['customer_name'], 1, info['bank_account_name'],
                            2, '%s/%s' % (info['bank_name'], info['branch_name']) ,
                            3, info['serial'], 4, info['amount'], 5, info['due_date'])

        w = self.builder.get_object('list_cheque_window')
        w.set_position(gtk.WIN_POS_CENTER)
        w.show_all()

    ## list cheques you are going to spend
    #
    # if you want to spend a list of cheques (more than one) you should use this.
    # it shows a list of selected cheques in a window.
    # there is an add button to selected new cheques for spending.
    # remember to call ChequeUI::save to save to database or you will lose everything.
    def list_spend_cheque(self):
        pass

    ## show histroy of cheque.
    #
    # there is a text entry in window so user can enter cheque id
    def show_history(self):
        pass

    ## Save datas to database.
    #
    # do not call any other function after this step.
    def save(self):
        pass

    ## add a new cheque
    #
    # if you want to add a single cheque use this, else using ChequeUI::list_new_cheques for multiple cheques is recommended.
    #
    # \note you can use ChequeUI::new_cheque for adding multiple cheques too. (call ChequeUI::new_cheque for each cheque)
    # You can use ChequeUI::list_new_cheques to list cheques before saving.
    #
    # <b>Signal</b> new_cheque_selected
    #
    # <b>Signal Handler</b> (Window, dictionary of items)
    # @return GtkWindow
    def new_cheque(self):
        pass

    ## select a cheque to spend
    #
    # shows a list available cheque for spending to selecting a single cheque from that list.
    # if you want to spend multiple cheques ChequeUI::list_spend_cheque is recommended.
    # \note see ChequeUI::new_cheque
    #
    # <b>Signal</b> spend_cheque_selected
    #
    # <b>Signal Handler</b> (Window)
    # Signal Handler (Window, cheque_id)
    # @return GtkWindow
    def spend_cheque(self):
        pass

    def update_non_cash_payment_label(self):
        s = 0
        for item in self.new_cheques:
            s += item['amount']

        if self.non_cash_payment_label != None:
            self.non_cash_payment_label.set_text(str(s))
        else:
            print 'None'

    ## Signal Handler (When User Clicks On Add in list_cheque_window 
    def on_add_cheque_clicked(self, sender, info=None):
        self.customer_id = None
        self.customer_name = '---'

        self.bank_account_id = None
        self.bank_account_name = '---'

        w = self.builder.get_object('add_cheque_window')
        w.set_position(gtk.WIN_POS_CENTER)
        
        combo = self.builder.get_object('bank_accounts')
        model = combo.get_model()
        model.clear()

        for acc in self.bank_accounts.get_all_accounts():
            iter = model.append()
            string = '%s/%s' % (acc.accBankBranch, self.bank_accounts.get_bank_name(acc.accBank))
            model.set(iter, 0, acc.accId, 1, acc.accName, 2, string)

        m = (self.mode == 'our')
        self.builder.get_object('bank_accounts').set_sensitive(m)
        self.builder.get_object('customer_button').set_sensitive(not m)
        self.builder.get_object('bank').set_sensitive(not m)
        self.builder.get_object('branch').set_sensitive(not m)

        self.builder.get_object('cheque_serial').set_text('') 
        self.builder.get_object('bank_accounts').set_active(-1)
        self.builder.get_object('customer_name').set_text('') 
        self.builder.get_object('bank').set_text('') 
        self.builder.get_object('branch').set_text('') 
        self.builder.get_object('desc').get_buffer().set_text('')
        self.amount_entry.set_text('0')

        w.show_all()

    ## Signal Handler (When User Closes add Window)
    def on_add_cheque_window_delete_event(self, window, event):
        window.hide_all()
        return True

    ## Signal Handler (When User Clicks on cancel in add window)
    def on_cancel_add_clicked(self, button):
        self.builder.get_object('add_cheque_window').emit('delete_event', None)

    def on_delete_cheque_clicked(self, button):
        treeview = self.builder.get_object('list_cheque_treeview') 
        selection = treeview.get_selection()
        model, iter = selection.get_selected()

        if iter == None:
            return

        found = None
        for item in self.new_cheques:
            if item['serial'] == model.get_value(iter, 3):
                found = item
        self.new_cheques.remove(item)

        model.remove(iter)
        self.update_non_cash_payment_label()

    def on_edit_cheque_clicked(self, button):
        pass
    
    ## Signal Handler (When User Clicks on Add in add window to save new cheque)
    #
    # automatically updated list_cheque_window
    def on_confirm_add_clicked(self, button):
        info = {}
        info['serial'] = self.builder.get_object('cheque_serial').get_text()
        info['amount'] = self.amount_entry.get_float()
        info['write_date'] = self.write_date.getDateObject()
        info['due_date'] = self.due_date.getDateObject()
        info['bank'] = self.builder.get_object('bank').get_text()
        info['branch'] = self.builder.get_object('branch').get_text()
        info['customer_id'] = self.customer_id
        info['customer_name'] = self.customer_name
        info['bank_account_name'] = self.bank_account_name
        info['bank_account_id'] = self.bank_account_id
        info['bank_name'] = self.builder.get_object('bank').get_text()
        info['branch_name'] = self.builder.get_object('branch').get_text()

        buf = self.builder.get_object('desc').get_buffer()
        info['desc'] = buf.get_text(buf.get_start_iter(), buf.get_end_iter())

        combo = self.builder.get_object('bank_accounts')
        if self.mode == 'our' and combo.get_active() != -1:
            model = combo.get_model()
            iter =  combo.get_active_iter()
            info['bank_account_id'] = model.get_value(iter, 0)
            info['bank_account_name'] = model.get_value(iter, 1)
            

        msg = ''
        if info['serial'] == '':
            msg += 'Serial Number is Empty\n'
        if info['amount'] <=0:
            msg += 'Amount is wron\n'
        if self.mode == 'other' and info['customer_id'] == None:
            msg += 'Select a customer\n'
        if self.mode == 'our' and info['bank_account_id'] == None:
            msg += 'Select a bank account\n'

        if len(msg):
            dialog = gtk.MessageDialog(buttons=gtk.BUTTONS_OK, message_format=msg)
            dialog.run()
            dialog.destroy()
            return

        self.new_cheques.append(info)

        model = self.builder.get_object('list_cheque_treeview').get_model()

        iter = model.append()
        model.set(iter, 0, info['customer_name'], 1, info['bank_account_name'],
                        2, '%s/%s' % (info['bank_name'], info['branch_name']) ,
                        3, info['serial'], 4, info['amount'], 5, info['due_date'])
        self.update_non_cash_payment_label()
        self.builder.get_object('add_cheque_window').emit('delete_event', None)

    def on_customer_button_clicked(self, button):
        cust = customers.Customer()
        cust.connect('customer-selected', self.on_customer_selected)
        cust.viewCustomers(True)
        cust.window.set_position(gtk.WIN_POS_CENTER)

    def on_customer_selected(self, customer, id, code):
        customer.window.destroy()
        self.customer_id = id
        query = config.db.session.query(Customers).select_from(Customers)
        query = query.filter(Customers.custCode == code)
        self.customer_name = query.first().custName
        self.builder.get_object('customer_name').set_text(self.customer_name)

    def on_list_cheque_window_delete_event(self, window, event):
        window.hide_all()
        return True

## @}
