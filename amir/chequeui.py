import class_bankaccounts
import class_cheque
import dateentry
import decimalentry
import helpers
from share import share
from database import Cheque
import gtk

config = share.config

## \defgroup UserInterface
## @{

class ChequeUI:
    def __init__(self, non_cash_label=None, spend_label = None):
        ## A list contains information about new cheques
        #
        # to remove all cheques for reseting form cheques_ui_obj.new_cheques = []
        self.cheque_class = class_cheque.ClassCheque()
        self.new_cheques = []
        #self.is_edit is a var that check the form called by add function or edit function
        ## a list contains informations about selected cheques for spending
        #self.spend_cheques only keep serial of cheque and values
        self.spend_cheques = []
        self.is_edit = 0
        self.non_cash_payment_label = non_cash_label
        self.spend_label = spend_label
        
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

        model = gtk.ListStore(str, str, str, str, str, str, str)
        treeview = self.builder.get_object('list_cheque_treeview')
        treeview.set_model(model)

        column = gtk.TreeViewColumn(_("Customer"), gtk.CellRendererText(), text=0)
        treeview.append_column(column)
        column = gtk.TreeViewColumn(_("Bank Account"), gtk.CellRendererText(), text=1)
        treeview.append_column(column)
        column = gtk.TreeViewColumn(_("Bank/Branch"), gtk.CellRendererText(), text=2)
        treeview.append_column(column)
        column = gtk.TreeViewColumn(_("Serial"), gtk.CellRendererText(), text=3)
        treeview.append_column(column)
        column = gtk.TreeViewColumn(_("Amount"), gtk.CellRendererText(), text=4)
        treeview.append_column(column)
        self.new_cheques = []
        column = gtk.TreeViewColumn(_("Due Date"), gtk.CellRendererText(), text=5)
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
    def list_cheques(self, mode, is_spend_cheque = 0):
        self.mode = mode
        treeviwe = self.builder.get_object('list_cheque_treeview')
        model = self.builder.get_object('list_cheque_treeview').get_model()
        model.clear()
        if(is_spend_cheque == 1):
            treeviwe.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
            selection = treeviwe.get_selection()
            self.builder.get_object('add_cheque').set_sensitive(False)
            self.builder.get_object('edit_cheque').set_sensitive(False)
            self.builder.get_object('delete_cheque').set_sensitive(False)
            self.builder.get_object('button1').set_sensitive(True)
            statusbar = self.builder.get_object('statusbar1')
            context_id = statusbar.get_context_id('statusbar')
            statusbar.push(context_id,_('Use Ctrl to select multiply'))
            spendable_cheques = self.cheque_class.get_spendable_cheques()
            for info , b_info in spendable_cheques:
                iter = model.append()
                if b_info == None:
                    model.set(iter,0, 'Customer Name', 1, None,2, unicode(info.chqNoteBookId),3, unicode(info.chqSerial),4, unicode(info.chqAmount),5, unicode(info.chqDueDate))
                else:
                    model.set(iter,0, 'Customer Name', 1, unicode(b_info.accName),2, unicode(info.chqNoteBookId),3, unicode(info.chqSerial),4, unicode(info.chqAmount),5, unicode(info.chqDueDate))
                for sp_ch in self.spend_cheques:
                    if info.chqSerial == unicode(sp_ch):
                        selection.select_iter(iter)
        else:
            treeviwe.get_selection().set_mode(gtk.SELECTION_SINGLE)
            self.builder.get_object('add_cheque').set_sensitive(True)
            self.builder.get_object('edit_cheque').set_sensitive(True)
            self.builder.get_object('delete_cheque').set_sensitive(True)
            self.builder.get_object('button1').set_sensitive(False)
            statusbar = self.builder.get_object('statusbar1')
            context_id = statusbar.get_context_id('statusbar')
            statusbar.remove_message(context_id,1)
            for info in self.new_cheques:
                iter = model.append()
                model.set(iter, 0, 'Customer Name', 1, info['bank_account_name'],
                                2, '%s/%s' % (info['bank_name'], info['branch_name']) ,
                                3, info['serial'], 4, info['amount'], 5, info['due_date'])

        w = self.builder.get_object('list_cheque_window')
        w.set_position(gtk.WIN_POS_CENTER)
        w.set_size_request(700,400)
        w.show_all()

    ## list cheques you are going to spend
    #
    # if you want to spend a list of cheques (more than one) you should use this.
    # it shows a list of selected cheques in a window.
    # there is an add button to selected new cheques for spending.
    # remember to call ChequeUI::save to save to database or you will lose everything.
    def list_spend_cheque(self):
        model = self.builder.get_object('list_cheque_treeview').get_model()
        model.clear
        

    ## show histroy of cheque.
    #
    # there is a text entry in window so user can enter cheque id
    def show_history(self):
        pass

    ## Save datas to database.
    #
    # do not call any other function after this step.
    def save(self):
        self.cheque.save()

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
    
    def on_destroy(self, window):
        window.destroy()

    def update_non_cash_payment_label(self):
        s = 0
        for item in self.new_cheques:
            s += item['amount']

        if self.non_cash_payment_label != None:
            self.non_cash_payment_label.set_text(str(s))
        else:
            print 'None'
    
    def update_spend_cheque_label(self,sp_cash):
        if self.spend_label != None:
            self.spend_label.set_text(str(sp_cash))
    ## Signal Handler (When User Clicks On Add in list_cheque_window) 
    def on_add_cheque_clicked(self, sender=None, info=None):
        self.is_edit = 0
        print info
        self.builder.get_object('add_edit').set_label('Add')
        self.bank_account_id = 0
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
        self.builder.get_object('bank').set_sensitive(not m)
        self.builder.get_object('branch').set_sensitive(not m)
        if info!= None:
            self.is_edit = 1
            self.builder.get_object('cheque_serial').set_text(unicode(info['serial']))
            self.amount_entry.set_text(unicode(info['amount']))
            self.builder.get_object('bank_accounts').set_active(-1)
            self.builder.get_object('bank').set_text(unicode(info['bank'])) 
            self.builder.get_object('branch').set_text(unicode(info['branch'])) 
            self.builder.get_object('desc').get_buffer().set_text(unicode(info['desc']))
            self.amount_entry.set_text('0')
            self.builder.get_object('add_edit').set_label('Edit')
            if m:
                c = 0
                bank_name = info['bank_account_id']
                combo_box = self.builder.get_object('bank_accounts')
                combo_box.set_active(c)
                model = combo_box.get_model()
                iter  = combo_box.get_active_iter()
                while iter != None:
                    if model.get_value(iter, 0) == bank_name:
                        break
                    else:
                        c+=1
                        self.builder.get_object('bank_names_combo').set_active(c)
                        iter  = combo_box.get_active_iter()
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
                break
        self.new_cheques.remove(item)
        model.remove(iter)
        self.update_non_cash_payment_label()
    def on_edit_cheque_clicked(self, button):
        treeviwe = self.builder.get_object('list_cheque_treeview')
        selection = treeviwe.get_selection()
        model, iter = selection.get_selected()
        if iter == None:
            return
        found = None
        for item in self.new_cheques:
            if item['serial'] == model.get_value(iter,3):
                found = item
        self.on_add_cheque_clicked(None,found)
    
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
        info['bank_account_name'] = self.bank_account_name
        info['bank_account_id'] = self.bank_account_id
        info['bank_name'] = self.builder.get_object('bank').get_text()
        info['branch_name'] = self.builder.get_object('branch').get_text()
        info['status'] = 1 if self.mode == 'our' else 4

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
            msg += 'Amount is wrong\n'
        if self.mode == 'our' and info['bank_account_id'] == None:
            msg += 'Select a bank account\n'

        if len(msg):
            dialog = gtk.MessageDialog(buttons=gtk.BUTTONS_OK, message_format=msg)
            dialog.run()
            dialog.destroy()
            return
        is_repeated = 0
        for ch in self.new_cheques:
            if ch['serial'] == info['serial']:
                is_repeated = 1
                break
        #check if the subprogram called by edit button
        treeview = self.builder.get_object('list_cheque_treeview')
        selection = treeview.get_selection()
        model, iter = selection.get_selected()
        print self.is_edit
        if self.is_edit == 1 :
            self.on_delete_cheque_clicked(None)

        self.new_cheques.append(info)

        model = self.builder.get_object('list_cheque_treeview').get_model()

        iter = model.append()
        model.set(iter, 0, 'customer_name', 1, info['bank_account_name'],
                        2, '%s/%s' % (info['bank_name'], info['branch_name']) ,
                        3, info['serial'], 4, info['amount'], 5, info['due_date'])
        self.update_non_cash_payment_label()
        self.builder.get_object('add_cheque_window').emit('delete_event', None)
        print self.new_cheques
    def on_select_spendchequ_ckicked(self,button):
        selected = {}
        self.sp_cash = 0
        def foreach(model,path,iter,selected):
            selected['amount'] = float(model.get_value(iter,4))
            self.sp_cash += float(model.get_value(iter,4))
            selected['serial'] = (model.get_value(iter,3))
            self.spend_cheques.append(selected)
        treeview = self.builder.get_object('list_cheque_treeview')
        selection = treeview.get_selection()
        selection.selected_foreach(foreach,selected)
        self.update_spend_cheque_label(self.sp_cash)
        self.cheque_class.sp_cheques = self.spend_cheques
        
        #
    def on_list_cheque_window_delete_event(self, window, event):
        window.hide_all()
        return True

## @}
