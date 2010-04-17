import pygtk
import gtk
from datetime import date

from sqlalchemy.orm.util import outerjoin

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
        
        money_cell_renderer = gtk.CellRendererText()
        money_cell_renderer.set_alignment(1.0, 0.5)
        
        self.treeview.append_column(column)
        column = gtk.TreeViewColumn(_("Debt"), money_cell_renderer, text=3)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = gtk.TreeViewColumn(_("Credit"), money_cell_renderer, text=4)
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
        self.numrows = 0
        if number > 0:
            self.showRows(number)
        else:
            self.docid = 0
    
        self.treeview.set_model(self.liststore)
        self.window.show_all()
        self.builder.connect_signals(self)
        
    def showRows(self, docnumber):
        query = self.session.query(Bill).select_from(Bill)
        bill = query.filter(Bill.number == docnumber).first()
        self.date.showDateObject(bill.date)
        self.docid = bill.id
        
        query = self.session.query(Notebook, Subject)
        query = query.select_from(outerjoin(Notebook, Subject, Notebook.subject_id == Subject.id))
        rows = query.filter(Notebook.bill_id == bill.id).all()
        for n, s in rows:
            self.numrows += 1
            if n.value < 0:
                value = -(n.value)
                debt = utility.showNumber(value)
                credit = "0"
                self.debt_sum += value
            else:
                credit = utility.showNumber(n.value)
                debt = "0"
                self.credit_sum += n.value
                
            self.liststore.append((self.numrows, s.code, s.name, debt, credit, n.desc))
            
        self.builder.get_object("docnumber").set_text (str(docnumber))
        self.builder.get_object("debtsum").set_text (utility.showNumber(self.debt_sum))
        self.builder.get_object("creditsum").set_text (utility.showNumber(self.credit_sum))
        if self.debt_sum > self.credit_sum:
            diff = self.debt_sum - self.credit_sum
        else:
            diff = self.credit_sum - self.debt_sum
        self.builder.get_object("difference").set_text (utility.showNumber(diff))
        
    
    def addRow(self, sender):
        dialog = self.builder.get_object("dialog1")
        dialog.set_title(_("Add new row"))
        self.code.set_text("")
        
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
        
    #TODO add progress bar
    def saveRow(self, code, amount, type, desc, iter=None):
        query = self.session.query(Subject).select_from(Subject)
        query = query.filter(Subject.code == code)
        sub = query.first()
        if sub == None:
            errorstr = _("No subject is registered with the code: %s") % code
            msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK, errorstr)
            msgbox.set_title(_("No subjects found"))
            msgbox.run()
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
            self.numrows += 1
            self.liststore.append ((self.numrows, code, sub.name, debt, credit, desc))
            
        self.builder.get_object("debtsum").set_text (utility.showNumber(self.debt_sum))
        self.builder.get_object("creditsum").set_text (utility.showNumber(self.credit_sum))
        if self.debt_sum > self.credit_sum:
            diff = self.debt_sum - self.credit_sum
        else:
            diff = self.credit_sum - self.debt_sum
        self.builder.get_object("difference").set_text (utility.showNumber(diff))
    
    def deleteRow(self, sender):
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        if iter != None :
            msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, 
                                       _("Are you sure to remove this row?"))
            msgbox.set_title(_("Are you sure?"))
            result = msgbox.run();
            if result == gtk.RESPONSE_OK :
                
                debt = int(self.liststore.get(iter, 3)[0].replace(",", ""))
                credit = int(self.liststore.get(iter, 4)[0].replace(",", ""))
                index = self.liststore.get(iter, 0)[0]
                res = self.liststore.remove(iter)
                #Update index of next rows
                if res:
                    while iter != None:
                        self.liststore.set_value (iter, 0, index)
                        index += 1
                        iter = self.liststore.iter_next(iter)
                self.numrows -= 1;
                
                self.debt_sum -= debt
                self.credit_sum -= credit
                self.builder.get_object("debtsum").set_text (utility.showNumber(self.debt_sum))
                self.builder.get_object("creditsum").set_text (utility.showNumber(self.credit_sum))
                if self.debt_sum > self.credit_sum:
                    diff = self.debt_sum - self.credit_sum
                else:
                    diff = self.credit_sum - self.debt_sum
                self.builder.get_object("difference").set_text (utility.showNumber(diff))
            msgbox.destroy()
    
    def saveDocument(self, sender):
        if self.debt_sum != self.credit_sum:
            msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, 
                                       _("Debt sum and Credit sum should be equal"))
            msgbox.set_title(_("Can not save document"))
            msgbox.run()
            msgbox.destroy()
            return
        else:
            number = 0
            today = date.today()
            if self.docid > 0 :
                query = self.session.query(Bill).select_from(Bill)
                bill = query.filter(Bill.id == self.docid).first()
                bill.lasteditdate = today
                bill.date = self.date.getDateObject()
                number = bill.number
                query = self.session.query(Notebook).filter(Notebook.bill_id == bill.id).delete()
            else :
                query = self.session.query(Bill.number).select_from(Bill)
                lastnumbert = query.order_by(Bill.number.desc()).first()
                if lastnumbert != None:
                    number = lastnumbert[0]
                number += 1
                
                #TODO if number is not equal to the maximum BigInteger value, prevent bill registration.
                bill = Bill (number, today, today, self.date.getDateObject())
                self.session.add(bill)
                self.session.commit()
                self.docid = bill.id
                
            iter = self.liststore.get_iter_first()
            
            while iter != None :
                code = self.liststore.get(iter, 1)[0]
                debt = self.liststore.get(iter, 3)[0].replace(",", "")
                value = -(int(debt))
                if value == 0 :
                    credit = self.liststore.get(iter, 4)[0].replace(",", "")
                    value = int(credit)
                desctxt = self.liststore.get(iter, 5)[0]
                
                query = self.session.query(Subject).select_from(Subject)
                query = query.filter(Subject.code == code)
                sub = query.first().id
                
                row = Notebook (sub, self.docid, value, desctxt)
                self.session.add(row)
                iter = self.liststore.iter_next(iter)
                
            self.session.commit()
            self.builder.get_object("docnumber").set_text (str(number))
        
    def deleteDocument(self, sender):
        msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, _("Are you sure to delete the whole document?"))
        msgbox.set_title(_("Are you sure?"))
        result = msgbox.run();
        
        if result == gtk.RESPONSE_OK :
            if self.docid > 0 :
                self.session.query(Notebook).filter(Notebook.bill_id == self.docid).delete()
                self.session.query(Bill).filter(Bill.id == self.docid).delete()
                self.session.commit()
            self.window.destroy()
        msgbox.destroy() 

    def selectSubject(self, sender):
        subject_win = subjects.Subjects()
        subject_win.connect("subject-selected", self.subjectSelected)
        
    def subjectSelected(self, sender, id, code, name):
        self.code.set_text(code)
        sender.window.destroy()
        #print(id)
        #print(code)
        #print(name)
        

        