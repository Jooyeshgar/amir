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
import  customers
import  product
from gi.repository import Gdk
from calverter import calverter
from converter import *
from datetime import datetime, timedelta

config = share.config

class CardexReport:
    def __init__(self):
        self.builder = get_builder("cardex")
        self.window = self.builder.get_object("window1")
        
        self.treeview = self.builder.get_object("factorTreeView")
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
        self.session = config.db.session  

        self.dateToEntry = self.builder.get_object("dateToEntry")
        self.dateFromEntry = self.builder.get_object("dateFromEntry")
        delimiter = config.datedelims[config.datedelim] 
        if share.config.datetypes[share.config.datetype] == "jalali":
            placeH = "1396"+delimiter+"1"+ delimiter +"1"
            self.dateToEntry.set_placeholder_text(placeH)
            self.dateFromEntry.set_placeholder_text(placeH)
        else:
            placeH = "1"+delimiter+"1"+delimiter+"2018"
            self.dateToEntry.set_placeholder_text(placeH)
            self.dateFromEntry.set_placeholder_text(placeH)

    def selectProduct(self,sender=0):
        self.proVal = self.builder.get_object("productCodeSearchEntry")
        obj = product.Product()
        obj.viewProducts()
        obj.connect("product-selected",self.proSelected)
        id = self.proVal.get_text()     
        prod= config.db.session.query(Products).filter(Products.id==id).first()
        if prod:
            code = prod.code
            group = prod.accGroup
            obj.highlightProduct(unicode(code) , unicode(group))

    def proSelected(self,sender=0, id=0, code=0):
        id = unicode(id)        
        if sender:
            self.proVal.set_text(id)
            sender.window.destroy()


    def selectCustomers(self,sender=0):
        self.customerEntry      = self.builder.get_object("customerCodeEntry")
        customer_win = customers.Customer()
        customer_win.viewCustomers()
        code = self.customerEntry.get_text()
        if code != '':
            customer_win.highlightCust(code)
        customer_win.connect("customer-selected", self.sellerSelected)

    def sellerSelected(self, sender, id, code):
        self.customerEntry.set_text(code)
        sender.window.destroy()             

    def showResult(self, productCode,factorType,customerCode,dateFrom,dateTo):
        query = config.db.session.query(Products)
        query = query.filter(Products.code == productCode)
        bill  = query.first()
        self.treestore.clear()
        if bill is not None:
            statusbar = self.builder.get_object('statusbar3')
            context_id = statusbar.get_context_id('statusbar')
            statusbar.remove_all(context_id)
            self.builder.get_object("nameTextView").get_buffer().set_text(bill.name)
            self.builder.get_object("groupTextView").get_buffer().set_text(str(bill.accGroup))
            self.builder.get_object("locationTextView").get_buffer().set_text(bill.location)
            self.builder.get_object("quantityTextView").get_buffer().set_text(utility.LN(format(float(bill.quantity))))
            self.builder.get_object("quantityWarningTextView").get_buffer().set_text(utility.LN(format(float(bill.qntyWarning))))
            self.builder.get_object("oversellTextView").get_buffer().set_text(str(bill.oversell))
            self.builder.get_object("purchacePriceTextView").get_buffer().set_text(utility.LN(format(float(bill.purchacePrice))))
            self.builder.get_object("dicountFormulaTextView").get_buffer().set_text(str(bill.discountFormula))
            self.builder.get_object("sellingPriceTextView").get_buffer().set_text(utility.LN(format(float(bill.sellingPrice))))
            self.builder.get_object("productDescriptionTextView").get_buffer().set_text(bill.productDesc)

            
            #Fill factor treeview
            query = config.db.session.query(FactorItems,Factors,Customers)
            query = query.filter(bill.id == FactorItems.productId, FactorItems.factorId == Factors.Id, Customers.custId == Factors.Cust)
            if factorType and factorType != 'All':
                if factorType == 'Sell':
                    factorType = 1
                else:
                    factorType = 0
                query = query.filter(Factors.Sell == factorType)

            if customerCode:
                query = query.filter(Customers.custCode == customerCode)

            if share.config.datetypes[share.config.datetype] == "jalali":
                if dateTo:
                    year, month, day = str(dateTo).split("-")
                    e=jalali_to_gregorian(int(year),int(month),int(day))
                    dateTo = datetime(e[0], e[1], e[2])
                if dateFrom:
                    year, month, day = dateFrom.split("-")
                    e=jalali_to_gregorian(int(year),int(month),int(day))
                    dateFrom = datetime(e[0], e[1], e[2])
            else:

                if dateTo:
                    year, month, day = str(dateTo).split("-")
                    dateTo = datetime(int(day),int(month),int(year))
                if dateFrom:
                    year, month, day = dateFrom.split("-")
                    dateFrom = datetime(int(day),int(month),int(year))

            if dateTo:
                query = query.filter(Factors.tDate <= dateTo)
            if dateFrom:
                DD = timedelta(days=1)
                dateFrom -= DD
                query = query.filter(Factors.tDate >= dateFrom)
                

            result = query.all()
            
            for factor in result:
                if factor.Factors.Sell == True:
                    buy_quantity = '-'
                    sell_quantity = str(utility.LN(float(factor.FactorItems.qnty)))
                else:
                    buy_quantity = str(utility.LN(float(factor.FactorItems.qnty)))
                    sell_quantity = '-'
                if share.config.datetypes[share.config.datetype] == "jalali": 
                    year, month, day = str(factor.Factors.tDate).split("-")
                    date = gregorian_to_jalali(int(year),int(month),int(day))
                    date = str(date[2]) + '-' + str(date[1]) + '-' + str(date[0])
                else:
                    year, month, day = str(factor.Factors.tDate).split("-")
                    date = str(day) + '-' + str(month) + '-' + str(year)
                self.treestore.append(None, (str(factor.Factors.Code), str(factor.Customers.custCode), str(factor.Customers.custName), sell_quantity, buy_quantity,
                 str(utility.LN(float(factor.FactorItems.qnty * factor.FactorItems.untPrc))), str(date)))
        else:
            statusbar = self.builder.get_object('statusbar3')
            context_id = statusbar.get_context_id('statusbar')
            statusbar.push(context_id,_('Not Found'))
        self.window.show_all()

    def searchProduct(self,sender):
        # Get data from DB
        box = self.builder.get_object("productCodeSearchEntry")
        productCode = box.get_text()
        self.showResult(productCode,0,0,0,0)
        

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

        delimiter = config.datedelims[config.datedelim] 
        dateTo = self.dateToEntry.get_text()
        dateTo = dateTo.replace(delimiter, "-")

        dateFrom = self.dateFromEntry.get_text()
        dateFrom = dateFrom.replace(delimiter, "-")

        self.showResult(productCode,productType,customerCode,dateFrom,dateTo)