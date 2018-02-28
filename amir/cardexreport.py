import gi
from gi.repository import Gtk
from datetime import date
import os
import platform

from sqlalchemy import or_
from sqlalchemy.orm.util import outerjoin
from sqlalchemy.sql import between, and_
from sqlalchemy.sql.functions import sum

import utility
import printreport
import previewreport
from database import *
from dateentry import *
from share import share
from helpers import get_builder

config = share.config

class CardexReport:
    def __init__(self):
        self.builder = get_builder("cardex")
        self.window = self.builder.get_object("window1")
        
        self.treeview = self.builder.get_object("tradeTreeView")
        self.treestore = Gtk.TreeStore(str, str, str, str, str, str, str)
        self.treeview.set_model(self.treestore)

        column = Gtk.TreeViewColumn(_("Factor Code"), Gtk.CellRendererText(), text = 0)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(0)
        column.set_sort_indicator(True)
        self.treeview.append_column(column)

        column = Gtk.TreeViewColumn(_("Customer Code"), Gtk.CellRendererText(), text = 1)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        column.set_sort_indicator(True)
        self.treeview.append_column(column)

        column = Gtk.TreeViewColumn(_("Customer Name"), Gtk.CellRendererText(), text = 2)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        column.set_sort_indicator(True)
        self.treeview.append_column(column)
        
        column = Gtk.TreeViewColumn(_("Sell Quantity"), Gtk.CellRendererText(), text = 3)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(2)
        column.set_sort_indicator(True)
        self.treeview.append_column(column)

        column = Gtk.TreeViewColumn(_("Buy Quantity"), Gtk.CellRendererText(), text = 4)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(3)
        column.set_sort_indicator(True)
        self.treeview.append_column(column)
        
        column = Gtk.TreeViewColumn(_("Total Price"), Gtk.CellRendererText(), text = 5)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(4)
        column.set_sort_indicator(True)
        self.treeview.append_column(column)

        column = Gtk.TreeViewColumn(_("Date"), Gtk.CellRendererText(), text = 6)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(5)
        column.set_sort_indicator(True)
        self.treeview.append_column(column)
        
        self.treeview.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        #self.treestore.set_sort_func(0, self.sortGroupIds)
        self.treestore.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        self.window.show_all()
        self.builder.connect_signals(self)

    def show(self, productCode,factorType,customerCode,dateFrom,dateTo):
        query = config.db.session.query(Products)
        query = query.filter(Products.code == productCode)
        bill  = query.first()
        if bill is not None:
            box = self.builder.get_object("statusTextView").get_buffer().set_text('')
            box = self.builder.get_object("nameTextView").get_buffer().set_text(bill.name)
            box = self.builder.get_object("groupTextView").get_buffer().set_text(str(bill.accGroup))
            box = self.builder.get_object("locationTextView").get_buffer().set_text(bill.location)
            box = self.builder.get_object("quantityTextView").get_buffer().set_text(str(bill.quantity))
            box = self.builder.get_object("quantityWarningTextView").get_buffer().set_text(str(bill.qntyWarning))
            box = self.builder.get_object("oversellTextView").get_buffer().set_text(str(bill.oversell))
            box = self.builder.get_object("purchacePriceTextView").get_buffer().set_text(str(bill.purchacePrice))
            box = self.builder.get_object("dicountFormulaTextView").get_buffer().set_text(str(bill.discountFormula))
            box = self.builder.get_object("sellingPriceTextView").get_buffer().set_text(str(bill.sellingPrice))
            box = self.builder.get_object("productDescriptionTextView").get_buffer().set_text(bill.productDesc)

            self.treestore.clear()
            
            #Fill factor treeview
            query = config.db.session.query(Exchanges,Trades,Customers)
            query = query.filter(bill.id == Exchanges.exchngProduct, Exchanges.exchngTransId == Trades.Id, Customers.custId == Trades.Cust)
            if factorType:
                if factorType == 'Sell':
                    factorType = 1
                else:
                    factorType = 0
                query = query.filter(Trades.Sell == factorType)

            if customerCode:
                query = query.filter(Customers.custCode == customerCode)

            result = query.all()
            
            for factor in result:
                if factor.Trades.Sell == True:
                    buy_quantity = '-'
                    sell_quantity = str(factor.Exchanges.exchngQnty)
                else:
                    buy_quantity = str(factor.Exchanges.exchngQnty)
                    sell_quantity = '-'
                self.treestore.append(None, (str(factor.Trades.Code), str(factor.Customers.custCode), str(factor.Customers.custName), str(sell_quantity), str(buy_quantity),
                 str(factor.Exchanges.exchngQnty * factor.Exchanges.exchngUntPrc), str(factor.Trades.tDate)))
        else:
            box = self.builder.get_object("statusTextView").get_buffer().set_text("Not Found")
        self.window.show_all()

    def searchProduct(self,sender):
        # Get data from DB
        box = self.builder.get_object("productCodeSearchEntry")
        productCode = box.get_text()
        self.show(productCode,0,0,0,0)
        

    def factorFilter(self,sender):
        combo = self.builder.get_object("typeComboBox")
        index = combo.get_active()
        model = combo.get_model()
        item = model[index]

        box = self.builder.get_object("productCodeSearchEntry")
        productCode = box.get_text()

        box = self.builder.get_object("customerCodeEntry")
        customerCode = box.get_text()
        if index == -1:
            productType = None
        else:
            productType = item[0]
        self.show(productCode,productType,customerCode,0,0)