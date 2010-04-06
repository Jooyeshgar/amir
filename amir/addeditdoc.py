import pygtk
import gtk
from database import *

import numberentry
import dateentry
import subjects
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
            code = self.treestore.get(iter, 1)[0]
            debt = self.treestore.get(iter, 2)[0]
            credit = self.treestore.get(iter, 3)[0]
            desc = self.treestore.get(iter, 4)[0]
            
            if debt != 0:
                self.builder.get_object("debtor").set_active(True)
                self.amount.set_text(debt)
            else:
                self.builder.get_object("creditor").set_active(True)
                self.amount.set_text(credit)
            self.code.set_text(code)
            self.builder.get_object("desc").set_text(desc)
        
            result = dialog.run()
            if result == 1:
                if self.builder.get_object("debtor").get_active() == True:
                    type = 0
                else:
                    type = 1
                    
                if debt != 0:
                    self.debt_sum -= debt
                else:
                    self.credit_sum -= credit
                    
                saveRow(self.code.get_text(), int(self.amount.get_text()), type, desc.get_text())
            
            dialog.hide()
    
    def selectSubject(self, sender):
        print("selecting...")
        #subjects = subjects.Subjects()
        
    def saveRow(self, code, amount, type, desc):
        query = self.session.query(Subject).select_from(Subject)
        query = query.filter(Subject.code == code)
        sub = query.first()
        
        if sub.type != 2:
            type = sub.type
        debt = 0
        credit = 0
        
        if type == 0:
           debt = amount
           self.debt_sum += amount
        else:
            if type == 1:
                credit = amount
                self.credit_sum += amount
                 
        self.liststore.append ((1, code, sub.name, debt, credit, desc))
        self.builder.get_object("debtsum").set_text (str(self.debt_sum))
        self.builder.get_object("creditsum").set_text (str(self.credit_sum))
        pass
    
    def deleteRow(self, sender):
        pass
    
    def saveDocument(self, sender):
        pass

        