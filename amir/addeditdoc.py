import pygtk
import gtk
from database import *

import numberentry
import dateentry
import subjects
import utility
from database import *

class AddEditDoc:
        
    def __init__(self, number=0):
        self.builder = gtk.Builder()
        self.builder.set_translation_domain("amir")
        self.builder.add_from_file("../data/ui/document.glade")
        
        self.window = self.builder.get_object("window1")
        self.window.set_title(_("Register new document"))
        
        self.date = dateentry.DateEntry()
        box = self.builder.get_object("datebox")
        box.add(self.date)
        self.date.show()
        
        self.code = numberentry.NumberEntry()
        box = self.builder.get_object("codebox")
        box.add(self.code)
        self.code.show()
        
        self.amount = numberentry.NumberEntry()
        box = self.builder.get_object("amountbox")
        box.add(self.amount)
        self.amount.show()
        
        self.treeview = self.builder.get_object("treeview")
        self.liststore = gtk.ListStore(int, str, str, str, str, str)
        
        column = gtk.TreeViewColumn(_("Index"), gtk.CellRendererText(), text=0)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = gtk.TreeViewColumn(_("Subject Code"), gtk.CellRendererText(), text=1)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = gtk.TreeViewColumn(_("Subject Name"), gtk.CellRendererText(), text=2)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = gtk.TreeViewColumn(_("Debt"), gtk.CellRendererText(), text=3)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = gtk.TreeViewColumn(_("Credit"), gtk.CellRendererText(), text=4)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = gtk.TreeViewColumn(_("Description"), gtk.CellRendererText(), text=5)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)

        self.treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        
        self.session = db.session
        self.debt_sum = 0
        self.credit_sum = 0
    
        self.treeview.set_model(self.liststore)
        self.window.show_all()
        self.builder.connect_signals(self)
        
    def addRow(self, sender):
        dialog = self.builder.get_object("dialog1")
        dialog.set_title(_("Add new row"))
        
        desc = self.builder.get_object("desc")
        
        result = dialog.run()
        if result == 1:
            if self.builder.get_object("debtor").get_active() == True:
                type = 0
            else:
                type = 1;
            self.saveRow(self.code.get_text(), int(self.amount.get_text()), type, desc.get_text())
        
        dialog.hide()
    
    def editRow(self, sender):
        dialog = self.builder.get_object("dialog1")
        dialog.set_title(_("Edit row"))
        
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        if iter != None :
            code = self.liststore.get(iter, 1)[0]
            debt = self.liststore.get(iter, 3)[0].replace(",", "")
            credit = self.liststore.get(iter, 4)[0].replace(",", "")
            desctxt = self.liststore.get(iter, 5)[0]
            
            if debt != "0":
                self.builder.get_object("debtor").set_active(True)
                self.amount.set_text(debt)
            else:
                self.builder.get_object("creditor").set_active(True)
                self.amount.set_text(credit)
            self.code.set_text(code)
            desc = self.builder.get_object("desc")
            desc.set_text(desctxt)
        
            result = dialog.run()
            if result == 1:
                if self.builder.get_object("debtor").get_active() == True:
                    type = 0
                else:
                    type = 1
                    
                if debt != "0":
                    self.debt_sum -= int(debt)
                else:
                    self.credit_sum -= int(credit)
                    
                self.saveRow(self.code.get_text(), int(self.amount.get_text()), type, desc.get_text(), iter)
            
            dialog.hide()
    
    def selectSubject(self, sender):
        print("selecting...")
        #subjects = subjects.Subjects()
        
    def saveRow(self, code, amount, type, desc, iter=None):
        query = self.session.query(Subject).select_from(Subject)
        query = query.filter(Subject.code == code)
        sub = query.first()
        if sub == None:
            errorstr = _("No subject is registered with the code: %s") % code
            msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK, errorstr)
            msgbox.set_title("No subjects found")
            msgbox.run();
            msgbox.destroy()
            return
            
        if sub.type != 2:
            type = sub.type
        debt = 0
        credit = 0
        
        if type == 0:
           debt = utility.showNumber(amount)
           self.debt_sum += amount
        else:
            if type == 1:
                credit = utility.showNumber(amount)
                self.credit_sum += amount
                 
        if iter != None:
            self.liststore.set (iter, 1, code, 2, sub.name, 3, debt, 4, credit, 5, desc)
        else :
            self.liststore.append ((1, code, sub.name, debt, credit, desc))
        self.builder.get_object("debtsum").set_text (utility.showNumber(self.debt_sum))
        self.builder.get_object("creditsum").set_text (utility.showNumber(self.credit_sum))
    
    def deleteRow(self, sender):
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        if iter != None :
            msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, "Are you sure to remove this row?")
            msgbox.set_title("Are you sure?")
            result = msgbox.run();
            if result == gtk.RESPONSE_OK :
                msgbox.destroy()
                
                debt = int(self.liststore.get(iter, 3)[0].replace(",", ""))
                credit = int(self.liststore.get(iter, 4)[0].replace(",", ""))
                self.liststore.remove(iter)
                
                self.debt_sum -= debt
                self.credit_sum -= credit
                self.builder.get_object("debtsum").set_text (utility.showNumber(self.debt_sum))
                self.builder.get_object("creditsum").set_text (utility.showNumber(self.credit_sum))
    
    def saveDocument(self, sender):
        pass

        