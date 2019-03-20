import gi
from gi.repository import Gtk
from datetime import date , timedelta
import os
import platform

from . import utility
from .database import *
from .dateentry import *
from .share import share
from .helpers import get_builder
from . import  customers
from . import  product
from gi.repository import Gdk
from .converter import *

import sys
if sys.version_info > (3,):
    unicode = str

config = share.config

class CardexReport:
    def __init__(self):
        self.builder = get_builder("cardex")
        self.window = self.builder.get_object("window1")

        self.treeview = self.builder.get_object("factorTreeView")
        self.treestore = Gtk.TreeStore(str, str, str, str, str, str, str,str , str)
        self.treeview.set_model(self.treestore)

        headers = (_("Date"),_("Type"),_("Quantity"), _("Unit Price"),_("Total Price"),_("Remained"), _("Factor Code") , _("Customer Name"),_("Customer Code") )
        #headers = (_("Factor Code") ,_("Customer Code"), _("Customer Name"),_("Stock inventory"),_("Sell Quantity"),_("Buy Quantity") , _("Total Price"),_("Date") )
        i = 0
        for header in headers :
            column = Gtk.TreeViewColumn(header, Gtk.CellRendererText(), text = i)
            column.set_spacing(5)
            column.set_resizable(True)
            column.set_sort_column_id(i)
            column.set_sort_indicator(True)
            self.treeview.append_column(column)
            i+=1
        self.rows = []
        self.window.show_all()
        self.builder.connect_signals(self)
        self.session = config.db.session

        self.dateToEntry = self.builder.get_object("dateToEntry")
        self.dateFromEntry = self.builder.get_object("dateFromEntry")
        if share.config.datetypes[share.config.datetype] == "jalali":
            (year , month , day ) = ("1397","12","20")
        else:
            (year , month , day ) = ("2018" , "12", "20")
        datelist = ["", "", ""]
        datelist[share.config.datefields["year"]] = year
        datelist[share.config.datefields["month"]] = month
        datelist[share.config.datefields["day"]] = day
        delimiter = share.config.datedelims[share.config.datedelim]
        placeH = datelist[0]+delimiter+datelist[1]+delimiter+datelist[2]
        self.dateToEntry.set_placeholder_text(placeH)
        self.dateFromEntry.set_placeholder_text(placeH)
        self.builder.get_object("typeComboBox").set_active(2)

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
        query = query.filter(Products.code == utility.convertToLatin(productCode) )
        product  = query.first()
        self.treestore.clear()
        if product is not None:
            statusbar = self.builder.get_object('statusbar3')
            context_id = statusbar.get_context_id('statusbar')
            statusbar.remove_all(context_id)
            oversellTxt = _("Yes") if product.oversell else _("No")
            self.builder.get_object("nameTextView").get_buffer().set_text(product.name)
            self.builder.get_object("groupTextView").get_buffer().set_text(utility.readNumber(product.accGroup))
            self.builder.get_object("locationTextView").get_buffer().set_text(product.location)
            self.builder.get_object("quantityTextView").get_buffer().set_text(utility.LN(float(product.quantity)))
            self.builder.get_object("quantityWarningTextView").get_buffer().set_text(utility.LN(float(product.qntyWarning)))
            self.builder.get_object("oversellTextView").get_buffer().set_text(oversellTxt)
            self.builder.get_object("purchacePriceTextView").get_buffer().set_text(utility.LN(float(product.purchacePrice)))
            self.builder.get_object("dicountFormulaTextView").get_buffer().set_text(str(product.discountFormula))
            self.builder.get_object("sellingPriceTextView").get_buffer().set_text(utility.LN(float(product.sellingPrice)))
            self.builder.get_object("productDescriptionTextView").get_buffer().set_text(product.productDesc)

            totalSellQnt = totalBuyQnt = totalSellIncome = totalBuyPrice = 0
            #Fill factor treeview
            initQ = config.db.session.query(FactorItems).filter(FactorItems.factorId == 0).first()
            productCount = 0
            if initQ:
                totalPrice = float(initQ.untPrc) * float(initQ.qnty)
                self.rows.append(("-" ,_("Initial inventory") ,utility.LN( initQ.qnty),utility.LN(initQ.untPrc),utility.LN(totalPrice) ,utility.LN(initQ.qnty),  "-" , "-" ,"-") )
                totalBuyPrice += float(initQ.untPrc) * float(initQ.qnty)
                totalBuyQnt += float(initQ.qnty)
                productCount = initQ.qnty
            query = config.db.session.query(FactorItems,Factors,Customers)
            query = query.filter(product.id == FactorItems.productId, FactorItems.factorId == Factors.Id, Customers.custId == Factors.Cust)
            # if factorType>= 0 and factorType != 2:
            #     query = query.filter(Factors.Sell == factorType)

            # if customerCode:
            #     query = query.filter(Customers.custCode == utility.convertToLatin(customerCode) )

            # if dateTo:
            #     dateTo = stringToDate(dateTo)

            # if dateFrom:
            #     dateFrom = stringToDate(dateFrom)

            # if dateTo:
            #     query = query.filter(Factors.tDate <= dateTo)
            # if dateFrom:
            #     query = query.filter(Factors.tDate >= dateFrom)

            result = query.all()
            if result == None or  not len(result):
                return

            for factor in result:
                quantity = utility.LN(factor.FactorItems.qnty)
                unitPrice = utility.LN(factor.FactorItems.untPrc)
                totalPrice = utility.LN(factor.FactorItems.untPrc * factor.FactorItems.qnty)
                if factor.Factors.Sell == True:
                    ftype = _("Sell")
                    productCount -= float(factor.FactorItems.qnty)
                    totalSellIncome += float(factor.FactorItems.qnty) * float(factor. FactorItems.untPrc)    # kole foroosh = sum(tedad * gheymat)
                    totalSellQnt += float(factor.FactorItems.qnty)                            # kole tedade forush = sum (tedad)
                else:
                    ftype = _("Buy")
                    productCount += float(factor.FactorItems.qnty)
                    totalBuyPrice += float(factor.FactorItems.qnty) * float(factor. FactorItems.untPrc)   # kole kharid = sum(tedad * gheymat)
                    totalBuyQnt += float(factor.FactorItems.qnty)

                date = dateToString(factor.Factors.tDate)
                self.rows.append((date,ftype,quantity,unitPrice, totalPrice ,utility.LN(productCount), utility.readNumber(factor.Factors.Code), unicode(factor.Customers.custName), unicode(factor.Customers.custCode)))

            for row in self.rows:
                self.treestore.append(None,  row)
            profit = totalSellIncome - ((totalBuyPrice/totalBuyQnt) *totalSellQnt )
            profit = "{0:.3f}".format(profit)           # rounding floating point number
            profitTxt = self.builder.get_object("profitTextview")
            profitTxt.get_buffer().set_text(utility.LN(profit))
            profitTxt.set_direction(Gtk.TextDirection.LTR)
        else:
            statusbar = self.builder.get_object('statusbar3')
            context_id = statusbar.get_context_id('statusbar')
            statusbar.push(context_id,_('Not Found'))
        self.window.show_all()

    def searchProduct(self,sender):
        # Get data from DB
        box = self.builder.get_object("productCodeSearchEntry")
        productCode = box.get_text()
        self.showResult(productCode,2,0,0,0)


    def factorFilter(self,sender):
        self.treestore.clear()
        combo = self.builder.get_object("typeComboBox")
        index = combo.get_active()
        productCode = self.builder.get_object("productCodeSearchEntry").get_text()

        customerCode =utility.readNumber(self.builder.get_object("customerCodeEntry").get_text())

        dateTo = self.dateToEntry.get_text()
        dateFrom = self.dateFromEntry.get_text()

        fTypes = [_("Buy") , _("Sell")]
        flag = True
        for row in self.rows:
            if customerCode and  row[8] != customerCode:
                flag = False
            if dateTo and row[0] > dateTo:
                flag = False
            if dateFrom and row[0] < dateFrom:
                flag = False

            if index!=2 and  row[1] != fTypes[index]:
                flag = False
            if flag:
                self.treestore.append(None , row)
            flag = True
