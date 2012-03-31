import chequeui
import class_cheque
import class_document
import customers
import dateentry
import dbconfig
import decimalentry
import helpers
import numberentry
import subjects
from amirconfig import config
from database import Subject
from database import Customers
from class_subject import Subjects
from utility import localizeNumber

import glib
import gtk

## \defgroup UserInterface
## @{

class AutomaticAccounting:
    type_names = (
        # 0 id, 1 name
        (0 , _('Get From Customer')),
        (1 , _('Pay To Customer')),
        (2 , _('Bank To Bank')),
        (3 , _('Cash To Bank')),
        (4 , _('Bank To Cash')),
        (5 , _('Bank Fee')),
        (6 , _('Transfer To Customer')),
        (7 , _('Investment')),
        (8 , _('Cost')),
        (9, _('Income')),
        (10, _('Removal')),
    )

    type_configs = {
        #0 non cash
        #1 discount
        #2 spend_cheque
        #3 from is subject?
        #4 to   is subject?
        #5 from key
        #6 to   key
        #    0    , 1    , 2    , 3    , 4    , 5          , 6
        0:  (True , True , False, False, True , None       , 'cash'),
        1:  (True , False, True , True , False, 'cash'     , None  ),
        2:  (True , False, False, True , True , 'bank'     , 'bank'),
        3:  (False, False, False, True , True , 'cash'     , 'bank'),
        4:  (True , False, False, True , True , 'bank'     , 'cash'),
        5:  (False, False, False, True , True , 'bank'     , 'bank-wage'), # 'to' is not changeable
        6:  (False, False, False, False, True , None       , 'bank'),
        7:  (True , False, True , True , True , 'partners' , 'cash,bank'),
        8:  (True , False, True , True , True , 'cash'     , 'cost'),
        9: (True , False, False, True , True , None       , 'cash,bank'),
        10: (True , False, True , True , True , 'cash,bank', 'partner'),
    }
    def __init__(self):
        self.mode = None
        self.liststore = None
        
        #self.main_window_background = background
        # Chosen Type
        self.type_index = None
        self.from_id = self.to_id = -1

        self.builder = helpers.get_builder('automaticaccounting')
        self.builder.connect_signals(self)

        self.chequeui = chequeui.ChequeUI(self.builder.get_object('non-cash-payment-label'),self.builder.get_object('spend-cheque-label'))
        # Date entry
        date_box = self.builder.get_object('date-box')
        self.date_entry = dateentry.DateEntry()
        date_box.pack_start(self.date_entry, False, False)
        self.current_time = self.date_entry.getDateObject()
        print self.current_time
        # type combo
        type_combo = self.builder.get_object('select-type')
        model = gtk.ListStore(str, str)
        type_combo.set_model(model)

        cell = gtk.CellRendererText()
        cell.set_visible(False)
        type_combo.pack_start(cell)
        type_combo.add_attribute(cell, 'text', 0)

        cell = gtk.CellRendererText()
        type_combo.pack_start(cell)
        type_combo.add_attribute(cell, 'text', 1)

        for item in self.type_names:
            iter = model.append()
            model.set(iter, 0, item[0], 1, item[1])

        # payment table
        table = self.builder.get_object('payment-table')

        self.cash_payment_entry = decimalentry.DecimalEntry()
        self.cash_payment_entry.connect('changed', self.on_cash_payment_entry_change)
        table.attach(self.cash_payment_entry, 1, 2, 0, 1)

        self.discount_entry = decimalentry.DecimalEntry()
        self.discount_entry.connect('changed', self.on_discount_entry_change)
        table.attach(self.discount_entry, 1, 2, 3, 4)

        # names table
        table = self.builder.get_object('names-table')

        self.from_entry = gtk.Entry()
        self.from_entry.set_sensitive(False)
        table.attach(self.from_entry, 1, 2, 0, 1)

        self.to_entry = gtk.Entry()
        self.to_entry.set_sensitive(False)
        table.attach(self.to_entry, 1, 2, 1, 2)

        self.total_credit_entry = decimalentry.DecimalEntry()
        self.total_credit_entry.connect('changed', self.on_total_credit_entry_change)
        table.attach(self.total_credit_entry, 1, 2, 2, 3)

        # choose first type
        type_combo.set_active(0)

    def on_type_change(self, combo):
        iter =  combo.get_active_iter()

        if iter == None:
            return
        
        self.chequeui.new_cheques = []
        self.chequeui.spend_cheques = []
        model = combo.get_model()
        index = model.get(iter, 0)[0]
        self.type_index = int(index)
        
        save_button = self.builder.get_object('save-button')
        
        non_cash, discount, spend_cheque = self.type_configs[self.type_index][:3]

        self.builder.get_object('discount-button').set_sensitive(discount)
        self.discount_entry.set_sensitive(discount)
        
        self.builder.get_object('list-cheque-button').set_sensitive(spend_cheque)
        self.builder.get_object('spend-cheque-label').set_sensitive(spend_cheque)

        self.builder.get_object('non-cash-payment-label').set_sensitive(non_cash)
        self.builder.get_object('non_cash_payment_button').set_sensitive(non_cash)

        self.cash_payment_entry.set_sensitive((non_cash or spend_cheque))

        self.from_entry.set_text("")
        self.to_entry.set_text("")
        self.cash_payment_entry.set_text('0')
        self.total_credit_entry.set_text('0')
        self.discount_entry.set_text('0')

        dbconf = dbconfig.dbConfig()

        if self.type_index == 5:
            self.builder.get_object('to-button').set_sensitive(False)
            query = config.db.session.query(Subject).select_from(Subject)
            query = query.filter(Subject.id == dbconf.get_int('bank-wage'))
            query = query.first()
            self.to_id =  query.id
            self.to_entry.set_text(query.name)
        else:
            self.builder.get_object('to-button').set_sensitive(True)

    def on_from_clicked(self, button):
        index  = self.type_index
        entry  = self.from_entry
        dbconf = dbconfig.dbConfig()

        if self.type_configs[self.type_index][3]:
            if self.type_configs[self.type_index][5] == None:
                sub = subjects.Subjects()
            else:
                keys = self.type_configs[self.type_index][5]
                parent_id=[]
                for key in keys.split(','):
                    parent_id+=dbconf.get_int_list(key)
                sub = subjects.Subjects(parent_id=parent_id)
            sub.connect('subject-selected',
                        self.on_subject_selected,
                        entry, False)
        else:
            cust = customers.Customer()
            cust.connect('customer-selected',
                         self.on_customer_selected,
                         entry, False)
            cust.viewCustomers(True)

    def on_to_clicked(self, button):
        entry = self.to_entry
        dbconf = dbconfig.dbConfig()

        if self.type_configs[self.type_index][4]:
            if self.type_configs[self.type_index][6] == None:
                sub = subjects.Subjects()
            else:
                keys = self.type_configs[self.type_index][6]
                parent_id=[]
                for key in keys.split(','):
                    parent_id+=dbconf.get_int_list(key)
                sub = subjects.Subjects(parent_id=parent_id)
            sub.connect('subject-selected',
                        self.on_subject_selected,
                        entry, True)
        else:
            cust = customers.Customer()
            cust.connect('customer-selected',
                         self.on_customer_selected,
                         entry, True)
            cust.viewCustomers(True)

    def on_total_credit_entry_change(self, entry):
        if not (self.type_configs[self.type_index][0] or self.type_configs[self.type_index][2]):
            self.cash_payment_entry.set_text(entry.get_text())
        self.on_cash_payment_entry_change(None)

    def on_discount_entry_change(self, entry):
        self.on_cash_payment_entry_change(None)

    def on_discount_clicked(self, button):
        dialog = gtk.Dialog("Discount percentage",
                            self.builder.get_object('general'),
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK)
                           )
        adj = gtk.Adjustment(0, 0, 100, 1, 1)
        spin = gtk.SpinButton(adj)

        hbox = gtk.HBox()
        hbox.pack_start(spin)
        hbox.pack_start(gtk.Label(' % '), False, False)
        hbox.show_all()

        dialog.vbox.pack_start(hbox, False, False)

        result = dialog.run()
        if result == gtk.RESPONSE_OK:
            val = spin.get_value()
            total = self.total_credit_entry.get_float()
            discount = (val*total)/100
            self.discount_entry.set_text(str(discount))

        dialog.destroy()

    def on_cash_payment_entry_change(self, entry):
        val1 = self.cash_payment_entry.get_float()
        val2 = float(unicode(self.builder.get_object('non-cash-payment-label').get_text()).replace('/', '.'))
        val3 = float(unicode(self.builder.get_object('spend-cheque-label').get_text()).replace('/','.'))
        discount = self.discount_entry.get_float()

        paid = val1+val2+val3+discount
        paid_label = self.builder.get_object('paid')
        paid_label.set_text(str(paid))

        total = self.total_credit_entry.get_float()
        r = total - (paid)
        mod = self.builder.get_object('mod')
        mod.set_text(str(r))

        self.check_save_button()

    def on_subject_selected(self, subject, id, code, name, entry, to):
        query = config.db.session.query(Subject).select_from(Subject)
        query = query.filter(Subject.code == code)
        if query.first().parent_id == 0:
            print 'You Can not select it'
            return

        if to:
            self.to_id = id
        else:
            self.from_id = id

        entry.set_text(name)
        subject.window.destroy()

    def on_customer_selected(self, customer, id, code, entry, to):
        id = config.db.session.query(Customers).select_from(Customers).filter(Customers.custId==id).first().custSubj
        if to:
            self.to_id = id
        else:
            self.from_id = id
        query = config.db.session.query(Customers).select_from(Customers)
        query = query.filter(Customers.custCode == code)
        entry.set_text(query.first().custName)
        customer.window.destroy()

    def check_save_button(self):
        save_button = self.builder.get_object('save-button')
        save_button.set_sensitive(False)

        if self.from_entry.get_text_length() == 0:
            return

        if self.to_entry.get_text_length() == 0 :
            return

        if self.total_credit_entry.get_float() == 0:
            return

        mod = self.builder.get_object('mod')
        if float(mod.get_text()) != 0:
            return

        save_button.set_sensitive(True)

    def on_non_cash_payment_button_clicked(self, button):
        if self.type_configs[self.type_index][3]:
            self.mode = 'our'
        else:
            self.mode = 'other'

        self.chequeui.list_cheques(self.mode)

    def on_spend_cheque_buttun_clicked(self,button):
        cl_cheque = class_cheque.ClassCheque()
        self.chequeui.list_cheques(None, 1)
        cl_cheque.save_cheque_history()
        
        
    def on_save_button_clicked(self, button):
        result = {}
        result['type']                  = self.type_index
        result['total_value']           = self.total_credit_entry.get_float()
        result['cash_payment']          = self.cash_payment_entry.get_float()
        result['non_cash_payment']      = self.builder.get_object('non-cash-payment-label').get_text()
        result['spend_cheque']          = self.builder.get_object('spend-cheque-label').get_text()
        result['discount']              = self.discount_entry.get_float()
        result['non-cash-payment-info'] = None # TODO: = non cash payment infos
        result['spend-cheque-info']     = None # TODO = spent cheque infos
        result['desc']                  = self.builder.get_object('desc').get_text()
        result['from']                     = self.from_id
        result['to']                       = self.to_id

        dbconf = dbconfig.dbConfig()

        if self.liststore == None:
        #Save data in data base for single use
            document = class_document.Document()
            document.add_notebook(result['from'],  result['total_value'], result['desc'])
            document.add_notebook(result['to']  , -result['cash_payment'], result['desc'])
            if result['discount'] :
                document.add_notebook(dbconf.get_int('sell-discount'), -result['discount'], result['desc'])
            cl_cheque = class_cheque.ClassCheque()
            for cheque in self.chequeui.new_cheques:
                if self.mode == 'our':
                    document.add_cheque(dbconf.get_int('our_cheque'), -cheque['amount'], cheque['desc'], cheque['serial'])
                else:
                    document.add_cheque(dbconf.get_int('other_cheque'), -cheque['amount'], cheque['desc'], cheque['serial'])
            #spendble cheque
            for sp_cheque in self.chequeui.spend_cheques:
                cl_cheque.update_status(sp_cheque['serial'],5)
                document.add_cheque(dbconf.get_int('other_cheque'), -sp_cheque['amount'] , unicode('kharj shodeh') , sp_cheque['serial'])
                    
            result = document.save()

            if result < 0:
                dialog = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, 'Failed, %s' % document.get_error_message(result))
                dialog.run()
                dialog.destroy()
                return

            if self.type_configs[self.type_index][3] == True: # from is subject
                customer_id = 0
            else: # from is customer
                customer_id = config.db.session.query(Customers).select_from(Customers).filter(Customers.custSubj==self.from_id).first().custId

            for cheque in self.chequeui.new_cheques:
                notebook_id =document.cheques_result[cheque['serial']]
                cl_cheque.add_cheque(cheque['amount'], cheque['write_date'], cheque['due_date'],
                                     cheque['serial'], cheque['status'],
                                     customer_id, cheque['bank_account_id'],
                                     result, notebook_id, cheque['desc'])
            cl_cheque.save()
            cl_cheque.save_cheque_history(self.current_time)
            self.on_destroy(self.builder.get_object('general'))

            infobar = gtk.InfoBar()
            label = gtk.Label(_('successfully added. Document number : %d') % document.number)
            infobar.get_content_area().add(label)
            width , height = self.main_window_background.window.get_size()
            infobar.set_size_request(width, -1)
            self.main_window_background.put(infobar ,0 , 0)
            infobar.show_all()

            glib.timeout_add_seconds(3, lambda w: w.destroy(), infobar)

        #Store result in list store for showing in addeditdoc
        else:
            mysubject = Subjects()
            numrows = len(self.liststore) + 1
            #document.add_notebook(result['from'],  result['total_value'], result['desc'])
            self.liststore.append ((localizeNumber(numrows), localizeNumber(result['from']), mysubject.get_name(result['from']), 0, localizeNumber(result['total_value']), result['desc'], None))
            #document.add_notebook(result['to']  , -result['cash_payment'], result['desc'])
            numrows += 1
            self.liststore.append ((localizeNumber(numrows), localizeNumber(result['to']), mysubject.get_name(result['to']), 0, localizeNumber(result['cash_payment']), result['desc'], None))
            if result['discount'] :
                #document.add_notebook(dbconf.get_int('sell-discount'), -result['discount'], result['desc'])
                self.liststore.append ((localizeNumber(numrows), localizeNumber(dbconf.get_int('sell-discount')), mysubject.get_name(dbconf.get_int('sell-discount')), localizeNumber(result['discount']), 0, result['desc'], None))

            #cl_cheque = class_cheque.ClassCheque()
            #or cheque in self.chequeui.new_cheques:
            #    if self.mode == 'our':
            #        document.add_cheque(dbconf.get_int('our_cheque'), -cheque['amount'], cheque['desc'], cheque['serial'])
            #    else:
            #        document.add_cheque(dbconf.get_int('other_cheque'), -cheque['amount'], cheque['desc'], cheque['serial'])
            #spendble cheque
            #for sp_cheque in self.chequeui.spend_cheques:
            #   cl_cheque.update_status(sp_cheque['serial'],5)
            #    document.add_cheque(dbconf.get_int('other_cheque'), -sp_cheque['amount'] , unicode('kharj shodeh') , sp_cheque['serial'])
                    

            #if self.type_configs[self.type_index][3] == True: # from is subject
            #    customer_id = 0
            #else: # from is customer
            #    customer_id = config.db.session.query(Customers).select_from(Customers).filter(Customers.custSubj==self.from_id).first().custId

            #for cheque in self.chequeui.new_cheques:
            #    notebook_id =document.cheques_result[cheque['serial']]
            #    cl_cheque.add_cheque(cheque['amount'], cheque['write_date'], cheque['due_date'],
            #                         cheque['serial'], cheque['status'],
            #                         customer_id, cheque['bank_account_id'],
            #                         result, notebook_id, cheque['desc'])
            #cl_cheque.save()
            #cl_cheque.save_cheque_history(self.current_time)
            self.on_destroy(self.builder.get_object('general'))


    def on_destroy(self, window):
        window.destroy()

    #TODO get a parameter to can send data to parent
    def run(self, parent=None, liststore=None):
        self.liststore = liststore
        win  = self.builder.get_object('general')
        win.connect('destroy', self.on_destroy)

        if parent:
            win.set_transient_for(parent)
        #win.set_position(gtk.WIN_POS_CENTER)
        win.set_destroy_with_parent(True)
        win.show_all()


## @}
