from gi.repository import Gtk
from . import class_document
from . import numberentry, decimalentry
from . import dateentry
from . import subjects
from . import utility
from . import automaticaccounting
from .share import share
from .database import Subject, Notebook
from .helpers import get_builder
from sqlalchemy import or_, and_, func

import sys
if sys.version_info > (3,):
    unicode = str

config = share.config

## \defgroup UserInterface
# @{

## Register or edit a document
class AddEditDoc:

    ##Create a new window and initialize it.
    # \param number Document number for edit or zero for new document
    def __init__(self, number=0, background=None):
        self.main_window_background = background
        self.new_items = []
        self.deleted_items = []
        self.edit_items = []
        self.builder = get_builder("document")

        self.window = self.builder.get_object("window1")
        # self.window.set_title(_("Register new document"))

        self.date = dateentry.DateEntry()
        box = self.builder.get_object("datebox")
        box.add(self.date)
        self.date.show()

        self.code = numberentry.NumberEntry()
        box = self.builder.get_object("codebox")
        box.add(self.code)
        self.code.show()
        self.code.connect("activate", self.selectSubject)
        self.code.set_tooltip_text(_("Press Enter to see available subjects."))

        self.amount = decimalentry.DecimalEntry()
        box = self.builder.get_object("amountbox")
        box.add(self.amount)
        self.amount.set_activates_default(True)
        self.amount.show()

        self.treeview = self.builder.get_object("treeview")
        #self.treeview.set_direction(Gtk.TextDirection.LTR)
        # if Gtk.widget_get_default_direction() == Gtk.TextDirection.RTL :
        #     halign = 1
        # else:
        #     halign = 0
        self.liststore = Gtk.ListStore(str, str, str, str, str, str, str)

        column = Gtk.TreeViewColumn(_("Index"), Gtk.CellRendererText(), text=0)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = Gtk.TreeViewColumn(_("Subject Code"), Gtk.CellRendererText(), text=1)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = Gtk.TreeViewColumn(_("Subject Name"), Gtk.CellRendererText(), text=2)
        column.set_spacing(5)
        column.set_resizable(True)

        money_cell_renderer = Gtk.CellRendererText()
        #money_cell_renderer.set_alignment(1.0, 0.5) #incompatible with pygtk2.16

        self.treeview.append_column(column)
        column = Gtk.TreeViewColumn(_("Debt"), money_cell_renderer, text=3)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = Gtk.TreeViewColumn(_("Credit"), money_cell_renderer, text=4)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = Gtk.TreeViewColumn(_("Description"), Gtk.CellRendererText(), text=5)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        #column = Gtk.TreeViewColumn(_("Notebook ID") , Gtk.CellRendererText(), text=6)
        #column.set_alignment(halign)
        #column.set_spacing(5)
        #column.set_resizable(True)
        #self.treeview.append_column(column)

        self.treeview.get_selection().set_mode(Gtk.SelectionMode.SINGLE)

        self.debt_sum   = 0
        self.credit_sum = 0
        self.numrows    = 0

        self.auto_win   = None
        self.cl_document = class_document.Document()

        if number > 0:
            if self.cl_document.set_bill(number):
                self.showRows()
                self.window.set_title(_("Edit document"))
            else:
                numstring = utility.LN(number)
                msg = _("No document found with number %s\nDo you want to register a document with this number?") % numstring
                msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL, msg)
                msgbox.set_title(_("No Documents found"))
                result = msgbox.run()
                msgbox.destroy()
                if result == Gtk.ResponseType.CANCEL:
                    return
                else:
                    self.builder.get_object("docnumber").set_text (numstring)

        self.treeview.set_model(self.liststore)
        self.window.show_all()

        self.builder.get_object("editable").hide()
        self.builder.get_object("non-editable").hide()
        if self.cl_document.permanent:
            # Pbill = config.db.session.query(Notebook).filter(Notebook.bill_id ==1).filter(or_(Notebook.chqId != 0 , Notebook.factorId != 0 ) ).first()
            # if Pbill  :
            if number != 1 :
                self.builder.get_object("non-editable").show()
        else:
            self.builder.get_object("editable").show()

        self.builder.connect_signals(self)
        #self.connect("database-changed", self.dbChanged)

    ##Add the document row to liststore to show in list view
    def showRows(self):
        self.debt_sum   = 0
        self.credit_sum = 0
        self.numrows    = 0

        self.date.showDateObject(self.cl_document.date)
        rows = self.cl_document.get_notebook_rows()
        for n, s in rows:
            self.numrows += 1
            if n.value < 0:
                value = -(n.value)
                debt = utility.LN(value)
                credit = utility.LN(0)
                self.debt_sum += value
            else:
                credit = utility.LN(n.value)
                debt = utility.LN(0)
                self.credit_sum += n.value

            if s:
                code = s.code
            else:
                code = 0;
                s = Subject()
            numrows = str(self.numrows)
            if config.digittype == 1:
                code = utility.convertToPersian(code)
                numrows = utility.convertToPersian(numrows)
            self.liststore.append((numrows, code, s.name, debt, credit, n.desc, str(n.id)))

        docnum = utility.LN(self.cl_document.number)
        self.builder.get_object("docnumber").set_text (docnum)
        self.builder.get_object("debtsum").set_text (utility.LN(self.debt_sum))
        self.builder.get_object("creditsum").set_text (utility.LN(self.credit_sum))
        if self.debt_sum > self.credit_sum:
            diff = self.debt_sum - self.credit_sum
        else:
            diff = self.credit_sum - self.debt_sum
        self.builder.get_object("difference").set_text (utility.LN(diff))

    ##Show add_row dialog and call saveRow() to save row to list store'
    def addRow(self, sender):
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        if iter != None :
            code    = self.liststore.get(iter, 1)[0]
        dialog = self.builder.get_object("dialog1")
        dialog.set_title(_("Add new row"))
        self.code.set_text("")

        desc = self.builder.get_object("desc")
        desc.set_text("")
        self.amount.set_text(utility.readNumber(0))

        result = dialog.run()
        if result == 1:
            type = not (self.builder.get_object("debtor").get_active() == True)

            code = self.code.get_text()
            amount = self.amount.get_float()
            if code != '' and amount != '':


                self.saveRow(utility.convertToLatin(code), amount, type, desc.get_text())
        dialog.hide()

    ##Show add_row dialog and call saveRow() to edit the current row
    def editRow(self, sender):
        dialog = self.builder.get_object("dialog1")
        dialog.set_title(_("Edit row"))

        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]

        if iter != None :
            code    = self.liststore.get(iter, 1)[0]
            debt    = self.liststore.get(iter, 3)[0].replace(",", "")
            credit  = self.liststore.get(iter, 4)[0].replace(",", "")
            desctxt = self.liststore.get(iter, 5)[0]

            if float(unicode(debt)) != 0:
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
                type = not (self.builder.get_object("debtor").get_active() == True)

                if float(unicode(debt)) != 0:
                    self.debt_sum -= float(unicode(debt))
                else:
                    self.credit_sum -= float(unicode(credit))

                code = self.code.get_text()
                amount = self.amount.get_float()
                if code != '' and amount != '':
                    self.saveRow(utility.convertToLatin(code),
                                 amount,
                                 int(type),
                                 desc.get_text(),
                                 iter)

            dialog.hide()

    ## Save or update row from liststore and update the sum and diff of row
    def saveRow(self, code, amount, type, desc, iter=None):
        query = config.db.session.query(Subject).select_from(Subject)
        query = query.filter(Subject.code == code)
        sub = query.first()
        if sub == None:
            if config.digittype == 1:
                code = utility.convertToPersian(code)
            errorstr = _("No subject is registered with the code: %s") % code
            msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, errorstr)
            msgbox.set_title(_("No subjects found"))
            msgbox.run()
            msgbox.destroy()
            return

        if sub.type != 2:
            type = sub.type

        debt   = "0"
        credit = "0"

        if config.digittype == 1:
            debt   = utility.convertToPersian(debt)
            credit = utility.convertToPersian(credit)
            code   = utility.convertToPersian(code)

        if type == 0:
            debt = utility.LN(amount)
            self.debt_sum += amount
        elif type == 1:
            credit = utility.LN(amount)
            self.credit_sum += amount

        if iter != None:
            self.liststore.set (iter, 1, code, 2, sub.name, 3, debt, 4, credit, 5, desc)
        else :
            self.numrows += 1
            numrows = str(self.numrows)
            if config.digittype == 1:
                numrows = utility.convertToPersian(numrows)
            self.liststore.append ((numrows, code, sub.name, debt, credit, desc, None))

        self.builder.get_object("debtsum").set_text (utility.LN(self.debt_sum))
        self.builder.get_object("creditsum").set_text (utility.LN(self.credit_sum))
        if self.debt_sum > self.credit_sum:
            diff = self.debt_sum - self.credit_sum
        else:
            diff = self.credit_sum - self.debt_sum
        self.builder.get_object("difference").set_text (utility.LN(diff))

    ## Delte the selected row from liststore and update sum and diff
    def deleteRow(self, sender):
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        if iter != None :
            msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL,
                                       _("Are you sure to remove this row?"))
            msgbox.set_title(_("Are you sure?"))
            result = msgbox.run();
            if result == Gtk.ResponseType.OK :
                id     = int(unicode(self.liststore.get(iter, 6)[0]))
                code   = int(unicode(self.liststore.get(iter, 1)[0]))
                debt   = int(unicode(self.liststore.get(iter, 3)[0].replace(",", "")))
                credit = int(unicode(self.liststore.get(iter, 4)[0].replace(",", "")))
                index  = int(unicode(self.liststore.get(iter, 0)[0]))
                res    = self.liststore.remove(iter)
                self.deleted_items.append(id)
                #Update index of next rows
                if res:
                    while iter != None:
                        strindex = str(index)
                        if config.digittype == 1:
                            strindex = utility.convertToPersian(strindex)
                        self.liststore.set_value (iter, 0, strindex)
                        index += 1
                        iter = self.liststore.iter_next(iter)
                self.numrows -= 1;

                self.debt_sum -= debt
                self.credit_sum -= credit
                self.builder.get_object("debtsum").set_text (utility.LN(self.debt_sum))
                self.builder.get_object("creditsum").set_text (utility.LN(self.credit_sum))
                if self.debt_sum > self.credit_sum:
                    diff = self.debt_sum - self.credit_sum
                else:
                    diff = self.credit_sum - self.debt_sum
                self.builder.get_object("difference").set_text (utility.LN(diff))
            msgbox.destroy()

    ##Save liststore change to database
    def saveDocument(self, sender):
        sender.grab_focus()

        self.cl_document.date = self.date.getDateObject()

        #TODO if number is not equal to the maximum BigInteger value, prevent bill registration.
        iter = self.liststore.get_iter_first()
        while iter != None :
            code = utility.convertToLatin(self.liststore.get(iter, 1)[0])
            debt = utility.getFloatNumber(self.liststore.get(iter, 3)[0])
            value = -(debt)
            if(self.liststore.get(iter,6)[0] != None):
                id = self.liststore.get(iter,6)[0]
            else:
                id = 0
            if value == 0 :
                credit = utility.getFloatNumber(self.liststore.get(iter, 4)[0])
                value = credit
            desctxt = unicode(self.liststore.get(iter, 5)[0])

            query = config.db.session.query(Subject)
            query = query.filter(Subject.code == code)
            subject_id = query.first().id

            self.cl_document.add_notebook(subject_id, value, desctxt, int(id))

            iter = self.liststore.iter_next(iter)
        result = self.cl_document.save(delete_items= self.deleted_items)
        self.deleted_items = []
        if result == -1:
            msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                                       _("Document should not be empty"))
            msgbox.set_title(_("Can not save document"))
            msgbox.run()
            msgbox.destroy()
            self.cl_document.clear_notebook()
            return
        elif result == -2:
            msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                                       _("Debt sum and Credit sum should be equal"))
            msgbox.set_title(_("Can not save document"))
            msgbox.run()
            msgbox.destroy()
            self.cl_document.clear_notebook()
            return
        else:
            self.liststore.clear()
            self.deleted_items = []
            self.cl_document.clear_notebook()
            self.showRows()

        docnum = utility.LN(self.cl_document.number)
        self.builder.get_object("docnumber").set_text (docnum)

        share.mainwin.silent_daialog(_("Document saved with number %s.") % docnum)

    ##Mark document as permanent
    def makePermanent(self, sender):
        if self.cl_document.id > 0 :
            self.cl_document.set_permanent(True)
            self.builder.get_object("editable").hide()
            self.builder.get_object("non-editable").show()
        else:
            msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.INFO, Gtk.ButtonsType.OK,
                                   _("You should save the document before make it permanent"))
            msgbox.set_title(_("Document is not saved"))
            msgbox.run()
            msgbox.destroy()

    ##Mark document as temporary
    def makeTemporary(self, sender):
        msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL,
                                   _("Are you sure to make this document temporary?"))
        msgbox.set_title(_("Are you sure?"))
        result = msgbox.run();
        msgbox.destroy()

        if result == Gtk.ResponseType.OK and self.cl_document.id > 0 :
            self.cl_document.set_permanent(False)
            self.builder.get_object("non-editable").hide()
            self.builder.get_object("editable").show()

    ##delete all document from database
    def deleteDocument(self, sender):
        if self.cl_document.id == 0 :
            return

        msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL,
                                   _("Are you sure to delete the whole document?"))
        msgbox.set_title(_("Are you sure?"))
        result = msgbox.run();

        if result == Gtk.ResponseType.OK :
            self.cl_document.delete()
            self.window.destroy()
        msgbox.destroy()

    ##Call automaticaccounting::AutomaticAccounting to show automaticacconting window
    def auto_Document(self, sender):
        auto_win = automaticaccounting.AutomaticAccounting()
        auto_win.run(self.window, self.liststore)
        auto_win.win.connect('destroy', self.updateSum)

    #Call  to show automaticacconting window
    #def auto_Saved(self, sender):
    #    self.showRows()

    ##Call subjects::Subjects to show Subject window
    def selectSubject(self, sender):
        subject_win = subjects.Subjects()
        code = utility.convertToLatin(self.code.get_text() )
        subject_win.highlightSubject(code)
        subject_win.connect("subject-selected", self.subjectSelected)

    ##Call back when subject selected from subjects::Subjects::selectSubjectFromList()
    def subjectSelected(self, sender, id, code, name):
        if config.digittype == 1:
            code = utility.convertToPersian(code)
        self.code.set_text(code)
        self.builder.get_object("nameLbl").set_text(name)
        q = config.db.session.query(func.sum(Notebook.value)).filter(Notebook.subject_id == id)
        if q.first()[0]:
            val = q.first()[0]
        else:
            val = 0
        self.builder.get_object("remainLbl").set_text(utility.readNumber(abs(val)))
        subType = ""
        if val <0:
            subType = _("Debtor")
        elif val>0:
            subType = _("Creditor")
        self.builder.get_object("subTypeLbl").set_text(subType)
        sender.window.destroy()

    ##Call when Databese changed from main window
    def dbChanged(self, sender, active_dbpath):
        self.window.destroy()

    ##Call for update sum after autodocument
    def updateSum(self, window):
        iter = self.liststore.get_iter_first()
        self.debt_sum = 0
        self.credit_sum = 0
        while iter != None :
            self.debt_sum += int(unicode(self.liststore.get(iter, 3)[0].replace(",", "")))
            self.credit_sum += int(unicode(self.liststore.get(iter, 4)[0].replace(",", "")))
            iter = self.liststore.iter_next(iter)
        self.builder.get_object("debtsum").set_text (utility.LN(self.debt_sum))
        self.builder.get_object("creditsum").set_text (utility.LN(self.credit_sum))
        self.builder.get_object("difference").set_text (utility.LN(abs(self.credit_sum - self.debt_sum)))

## @}
