import gi
from gi.repository import Gtk

from sqlalchemy import or_
from sqlalchemy.orm.util import outerjoin, join
from sqlalchemy.sql import between, and_
from sqlalchemy.sql.functions import sum, count

from .database import *
from .dateentry import *
from .share import share
from .helpers import get_builder
from gi.repository import Gdk
from .calverter import calverter
from datetime import datetime, timedelta
from . import dateentry
from . import class_document
from . import dbconfig
from . import subjects, customers
from . import class_bankaccounts
from . import decimalentry, utility

from gettext import gettext as _

import logging

dbconf = dbconfig.dbConfig()
# config = share.config


class ChequeReport(GObject.GObject):
    chequeStatus = ["", _("Paid-Not passed"), _("Paid-Passed"), _("Recieved-Not cashed"), _("Recieved-Cashed"), _(
        "Spent"), _("Returned from customer"), _("Returned to customer"), _("Paid-Bounced"), _("Recieved-Bounced"), _("Float")]
    treeviews = ["treeviewIncoming", "treeviewOutgoing", "treeviewNotPassed", "treeviewNotCashed", "treeviewPassed", "treeviewCashed",
                 "treeviewSpent", "treeviewBounced", "treeviewBouncedP", "treeviewReturnedT", "treeviewReturnedF", "treeviewFloat", "treeviewDeleted"]

    def __init__(self):
        self.cal = calverter()

        self.builder = get_builder("chequereport")
        self.window = self.builder.get_object("windowChequeReport")
        self.window.set_title(_("Cheques Report"))

        self.treeviewIncoming = self.builder.get_object("treeviewIncoming")
        self.treeviewOutgoing = self.builder.get_object("treeviewOutgoing")
        self.treeviewNotPassed = self.builder.get_object("treeviewNotPassed")
        self.treeviewNotCashed = self.builder.get_object("treeviewNotCashed")
        self.treeviewDeleted = self.builder.get_object("treeviewDeleted")
        self.treeviewCashed = self.builder.get_object("treeviewCashed")
        self.treeviewPassed = self.builder.get_object("treeviewPassed")
        self.treeviewSpent = self.builder.get_object("treeviewSpent")
        self.treeviewBounced = self.builder.get_object("treeviewBounced")
        self.treeviewBouncedP = self.builder.get_object("treeviewBouncedP")
        self.treeviewReturnedT = self.builder.get_object("treeviewReturnedT")
        self.treeviewReturnedF = self.builder.get_object("treeviewReturnedF")
        self.treeviewFloat = self.builder.get_object("treeviewFloat")
        self.treestoreIncoming = Gtk.TreeStore(
            str, str, str, str, str, str, str, str, str, str)
        self.treestoreOutgoing = Gtk.TreeStore(
            str, str, str, str, str, str, str, str, str, str)
        self.treestoreNotPassed = Gtk.TreeStore(
            str, str, str, str, str, str, str, str, str, str)
        self.treestoreNotCashed = Gtk.TreeStore(
            str, str, str, str, str, str, str, str, str, str)
        self.treestoreDeleted = Gtk.TreeStore(
            str, str, str, str, str, str, str, str, str, str)
        self.treestorePassed = Gtk.TreeStore(
            str, str, str, str, str, str, str, str, str, str)
        self.treestoreCashed = Gtk.TreeStore(
            str, str, str, str, str, str, str, str, str, str)
        self.treestoreSpent = Gtk.TreeStore(
            str, str, str, str, str, str, str, str, str, str)
        self.treestoreBounced = Gtk.TreeStore(
            str, str, str, str, str, str, str, str, str, str)
        self.treestoreBouncedP = Gtk.TreeStore(
            str, str, str, str, str, str, str, str, str, str)
        self.treestoreReturnedT = Gtk.TreeStore(
            str, str, str, str, str, str, str, str, str, str)
        self.treestoreReturnedF = Gtk.TreeStore(
            str, str, str, str, str, str, str, str, str, str)
        self.treestoreFloat = Gtk.TreeStore(
            str, str, str, str, str, str, str, str, str, str)
        self.treeviewIncoming.set_model(self.treestoreIncoming)
        self.treeviewOutgoing.set_model(self.treestoreOutgoing)
        self.treeviewNotPassed.set_model(self.treestoreNotPassed)
        self.treeviewNotCashed.set_model(self.treestoreNotCashed)
        self.treeviewDeleted.set_model(self.treestoreDeleted)
        self.treeviewPassed.set_model(self.treestorePassed)
        self.treeviewCashed.set_model(self.treestoreCashed)
        self.treeviewSpent.set_model(self.treestoreSpent)
        self.treeviewBounced.set_model(self.treestoreBounced)
        self.treeviewBouncedP.set_model(self.treestoreBouncedP)
        self.treeviewReturnedT.set_model(self.treestoreReturnedT)
        self.treeviewReturnedF.set_model(self.treestoreReturnedF)
        self.treeviewFloat.set_model(self.treestoreFloat)

        headers = (_("ID"), _("Amount"), _("Write Date"), _("Due Date"), _("Serial"), _(
            "Customer Name"), _("Account"), _("Description"), _("Bill ID"), _("Status"))
        for treeview in self.treeviews:
            i = 0
            for header in headers:
                column = Gtk.TreeViewColumn(
                    str(header), Gtk.CellRendererText(), text=i)
                column.set_spacing(5)
                column.set_resizable(True)
                column.set_sort_column_id(i)
                column.set_sort_indicator(True)
                self.builder.get_object(treeview).append_column(column)
                i += 1

        self.window.show_all()
        self.builder.connect_signals(self)

        dateFromEntry = self.builder.get_object("dateFromSearchentry")
        dateToEntry = self.builder.get_object("dateToSearchentry")
        dateFromEntry1 = self.builder.get_object("dateFromSearchentry1")
        dateToEntry1 = self.builder.get_object("dateToSearchentry1")
        if share.config.datetypes[share.config.datetype] == "jalali":
            year, month, day = "1397", "12", "20"
        else:
            year, month, day = "2018", "12", "20"
        placeH = self.format_date([year, month, day])
        dateToEntry.set_placeholder_text(placeH)
        dateFromEntry.set_placeholder_text(placeH)
        dateToEntry1.set_placeholder_text(placeH)
        dateFromEntry1.set_placeholder_text(placeH)

        self.date_entry = dateentry.DateEntry()
        self.current_time = self.date_entry.getDateObject()
        self.createHistoryTreeview()

    def searchFilter(self, sender=None):
        box = self.builder.get_object("idSearchentry")
        chequeId = box.get_text()

        box = self.builder.get_object("serialSearchentry")
        chqSerial = box.get_text()

        box = self.builder.get_object("amountFromSearchentry")
        amountFrom = box.get_text()

        box = self.builder.get_object("amountToSearchentry")
        amountTo = box.get_text()

        box = self.builder.get_object("dateFromSearchentry1")  # Due
        dateFrom = box.get_text()

        box = self.builder.get_object("dateToSearchentry1")  # Due
        dateTo = box.get_text()

        box = self.builder.get_object("dateFromSearchentry")  # write
        wDateFrom = box.get_text()

        box = self.builder.get_object("dateToSearchentry")  # write
        wDateTo = box.get_text()
        self.showResult(chequeId, chqSerial, amountFrom,
                        amountTo, dateFrom, dateTo, wDateTo, wDateFrom)

    def showResult(self, chequeId=None, chqSerial=None, amountFrom=None, amountTo=None, dateFrom=None, dateTo=None, wDateTo=None, wDateFrom=None):
        self.treestoreIncoming.clear()
        self.treestoreOutgoing.clear()
        self.treestoreNotPassed.clear()
        self.treestoreNotCashed.clear()
        self.treestoreDeleted.clear()
        self.treestorePassed.clear()
        self.treestoreCashed.clear()
        self.treestoreSpent.clear()
        self.treestoreBounced.clear()
        self.treestoreBouncedP.clear()
        self.treestoreReturnedT.clear()
        self.treestoreReturnedF.clear()

        result = share.config.db.session.query(Cheque, Customers.custName).select_from(
            outerjoin(Cheque, Customers, Customers.custId == Cheque.chqCust))
        # Apply filters
        delimiter = share.config.datedelims[share.config.datedelim]
        if chequeId:
            result = result.filter(Cheque.chqId == chequeId)
        if chqSerial:
            result = result.filter(Cheque.chqSerial.like(chqSerial+"%"))
        if amountFrom:
            result = result.filter(Cheque.chqAmount >= amountFrom)
        if amountTo:
            result = result.filter(Cheque.chqAmount <= amountTo)

        if dateTo:
            dateTo = dateentry.stringToDate(dateTo)
        if dateFrom:
            dateFrom = dateentry.stringToDate(dateFrom)
        if wDateTo:
            wDateTo = dateentry.stringToDate(wDateTo)
        if wDateFrom:
            wDateFrom = dateentry.stringToDate(wDateFrom)

        if dateTo:
            result = result.filter(Cheque.chqDueDate <= dateTo)
        if wDateTo:
            result = result.filter(Cheque.chqWrtDate <= wDateTo)
        if dateFrom:
            #dateFrom -= timedelta(days=1)
            result = result.filter(Cheque.chqDueDate >= dateFrom)
        if wDateFrom:
            #wDateFrom -= timedelta(days=1)
            result = result.filter(Cheque.chqWrtDate >= wDateFrom)

        totalIn = totalGo = totalnotcash = totalnotpass = totalPass = totalCash = totalSpent = totalBouncedp = totalBounced = totalRetT = totalRetF = totalFloat = 0
        # Show
        for cheque, cust in result.all():
            chqWrtDate = dateentry.dateToString(cheque.chqWrtDate)
            chqDueDate = dateentry.dateToString(cheque.chqDueDate)

            # if (cheque.chqStatus == 2) or (cheque.chqStatus == 4):
            #     clear = _('Cleared')
            # else:
            #     clear = _('Not Cleared' )
            chqBill = share.config.db.session.query(Notebook.bill_id).filter(
                Notebook.chqId == cheque.chqId).first()
            if chqBill:
                chqBill = chqBill.bill_id
            else:
                chqBill = 0
            self.bankaccounts_class = class_bankaccounts.BankAccountsClass()
            isSpended = False
            stat = cheque.chqStatus
            if stat == 6:
                history = share.config.db.session.query(ChequeHistory).filter(
                    ChequeHistory.ChequeId == cheque.chqId).order_by(ChequeHistory.Id.desc()).limit(2).all()
                if len(history):
                    history = history[1]
                    isSpended = True if history.Status == 5 else False
            if stat in [1, 2, 6, 8] and not isSpended:
                chqAccount = self.bankaccounts_class.get_account(
                    cheque.chqAccount).accName
            else:
                chqAccount = self.bankaccounts_class.get_bank_name(
                    cheque.chqAccount)
            addingRow = (str(cheque.chqId), str(cheque.chqAmount), str(chqWrtDate), str(chqDueDate), str(cheque.chqSerial),
                str(cust), str(chqAccount), str(cheque.chqDesc), str(chqBill), str(self.chequeStatus[cheque.chqStatus]))
            if cheque.chqDelete == False:
                if stat in [3, 4, 7, 9]:
                    self.treestoreIncoming.append(None, addingRow)
                    totalIn += cheque.chqAmount
                else:
                    self.treestoreOutgoing.append(None, addingRow)
                    totalGo += cheque.chqAmount

                if stat == 1:
                    self.treestoreNotPassed.append(None, addingRow)
                    totalPass += cheque.chqAmount
                elif stat == 2:
                    self.treestorePassed.append(None, addingRow)
                    totalnotpass += cheque.chqAmount
                elif stat == 3:
                    self.treestoreNotCashed.append(None, addingRow)
                    totalnotcash += cheque.chqAmount
                elif stat == 4:
                    self.treestoreCashed.append(None, addingRow)
                    totalCash += cheque.chqAmount
                elif stat == 5:
                    self.treestoreSpent.append(None, addingRow)
                    totalSpent += cheque.chqAmount
                elif stat == 6:
                    self.treestoreReturnedF.append(None, addingRow)
                    totalRetF += cheque.chqAmount
                elif stat == 7:
                    self.treestoreReturnedT.append(None, addingRow)
                    totalRetT += cheque.chqAmount
                elif stat == 8:
                    self.treestoreBouncedP.append(None, addingRow)
                    totalBouncedp += cheque.chqAmount
                elif stat == 9:
                    self.treestoreBounced.append(None, addingRow)
                    totalBounced += cheque.chqAmount
                elif stat == 10:
                    self.treestoreFloat.append(None, addingRow)
                    totalFloat += cheque.chqAmount
            else:
                self.treestoreDeleted.     append(None, addingRow)
        self.totals = (totalIn, totalGo, totalnotpass, totalnotcash, totalPass, totalCash,
                       totalSpent, totalBounced, totalBouncedp, totalRetT, totalRetF, totalFloat, "")
        self.builder.get_object("totalLbl").set_text(str(totalIn))
        self.currentTreeview = 0

    def getSelection(self):
        treeview = self.builder.get_object(
            self.treeviews[self.currentTreeview])
        selection = treeview.get_selection()
        iter = selection.get_selected()[1]
        if iter != None:
            self.code = convertToLatin(treeview.get_model().get(iter, 0)[0])

    def editCheque(self, sender):
        self.getSelection()
        self.initChequeForm()
        cheque = share.config.db.session.query(Cheque).filter(
            Cheque.chqId == self.code).first()
        #payer_id   = cheque.chqCust
        amount = utility.LN(cheque.chqAmount, False)
        serial = cheque.chqSerial
        wrtDate = cheque.chqWrtDate
        dueDate = cheque.chqDueDate
        desc = cheque.chqDesc

        self.builder.get_object("chequeStatusLbl") .set_text(
            self.chequeStatus[cheque.chqStatus])
        self.bankCombo.set_active(cheque.chqAccount - 1)
        #self.edtPymntFlg = True
        #self.edititer = iter
        self.addPymntDlg.set_title(_("Edit Non-Cash Payment"))
        self.builder.get_object("submitBtn").set_label(_("Save Changes..."))
        self.builder.get_object("paymentsStatusBar").push(1, "")

        self.pymntAmntEntry.set_text(amount)
        self.serialNoEntry.set_text(serial)
        self.writeDateEntry.showDateObject(wrtDate)
        self.dueDateEntry.showDateObject(dueDate)
        self.pymntDescEntry.set_text(desc)

    def initChequeForm(self):
        self.addPymntDlg = self.builder.get_object("addPaymentDlg")
        self.pymntAmntEntry = decimalentry.DecimalEntry()
        self.builder.get_object("pymntAmntBox").add(self.pymntAmntEntry)
        self.pymntAmntEntry.show()

        self.dueDateEntry = dateentry.DateEntry()
        self.builder.get_object("pymntDueDateBox").add(self.dueDateEntry)
        self.dueDateEntry.show()

        self.writeDateEntry = dateentry.DateEntry()
        self.builder.get_object("pymntWritingDateBox").add(self.writeDateEntry)
        self.writeDateEntry.show()
        self.pymntDescEntry = self.builder.get_object("pymntDescEntry")
        self.bankEntry = self.builder.get_object("bankEntry")
        page = self.builder.get_object("notebook1").get_current_page()
        sellFlag = None
        if page == 0:
            sellFlag = True
        elif page == 1:
            sellFlag = False
            self.builder.get_object("payerLbl").set_text("Payid to:")
            self.builder.get_object("chooseBankBtn").set_sensitive(False)
        self.bankCombo = self.builder.get_object('bank_names_combo')
        model = Gtk.ListStore(str)
        self.bankCombo.set_model(model)
        if sellFlag:  # other's cheque
            banks = self.bankaccounts_class.get_bank_names()
        else:
            banks = self.bankaccounts_class.get_all_accounts()
        for item in banks:
            iter = model.append()
            name = item.Name if sellFlag else item.accName
            model.set(iter, 0, name)
        cell = Gtk.CellRendererText()
        self.bankCombo.pack_start(cell, True)
        self.serialNoEntry = self.builder.get_object("serialNoEntry")
        self.payerEntry = self.builder.get_object("payerNameEntry")
        self.customerNameLbl = self.builder.get_object("customerNameLbl")
        self.addPymntDlg.show_all()

    def submitPayment(self, sender=0):
        if self.validatePayment() == False:
            return
        pymntAmnt = self.pymntAmntEntry.get_float()
        wrtDate = self.writeDateEntry.getDateObject()
        dueDte = self.dueDateEntry.getDateObject()
        bank = int(self.bankCombo.get_active()) + 1
        # if self.sellFlag:
        #     bank_name = self.bankaccounts_class.get_bank_name(bank)
        # else:
        #     bank_name = self.bankaccounts_class.get_account(bank).accName
        serial = self.serialNoEntry.get_text()
        pymntDesc = self.pymntDescEntry.get_text()
        payer = self.payerEntry.get_text()
        pymnt_str = utility.LN(pymntAmnt)

        cheque = share.config.db.session.query(Cheque).filter(
            Cheque.chqId == self.code) .first()
        cheque.chqAmount = pymntAmnt
        cheque.chqWrtDate = wrtDate
        cheque.chqDueDate = dueDte
        cheque.chqSerial = serial
        cheque.chqCust = int(self.builder.get_object(
            "payerNameEntry").get_text())
        cheque.chqAccount = bank
        cheque.chqDesc = pymntDesc

        ch = cheque
        ch_history = ChequeHistory(ch.chqId, ch.chqAmount, ch.chqWrtDate, ch.chqDueDate, ch.chqSerial,
                                   ch.chqStatus, ch.chqCust, ch.chqAccount, ch.chqTransId, ch.chqDesc, self.current_time)
        share.config.db.session.add(ch_history)
        share.config.db.session.commit()
        self.addPymntDlg.hide()
        self.searchFilter()

    def cancelPayment(self, sender=0, ev=0):
        self.addPymntDlg.hide()
        return True

    def on_add_bank_clicked(self, sender):
        model = self.bankCombo.get_model()
        self.bankaccounts_class.addNewBank(model)

    def odatAzMoshtari(self, sender):
        msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL,
                                   _("Are you sure to return this cheque?"))
        msgbox.set_title(_("Are you sure?"))
        result = msgbox.run()

        if result == Gtk.ResponseType.CANCEL:
            msgbox.destroy()
            return
        self.getSelection()
        result = share.config.db.session.query(Cheque, Customers)
        result = result.filter(Customers.custId == Cheque.chqCust)
        result = result.filter(Cheque.chqId == self.code).first()
        stat = result.Cheque.chqStatus
        result.Cheque.chqStatus = 6
        ch_history = ChequeHistory(result.Cheque.chqId, result.Cheque.chqAmount, result.Cheque.chqWrtDate, result.Cheque.chqDueDate, result.Cheque.chqSerial,
                                   result.Cheque.chqStatus, result.Cheque.chqCust, result.Cheque.chqAccount, result.Cheque.chqTransId, result.Cheque.chqDesc, self.current_time)

        document = class_document.Document()
        document.add_notebook(result.Customers.custSubj, result.Cheque.chqAmount, _(
            'Cheque with serial No. ')+result.Cheque.chqSerial + _(' returned from ')+result.Customers.custName)
        if stat == 5:
            document.add_notebook(dbconf.get_int('other_cheque'), -result.Cheque.chqAmount, _(
                'Cheque with serial No. ')+result.Cheque.chqSerial + _(' returned from ')+result.Customers.custName)
        else:
            document.add_notebook(dbconf.get_int('our_cheque'), -result.Cheque.chqAmount, _(
                'Cheque with serial No. ')+result.Cheque.chqSerial + _(' returned from ')+result.Customers.custName)
        document.save()

        share.config.db.session.add(ch_history)
        share.config.db.session.commit()
        share.mainwin.silent_daialog(
            _("The operation was completed successfully."))
        self.searchFilter()
        msgbox.destroy()

    def odatBeMoshtari(self, sender):
        msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL,
                                   _("Are you sure to return this cheque?"))
        msgbox.set_title(_("Are you sure?"))
        result = msgbox.run()

        if result == Gtk.ResponseType.CANCEL:
            msgbox.destroy()
            return
        self.getSelection()
        result = share.config.db.session.query(Cheque, Customers)
        result = result.filter(Customers.custId == Cheque.chqCust)
        result = result.filter(Cheque.chqId == self.code).first()
        result.Cheque.chqStatus = 7
        ch_history = ChequeHistory(result.Cheque.chqId, result.Cheque.chqAmount, result.Cheque.chqWrtDate, result.Cheque.chqDueDate, result.Cheque.chqSerial,
                                   result.Cheque.chqStatus, result.Cheque.chqCust, result.Cheque.chqAccount, result.Cheque.chqTransId, result.Cheque.chqDesc, self.current_time)
        share.config.db.session.add(ch_history)
        share.config.db.session.commit()

        document = class_document.Document()
        document.add_notebook(result.Customers.custSubj, -result.Cheque.chqAmount, _(
            'Cheque with serial No. ')+result.Cheque.chqSerial + _(' returned to ')+result.Customers.custName)
        document.add_notebook(dbconf.get_int('other_cheque'), result.Cheque.chqAmount, _(
            'Cheque with serial No. ')+result.Cheque.chqSerial + _(' returned to ')+result.Customers.custName)
        document.save()

        share.config.db.session.commit()
        share.mainwin.silent_daialog(
            _("The operation was completed successfully."))
        self.searchFilter()
        msgbox.destroy()

    def bargasht(self, sender):
        msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL,
                                   _("Are you sure to bounce this cheque?"))
        msgbox.set_title(_("Are you sure?"))
        result = msgbox.run()

        if result == Gtk.ResponseType.CANCEL:
            msgbox.destroy()
            return
        self.getSelection()
        result = share.config.db.session.query(Cheque, Customers)
        result = result.filter(Customers.custId == Cheque.chqCust)
        result = result.filter(Cheque.chqId == self.code).first()
        stat = result.Cheque.chqStatus

        document = class_document.Document()
        result.Cheque.chqStatus = 8 if stat in (1, 2, 5) else 9
        if stat in (1, 2, 5):  # our
            result.Cheque.chqStatus = 8
            document.add_notebook(result.Customers.custSubj,
                                  result.Cheque.chqAmount, _('Bounced cheque'))
            document.add_notebook(dbconf.get_int(
                'our_cheque'), -result.Cheque.chqAmount, _('Bounced cheque'))
        elif stat in (3, 4):  # their
            result.Cheque.chqStatus = 9
            document.add_notebook(
                result.Customers.custSubj, -result.Cheque.chqAmount, _('Bounced cheque'))
            document.add_notebook(dbconf.get_int(
                'other_cheque'), result.Cheque.chqAmount, _('Bounced cheque'))

        ch_history = ChequeHistory(result.Cheque.chqId, result.Cheque.chqAmount, result.Cheque.chqWrtDate, result.Cheque.chqDueDate, result.Cheque.chqSerial,
                                   result.Cheque.chqStatus, result.Cheque.chqCust, result.Cheque.chqAccount, result.Cheque.chqTransId, result.Cheque.chqDesc, self.current_time)
        share.config.db.session.add(ch_history)

        document.save()

        share.config.db.session.commit()
        share.mainwin.silent_daialog(
            _("The operation was completed successfully."))
        self.searchFilter()
        msgbox.destroy()

    def passShode(self, sender):
        msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL,
                                   _("Are you sure to get this cheque passed?"))
        msgbox.set_title(_("Are you sure?"))
        result = msgbox.run()

        if result == Gtk.ResponseType.CANCEL:
            msgbox.destroy()
            return
        self.getSelection()
        document = class_document.Document()

        result = share.config.db.session.query(Cheque).filter(
            Cheque.chqId == self.code).first()
        status = result.chqStatus
        if status == 3 or status == 10:
            sub = subjects.Subjects(parent_id=[1, 14])
            sub.connect('subject-selected', self.casheCheque)

        if status == 1:
            result.chqStatus = 2
            if status == 1:  # pass
                ba = class_bankaccounts.BankAccountsClass()
                accName = ba.get_account(result.chqAccount).accName
                banksub = share.config.db.session.query(Subject).filter(Subject.parent_id == (
                    dbconf.get_int('bank'))).filter(Subject.name == accName).first().id
                document.add_notebook(banksub, result.chqAmount, _(
                    "Cheque with serial No.")+result.chqSerial + _('Passed'))
                document.add_notebook(dbconf.get_int('our_cheque'), _(
                    "Cheque with serial No.")+result.chqSerial + -result.chqAmount, _('Passed'))

        ch_history = ChequeHistory(result.chqId, result.chqAmount, result.chqWrtDate, result.chqDueDate, result.chqSerial,
                                   result.chqStatus, result.chqCust, result.chqAccount, result.chqTransId, result.chqDesc, self.current_time)
        share.config.db.session.add(ch_history)
        document.save()
        share.config.db.session.commit()
        share.mainwin.silent_daialog(
            _("The operation was completed successfully."))
        self.searchFilter()
        msgbox.destroy()

    def darJaryanVosul(self, sender):
        msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL,
                                   _("Are you sure to float this cheque?"))
        msgbox.set_title(_("Are you sure?"))
        result = msgbox.run()

        if result == Gtk.ResponseType.CANCEL:
            msgbox.destroy()
            return
        self.getSelection()
        result = share.config.db.session.query(Cheque).filter(
            Cheque.chqId == self.code).first()
        status = result.chqStatus
        result.chqStatus = 10
        document = class_document.Document()
        document.add_notebook(dbconf.get_int('float'), -result.chqAmount,
                              _("Cheque with serial No.")+result.chqSerial + _('Floated'))
        document.add_notebook(dbconf.get_int('other_cheque'), result.chqAmount, _(
            "Cheque with serial No.")+result.chqSerial + _('Floated'))
        ch_history = ChequeHistory(result.chqId, result.chqAmount, result.chqWrtDate, result.chqDueDate, result.chqSerial,
                                   result.chqStatus, result.chqCust, result.chqAccount, result.chqTransId, result.chqDesc, self.current_time)
        share.config.db.session.add(ch_history)
        document.save()
        share.config.db.session.commit()
        share.mainwin.silent_daialog(
            _("The operation was completed successfully."))
        self.searchFilter()
        msgbox.destroy()

    def casheCheque(self, subject, id, code, name):
        result = share.config.db.session.query(Cheque, Customers)
        result = result.filter(Customers.custId == Cheque.chqCust)
        result = result.filter(Cheque.chqId == self.code).first()
        status = result.Cheque.chqStatus
        result.Cheque.chqStatus = 4
        document = class_document.Document()
        chequeValue = result.Cheque.chqAmount
        desc = _("Cheque with serial No.") + \
            result.Cheque.chqSerial + _('Cashed')
        if status == 10:
            document.add_notebook(id, -chequeValue, desc)
            document.add_notebook(dbconf.get_int('float'), chequeValue, desc)
        elif status == 3:
            document.add_notebook(id, -chequeValue, desc)
            document.add_notebook(dbconf.get_int(
                'other_cheque'), chequeValue, desc)
        ch_history = ChequeHistory(result.Cheque.chqId, result.Cheque.chqAmount, result.Cheque.chqWrtDate, result.Cheque.chqDueDate, result.Cheque.chqSerial,
                                   result.Cheque.chqStatus, result.Cheque.chqCust, result.Cheque.chqAccount, result.Cheque.chqTransId, result.Cheque.chqDesc, self.current_time)
        share.config.db.session.add(ch_history)
        document.save()
        share.config.db.session.commit()
        subject.window.destroy()
        share.mainwin.silent_daialog(
            _("The operation was completed successfully."))
        self.searchFilter()

    def on_dialog_destroy(self, sender, data=None):
        sender.hide()
        return True

    def selectChequeFromTreeview(self, treeview, path, view_column):
        treestore = treeview.get_model()
        iter = treestore.get_iter(path)
        if iter != None:
            self.code = convertToLatin(treestore.get(iter, 0)[0])
            self.showHistory(self.code)

    def format_date(self, date):
        year, month, day = int(date[0]), int(date[1]), int(date[2])

        if share.config.datetypes[share.config.datetype] == "jalali":
            jd = self.cal.gregorian_to_jd(year, month, day)
            year, month, day = self.cal.jd_to_gregorian(jd)

        delim = share.config.datedelims[share.config.datedelim]
        datelist = ["", "", ""]
        datelist[share.config.datefields["year"]] = str(year)
        datelist[share.config.datefields["month"]] = str(month)
        datelist[share.config.datefields["day"]] = str(day)

        return delim.join(datelist)

    def showHistory(self, code):
        self.treestoreHistory.clear()
        result = share.config.db.session.query(ChequeHistory, Cheque, Customers.custName)\
            .join(Cheque, ChequeHistory.ChequeId == Cheque.chqId).join(Customers,  Customers.custId == Cheque.chqCust)\
            .filter(ChequeHistory.ChequeId == code).all()

        for chequeHistory, cheque, cust in result:
            chqWrtDate = self.format_date(str(chequeHistory.WrtDate).split('-'))
            chqDueDate = self.format_date(str(chequeHistory.DueDate).split('-'))

            if (chequeHistory.Status == 2) or (chequeHistory.Status == 4):
                clear = 'Cleared'
            else:
                clear = 'Not Cleared'

            chqBill = share.config.db.session.query(Notebook.bill_id).filter(
                Notebook.chqId == cheque.chqId).first()
            if chqBill:
                chqBill = chqBill.bill_id
            else:
                chqBill = 0
            self.treestoreHistory.append(None, (str(chequeHistory.ChequeId), str(chequeHistory.Amount), str(chqWrtDate), str(chqDueDate), str(chequeHistory.Serial), str(clear),
                str(cust), str(chequeHistory.Account), str(chequeHistory.TransId), str(chequeHistory.Desc), str(chequeHistory.Date), str(chqBill), str(self.chequeStatus[chequeHistory.Status])))
            self.historywindow.show_all()

    def on_select_cell(self, sender=0):
        self.builder.get_object("odatAsMoshtariButton").set_sensitive(True)
        self.builder.get_object("odatBeMoshtariButton").set_sensitive(True)
        self.builder.get_object("bargashtButton").set_sensitive(True)
        self.builder.get_object("passButton").set_sensitive(True)
        self.builder.get_object("deleteButton").set_sensitive(True)
        self.builder.get_object("editButton").set_sensitive(True)
        self.builder.get_object("JaryanButton").set_sensitive(True)
        self.getSelection()
        result = share.config.db.session.query(Cheque)
        result = result.filter(Cheque.chqId == self.code).first()
        if result.chqStatus not in [1, 5]:          # [2,3,4,5,6,7,8,9]: # 1
            self.builder.get_object(
                "odatAsMoshtariButton").set_sensitive(False)
        if result.chqStatus != 3:           # [1,2,4,5,6,7,8]: # 3
            self.builder.get_object(
                "odatBeMoshtariButton").set_sensitive(False)
        if result.chqStatus not in [1, 3, 5, 10]:  # [2,4,6,7,8]:   # 1 , 3 , 5
            self.builder.get_object("bargashtButton").set_sensitive(False)
            self.builder.get_object("passButton").set_sensitive(False)
        if result.chqStatus not in [1, 3]:
            self.builder.get_object("editButton").set_sensitive(False)
        if result.chqStatus in [2, 4]:
            self.builder.get_object("editButton").set_sensitive(False)
            self.builder.get_object("deleteButton").set_sensitive(False)
            self.builder.get_object("passButton").set_sensitive(False)
            self.builder.get_object("bargashtButton").set_sensitive(False)
        if result.chqStatus != 3:
            self.builder.get_object("JaryanButton").set_sensitive(False)
        if result.chqDelete == True:
            self.builder.get_object("editButton").set_sensitive(False)
            self.builder.get_object("deleteButton").set_sensitive(False)
            self.builder.get_object("passButton").set_sensitive(False)
            self.builder.get_object("bargashtButton").set_sensitive(False)
            self.builder.get_object(
                "odatBeMoshtariButton").set_sensitive(False)
            self.builder.get_object(
                "odatAsMoshtariButton").set_sensitive(False)

    def on_switch_page(self, sender, tree,  page, data=0):
        self.currentTreeview = page
        self.builder.get_object("totalLbl").set_text(str(self.totals[page]))

    def on_delete(self, sender):
        msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL,
                                   _("Are you sure to delete the cheque?"))
        msgbox.set_title(_("Are you sure?"))
        result = msgbox.run()

        if result == Gtk.ResponseType.OK:
            self.getSelection()
            result = share.config.db.session.query(Cheque).filter(
                Cheque.chqId == self.code).first()

            notebook = share.config.db.session.query(
                Notebook).filter(Notebook.chqId == result.chqId)
            bill_id = notebook.first().bill_id
            notebook.delete()
            noteCount = share.config.db.session.query(count(Notebook.bill_id)).filter(
                Notebook.bill_id == bill_id).first()[0]
            if noteCount == 0:
                share.config.db.session.query(Bill).filter(
                    Bill.id == bill_id).delete()

            result.chqDelete = True
            ch_history = ChequeHistory(result.chqId, result.chqAmount, result.chqWrtDate, result.chqDueDate, result.chqSerial, result.chqStatus,
                                       result.chqCust, result.chqAccount, result.chqTransId, result.chqDesc, self.current_time, result.chqDelete)
            share.config.db.session.add(ch_history)
            share.config.db.session.commit()

            share.mainwin.silent_daialog(
                _("The operation was completed successfully."))
            self.searchFilter()
        msgbox.destroy()

    def createHistoryTreeview(self):
        self.historywindow = self.builder.get_object("window1")
        self.historywindow.set_title("Cheque History")

        self.treeviewHistory = self.builder.get_object("treeviewHistory")
        self.treestoreHistory = Gtk.TreeStore(
            str, str, str, str, str, str, str, str, str, str, str, str, str)
        self.treeviewHistory.set_model(self.treestoreHistory)

        column = Gtk.TreeViewColumn(_("ID"), Gtk.CellRendererText(), text=0)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(0)
        column.set_sort_indicator(True)
        self.treeviewHistory.append_column(column)

        column = Gtk.TreeViewColumn(
            _("Amount"), Gtk.CellRendererText(), text=1)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(4)
        column.set_sort_indicator(True)
        self.treeviewHistory.append_column(column)

        column = Gtk.TreeViewColumn(
            _("Write Date"), Gtk.CellRendererText(), text=2)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(5)
        column.set_sort_indicator(True)
        self.treeviewHistory.append_column(column)

        column = Gtk.TreeViewColumn(
            _("Due Date"), Gtk.CellRendererText(), text=3)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(5)
        column.set_sort_indicator(True)
        self.treeviewHistory.append_column(column)

        column = Gtk.TreeViewColumn(
            _("Serial"), Gtk.CellRendererText(), text=4)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        column.set_sort_indicator(True)
        self.treeviewHistory.append_column(column)

        column = Gtk.TreeViewColumn(_("Clear"), Gtk.CellRendererText(), text=5)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        column.set_sort_indicator(True)
        self.treeviewHistory.append_column(column)

        column = Gtk.TreeViewColumn(
            _("Customer Name"), Gtk.CellRendererText(), text=6)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        column.set_sort_indicator(True)
        self.treeviewHistory.append_column(column)

        column = Gtk.TreeViewColumn(
            _("Account"), Gtk.CellRendererText(), text=7)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        column.set_sort_indicator(True)
        self.treeviewHistory.append_column(column)

        column = Gtk.TreeViewColumn(
            _("Transaction ID"), Gtk.CellRendererText(), text=8)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        column.set_sort_indicator(True)
        self.treeviewHistory.append_column(column)

        column = Gtk.TreeViewColumn(
            _("Description"), Gtk.CellRendererText(), text=9)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(3)
        column.set_sort_indicator(True)
        self.treeviewHistory.append_column(column)

        column = Gtk.TreeViewColumn(
            _("History Date"), Gtk.CellRendererText(), text=10)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(3)
        column.set_sort_indicator(True)
        self.treeviewHistory.append_column(column)

        column = Gtk.TreeViewColumn(
            _("Bill ID"), Gtk.CellRendererText(), text=11)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(3)
        column.set_sort_indicator(True)
        self.treeviewHistory.append_column(column)

        column = Gtk.TreeViewColumn(
            _("Status"), Gtk.CellRendererText(), text=12)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(3)
        column.set_sort_indicator(True)
        self.treeviewHistory.append_column(column)
        self.builder.connect_signals(self)

    def validatePayment(self):
        errFlg = False
        msg = ""

        dueDte = self.dueDateEntry.get_text()
        if dueDte == "":
            msg += _("You must enter the due date for the non-cash payment.\n")
            errFlg = True

        payment = self.pymntAmntEntry.get_text()
        if payment == "":
            msg += _("You must enter the Amount for cheque ")
            errFlg = True

        wrtDate = self.writeDateEntry.get_text()
        if wrtDate == "":
            msg = _("You must enter a writing date for the cheque.\n")
            errFlg = True

        serialNo = self.serialNoEntry.get_text()
        if serialNo == "":
            msg += _("You must enter the serial number for the non-cash payment.\n")
            errFlg = True

        # ----values:
        if errFlg:
            msg = _("The payment cannot be saved.\n\n%s") % msg
            msgbox = Gtk.MessageDialog(self.addPymntDlg, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING,
                                       Gtk.ButtonsType.OK, msg)
            msgbox.set_title(_("Invalid data"))
            msgbox.run()
            msgbox.destroy()
            return False
        else:
            return True

    def selectCustomers(self, sender=0):
        customer_win = customers.Customer()
        customer_win.viewCustomers()
        customer_win.connect("customer-selected", self.sellerSelected)

    def sellerSelected(self, sender, id, code):
        self.builder.get_object("payerNameEntry").set_text(code)
        sender.window.destroy()
        self.setCustomerName()

    def setCustomerName(self, sender=0, ev=0):
        ccode = self.builder.get_object("payerNameEntry").get_text()
        query = share.config.db.session.query(Customers).select_from(Customers)
        customer = query.filter(Customers.custCode == ccode).first()
        self.builder.get_object("customerNameLbl").set_text("")
        if customer:
            self.builder.get_object(
                "customerNameLbl").set_text(customer.custName)
