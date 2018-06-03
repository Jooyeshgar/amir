import gi
from gi.repository import Gtk

from sqlalchemy import or_
from sqlalchemy.orm.util import outerjoin
from sqlalchemy.sql import between, and_
from sqlalchemy.sql.functions import sum

from database import *
from dateentry import *
from share import share
from helpers import get_builder
from gi.repository import Gdk
from converter import *
from datetime import datetime, timedelta

config = share.config

class ChequeReport:
    def __init__(self):
        self.builder = get_builder("chequereport")
        self.window = self.builder.get_object("windowChequeReport")
        
        self.treeviewIncoming = self.builder.get_object("treeviewIncoming")
        self.treeviewOutgoing = self.builder.get_object("treeviewOutgoing")
        self.treestoreIncoming = Gtk.TreeStore(str, str, str, str, str, str, str, str, str, str, str, str, str, str)
        self.treestoreOutgoing = Gtk.TreeStore(str, str, str, str, str, str, str, str, str, str, str, str, str, str)
        self.treeviewIncoming.set_model(self.treestoreIncoming)
        self.treeviewOutgoing.set_model(self.treestoreOutgoing)

        column = Gtk.TreeViewColumn(_("ID"), Gtk.CellRendererText(), text = 0)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(0)
        column.set_sort_indicator(True)
        self.treeviewIncoming.append_column(column)
        column = Gtk.TreeViewColumn(_("ID"), Gtk.CellRendererText(), text = 0)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(0)
        column.set_sort_indicator(True)
        self.treeviewOutgoing.append_column(column)

        column = Gtk.TreeViewColumn(_("Amount"), Gtk.CellRendererText(), text = 1)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(4)
        column.set_sort_indicator(True)
        self.treeviewIncoming.append_column(column)
        column = Gtk.TreeViewColumn(_("Amount"), Gtk.CellRendererText(), text = 1)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(4)
        column.set_sort_indicator(True)
        self.treeviewOutgoing.append_column(column)

        column = Gtk.TreeViewColumn(_("Write Date"), Gtk.CellRendererText(), text = 2)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(5)
        column.set_sort_indicator(True)
        self.treeviewIncoming.append_column(column)
        column = Gtk.TreeViewColumn(_("Write Date"), Gtk.CellRendererText(), text = 2)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(5)
        column.set_sort_indicator(True)
        self.treeviewOutgoing.append_column(column)

        column = Gtk.TreeViewColumn(_("Due Date"), Gtk.CellRendererText(), text = 3)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(5)
        column.set_sort_indicator(True)
        self.treeviewIncoming.append_column(column)
        column = Gtk.TreeViewColumn(_("Due Date"), Gtk.CellRendererText(), text = 3)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(5)
        column.set_sort_indicator(True)
        self.treeviewOutgoing.append_column(column)

        column = Gtk.TreeViewColumn(_("Serial"), Gtk.CellRendererText(), text = 4)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        column.set_sort_indicator(True)
        self.treeviewIncoming.append_column(column)
        column = Gtk.TreeViewColumn(_("Serial"), Gtk.CellRendererText(), text = 4)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        column.set_sort_indicator(True)
        self.treeviewOutgoing.append_column(column)

        column = Gtk.TreeViewColumn(_("Clear"), Gtk.CellRendererText(), text = 5)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        column.set_sort_indicator(True)
        self.treeviewIncoming.append_column(column)
        column = Gtk.TreeViewColumn(_("Clear"), Gtk.CellRendererText(), text = 5)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        column.set_sort_indicator(True)
        self.treeviewOutgoing.append_column(column)
        
        column = Gtk.TreeViewColumn(_("Customer Name"), Gtk.CellRendererText(), text = 6)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        column.set_sort_indicator(True)
        self.treeviewIncoming.append_column(column)
        column = Gtk.TreeViewColumn(_("Customer Name"), Gtk.CellRendererText(), text = 6)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        column.set_sort_indicator(True)
        self.treeviewOutgoing.append_column(column)

        column = Gtk.TreeViewColumn(_("Account"), Gtk.CellRendererText(), text = 7)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        column.set_sort_indicator(True)
        self.treeviewIncoming.append_column(column)
        column = Gtk.TreeViewColumn(_("Account"), Gtk.CellRendererText(), text = 7)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        column.set_sort_indicator(True)
        self.treeviewOutgoing.append_column(column)

        column = Gtk.TreeViewColumn(_("Transaction ID"), Gtk.CellRendererText(), text = 8)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        column.set_sort_indicator(True)
        self.treeviewIncoming.append_column(column)
        column = Gtk.TreeViewColumn(_("Transaction ID"), Gtk.CellRendererText(), text = 8)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        column.set_sort_indicator(True)
        self.treeviewOutgoing.append_column(column)

        column = Gtk.TreeViewColumn(_("Note Book ID"), Gtk.CellRendererText(), text = 9)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(2)
        column.set_sort_indicator(True)
        self.treeviewIncoming.append_column(column)
        column = Gtk.TreeViewColumn(_("Note Book ID"), Gtk.CellRendererText(), text = 9)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(2)
        column.set_sort_indicator(True)
        self.treeviewOutgoing.append_column(column)

        column = Gtk.TreeViewColumn(_("Description"), Gtk.CellRendererText(), text = 10)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(3)
        column.set_sort_indicator(True)
        self.treeviewIncoming.append_column(column)
        column = Gtk.TreeViewColumn(_("Description"), Gtk.CellRendererText(), text = 10)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(3)
        column.set_sort_indicator(True)
        self.treeviewOutgoing.append_column(column)

        column = Gtk.TreeViewColumn(_("History ID"), Gtk.CellRendererText(), text = 11)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(3)
        column.set_sort_indicator(True)
        self.treeviewIncoming.append_column(column)
        column = Gtk.TreeViewColumn(_("History ID"), Gtk.CellRendererText(), text = 11)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(3)
        column.set_sort_indicator(True)
        self.treeviewOutgoing.append_column(column)

        column = Gtk.TreeViewColumn(_("Bill ID"), Gtk.CellRendererText(), text = 12)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(3)
        column.set_sort_indicator(True)
        self.treeviewIncoming.append_column(column)
        column = Gtk.TreeViewColumn(_("Bill ID"), Gtk.CellRendererText(), text = 12)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(3)
        column.set_sort_indicator(True)
        self.treeviewOutgoing.append_column(column)
        
        column = Gtk.TreeViewColumn(_("Order"), Gtk.CellRendererText(), text = 13)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(3)
        column.set_sort_indicator(True)
        self.treeviewIncoming.append_column(column)
        column = Gtk.TreeViewColumn(_("Order"), Gtk.CellRendererText(), text = 13)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(3)
        column.set_sort_indicator(True)
        self.treeviewOutgoing.append_column(column)
        
        self.treeviewIncoming.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        self.treeviewOutgoing.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        #self.treestore.set_sort_func(0, self.sortGroupIds)
        # self.treestore.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        self.window.show_all()
        self.builder.connect_signals(self)
        self.session = config.db.session

        self.dateFromEntry = self.builder.get_object("incomingDateFromSearchentry")
        self.dateToEntry = self.builder.get_object("incomingDateToSearchentry")
        if share.config.datetypes[share.config.datetype] == "jalali":
            self.dateToEntry.set_placeholder_text("1396:1:1")
            self.dateFromEntry.set_placeholder_text("1396:1:1")
        else:
            self.dateToEntry.set_placeholder_text("1:1:2018")
            self.dateFromEntry.set_placeholder_text("1:1:2018")

        self.dateFromEntry = self.builder.get_object("outgoingDateFromSearchentry")
        self.dateToEntry = self.builder.get_object("outgoingDateToSearchentry")
        if share.config.datetypes[share.config.datetype] == "jalali":
            self.dateToEntry.set_placeholder_text("1396:1:1")
            self.dateFromEntry.set_placeholder_text("1396:1:1")
        else:
            self.dateToEntry.set_placeholder_text("1:1:2018")
            self.dateFromEntry.set_placeholder_text("1:1:2018")

        self.showResult()

    def incomingSearchFilter(self, sender):
        box = self.builder.get_object("incomingIdSearchentry")
        chequeId = box.get_text()

        box = self.builder.get_object("incomingSerialSearchentry")
        chqSerial = box.get_text()

        box = self.builder.get_object("incomingAmountFromSearchentry")
        amountFrom = box.get_text()

        box = self.builder.get_object("incomingAmountToSearchentry")
        amountTo = box.get_text()

        box = self.builder.get_object("incomingDateFromSearchentry")
        dateFrom = box.get_text()

        box = self.builder.get_object("incomingDateToSearchentry")
        dateTo = box.get_text()
        self.showResult(None, chqSerial, amountFrom, amountTo, dateFrom, dateTo)

    def outgoingSearchFilter(self, sender):
        box = self.builder.get_object("outgoingIdSearchentry")
        chequeId = box.get_text()

        box = self.builder.get_object("outgoingSerialSearchentry")
        chqSerial = box.get_text()

        box = self.builder.get_object("outgoingAmountFromSearchentry")
        amountFrom = box.get_text()

        box = self.builder.get_object("outgoingAmountToSearchentry")
        amountTo = box.get_text()

        box = self.builder.get_object("outgoingDateFromSearchentry")
        dateFrom = box.get_text()

        box = self.builder.get_object("outgoingDateToSearchentry")
        dateTo = box.get_text()
        self.showResult(None, chqSerial, amountFrom, amountTo, dateFrom, dateTo)


    def showResult(self, chequeId=None, chqSerial=None, amountFrom=None, amountTo=None, dateFrom=None, dateTo=None):
        self.treestoreIncoming.clear()
        self.treestoreOutgoing.clear()
        result = config.db.session.query(Cheque, Customers)
        result = result.filter(Customers.custId==Cheque.chqCust)

        # Apply filters
        if chequeId:
            result = result.filter(Cheque.chqId == chequeId)
        if chqSerial:
            result = result.filter(Cheque.chqSerial == chqSerial)
        if amountFrom:
            result = result.filter(Cheque.chqAmount >= amountFrom)
        if amountTo:
            result = result.filter(Cheque.chqAmount <= amountTo)
        if share.config.datetypes[share.config.datetype] == "jalali":
            if dateTo:
                year, month, day = str(dateTo).split(":")
                e=jalali_to_gregorian(int(year),int(month),int(day))
                dateTo = datetime(e[0], e[1], e[2])
            if dateFrom:
                year, month, day = dateFrom.split(":")
                e=jalali_to_gregorian(int(year),int(month),int(day))
                dateFrom = datetime(e[0], e[1], e[2])
        else:
            if dateTo:
                year, month, day = str(dateTo).split(":")
                dateTo = datetime(int(day),int(month),int(year))
            if dateFrom:
                year, month, day = dateFrom.split(":")
                dateFrom = datetime(int(day),int(month),int(year))

        if dateTo:
            result = result.filter(Cheque.chqDueDate <= dateTo)
        if dateFrom:
            DD = timedelta(days=1)
            dateFrom -= DD
            result = result.filter(Cheque.chqDueDate >= dateFrom)

        # Show
        for cheque,customer in result:
            if share.config.datetypes[share.config.datetype] == "jalali": 
                year, month, day = str(cheque.chqWrtDate).split("-")
                chqWrtDate = gregorian_to_jalali(int(year),int(month),int(day))
                chqWrtDate = str(chqWrtDate[0]) + '-' + str(chqWrtDate[1]) + '-' + str(chqWrtDate[2])

                year, month, day = str(cheque.chqWrtDate).split("-")
                chqDueDate = gregorian_to_jalali(int(year),int(month),int(day))
                chqDueDate = str(chqDueDate[0]) + '-' + str(chqDueDate[1]) + '-' + str(chqDueDate[2])

            else:
                year, month, day = str(cheque.chqWrtDate).split("-")
                chqWrtDate = str(day) + '-' + str(month) + '-' + str(year)

                year, month, day = str(cheque.chqDueDate).split("-")
                chqDueDate = str(day) + '-' + str(month) + '-' + str(year)

            if (cheque.chqStatus == 2) or (cheque.chqStatus == 3):
                clear = 'Cleared'
            else:
                clear = 'Not Cleared'

            if (cheque.chqStatus == 3) or (cheque.chqStatus == 4):
                self.treestoreIncoming.append(None, (str(cheque.chqId), str(cheque.chqAmount), str(chqWrtDate), str(chqDueDate), str(cheque.chqSerial), str(clear), str(customer.custName), str(cheque.chqAccount), str(cheque.chqTransId), str(cheque.chqNoteBookId), str(cheque.chqDesc), str(cheque.chqHistoryId), str(cheque.chqBillId), str(cheque.chqOrder)))
            else:
                self.treestoreOutgoing.append(None, (str(cheque.chqId), str(cheque.chqAmount), str(chqWrtDate), str(chqDueDate), str(cheque.chqSerial), str(clear), str(customer.custName), str(cheque.chqAccount), str(cheque.chqTransId), str(cheque.chqNoteBookId), str(cheque.chqDesc), str(cheque.chqHistoryId), str(cheque.chqBillId), str(cheque.chqOrder)))

        self.window.show_all()

    # def searchProduct(self,sender):
    #     # Get data from DB
    #     box = self.builder.get_object("productCodeSearchEntry")
    #     productCode = box.get_text()
    #     self.showResult(productCode,0,0,0,0)