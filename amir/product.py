import  sys
import  os
import  gobject

import  re

from . import numberentry
from . import decimalentry
from . import dateentry
from . import subjects
from . import productgroup
from . import utility
from . import dbconfig

from    sqlalchemy.orm              import  sessionmaker, join
from    sqlalchemy.orm.util         import  outerjoin
from    sqlalchemy.sql              import  and_, or_
from    sqlalchemy.sql.functions    import  *

from    .helpers                    import  get_builder
from    .share                      import  share
from    datetime                    import  date
from    .database                   import  *
import gi
from gi.repository import Gtk
from gi.repository import GObject

if sys.version_info > (3,):
    unicode = str

config = share.config

gi.require_version('Gtk', '3.0')

class Product(productgroup.ProductGroup):

    def __init__(self):
        productgroup.ProductGroup.__init__(self)

        self.qntyEntry = decimalentry.DecimalEntry()
        self.builder.get_object("qntyBox").add(self.qntyEntry)
        self.qntyEntry.show()
        
        self.qntyWrnEntry = decimalentry.DecimalEntry()
        self.builder.get_object("qntyWrnBox").add(self.qntyWrnEntry)
        self.qntyWrnEntry.show()

        self.purchPriceEntry = decimalentry.DecimalEntry()
        self.builder.get_object("purchPriceBox").add(self.purchPriceEntry)
        self.purchPriceEntry.show()
        
        self.sellPriceEntry = decimalentry.DecimalEntry()
        self.builder.get_object("sellPriceBox").add(self.sellPriceEntry)
        self.sellPriceEntry.show()

        self.treeview = self.builder.get_object("productsTreeView")
        self.treestore = Gtk.TreeStore(str, str, str, str, str, str , int)

    def viewProducts(self):
        self.window = self.builder.get_object("viewProductsWindow")
#              #        moved to __init__ function
#        self.treeview = self.builder.get_object("productsTreeView")
#        self.treestore = Gtk.TreeStore(str, str, str, str, str)  
        self.treestore.clear()
        self.treeview.set_model(self.treestore)

        column      = Gtk.TreeViewColumn(_("Code"), 
                                            Gtk.CellRendererText(),
                                            text = 0)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(0)
        column.set_sort_indicator(True)
        self.treeview.append_column(column)
        
        column      = Gtk.TreeViewColumn(_("Name"), 
                                            Gtk.CellRendererText(),
                                            text = 1)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        column.set_sort_indicator(True)
        self.treeview.append_column(column)
        
        column      = Gtk.TreeViewColumn(_("Quantity"), 
                                            Gtk.CellRendererText(),
                                            text = 2)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(2)
        column.set_sort_indicator(True)
        self.treeview.append_column(column)
        
        column      = Gtk.TreeViewColumn(_("Purchase Price"), 
                                            Gtk.CellRendererText(),
                                            text = 3)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)

        column      = Gtk.TreeViewColumn(_("Selling Price"), 
                                            Gtk.CellRendererText(),
                                            text = 4)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)

        column      = Gtk.TreeViewColumn(_("Unit measurement"), 
                                            Gtk.CellRendererText(),
                                            text = 5)
        #column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)

        
        self.treeview.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        self.treestore.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        
        #Fill groups treeview
        self.fillTreeview()

        self.window.show_all()
        if utility.checkPermission(32):
            self.builder.get_object("addProductBtn").hide()
            self.builder.get_object("addGroupBtn").hide()
        if utility.checkPermission(128):
            self.builder.get_object("editBtn").hide()
        if utility.checkPermission(256):
            self.builder.get_object("deleteBtn").hide()

    ##Fill groups treeview
    def fillTreeview(self):
        self.treestore.clear();
        query = config.db.session.query(ProductGroups, Products)
        query = query.select_from(outerjoin(ProductGroups, Products, ProductGroups.id == Products.accGroup))
        query = query.order_by(ProductGroups.id.asc())
        result = query.all()
        
        last_gid = 0
        grouprow = None
        for g, p in result:

            if g.id != last_gid:                
                grouprow = self.treestore.append(None, (utility.readNumber(g.code),utility.readNumber(g.name), "", "", "" , "",0))
                last_gid = g.id
                
            if p != None:
                self.treestore.append(grouprow,(utility.readNumber(p.code),utility.readNumber(p.name), utility.LN(p.quantity), 
                                        utility.LN(p.purchacePrice), utility.LN(p.sellingPrice) ,p.uMeasurement,p.id) )


    def addProduct(self, sender, pcode = ""):
        #self.treestore = Gtk.TreeStore(str, str, str, str, str)                
        
        accgrp = "0"
        try:
            selection = self.treeview.get_selection()
        except AttributeError:
            #Skip if there is no table to have selected row.
            pass
        else:
            iter = selection.get_selected()[1]
            if iter != None and self.treestore.iter_parent(iter) == None:
                accgrp = self.treestore.get_value(iter, 0)
        accgrp =utility.convertToLatin(accgrp)
        dialog = self.builder.get_object("addProductDlg")
        dialog.set_title(_("Add New Product"))
        
        self.builder.get_object("qnttyLbl").set_text(_("Initial inventory:") )
        lastProCode = config.db.session.query(Products.code).filter(Products.accGroup==accgrp).order_by(Products.code.desc()).first()
        if lastProCode:
            lastProCode = lastProCode.code    
        lastProCode = unicode(int(lastProCode)+1 ) if lastProCode else ""
        self.builder.get_object("proCodeEntry").set_text(lastProCode)
        self.builder.get_object("accGrpEntry" ).set_text(accgrp)
        self.builder.get_object("proNameEntry").set_text("")
        self.builder.get_object("proLocEntry" ).set_text("")
        self.builder.get_object("proDescEntry").set_text("")
        self.builder.get_object("discFormulaEntry").set_text("")
        self.qntyEntry.set_text("")
        self.qntyWrnEntry.set_text("")
        self.purchPriceEntry.set_text("")
        self.sellPriceEntry.set_text("")
        self.builder.get_object("oversell").set_active(False)
        self.builder.get_object("uMeasureEntry").set_text("")
        
        success = False
        while not success :
            result = dialog.run()
            if result == 1:                
                code     = unicode(self.builder.get_object("proCodeEntry").get_text())
                accgrp   = unicode(self.builder.get_object("accGrpEntry" ).get_text())
                name     = unicode(self.builder.get_object("proNameEntry").get_text())
                location = unicode(self.builder.get_object("proLocEntry" ).get_text())
                desc     = unicode(self.builder.get_object("proDescEntry").get_text())
                formula  = unicode(self.builder.get_object("discFormulaEntry").get_text())
                quantity = self.qntyEntry.get_float()
                q_warn   = self.qntyWrnEntry.get_float()
                p_price  = self.purchPriceEntry.get_float()
                s_price  = self.sellPriceEntry.get_float()
                oversell = self.builder.get_object("oversell").get_active()
                measurement = unicode(self.builder.get_object("uMeasureEntry").get_text())
                success = self.saveProduct(code, accgrp, name, location, desc, quantity, q_warn, p_price, s_price, oversell, formula, measurement)
            else:
                break
    
        dialog.hide()

    def editProductsAndGrps(self, sender):
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]        
        if iter != None:
            if self.treestore.iter_parent(iter) == None:
            #iter points to a product group
                self.editProductGroup(sender)
            else:
            #iter points to a product
                dialog = self.builder.get_object("addProductDlg")
                dialog.set_title(_("Edit Product"))
                
                self.builder.get_object("qnttyLbl").set_text(_("Quantity:")  ) 
                code = self.treestore.get_value(iter, 0)
                id = self.treestore.get_value(iter, 6)                
                query = config.db.session.query(Products, ProductGroups.code)
                query = query.select_from(outerjoin(ProductGroups, Products, ProductGroups.id == Products.accGroup))
                result = query.filter(Products.id== id).first()
                product = result[0]
                groupcode = result[1]                
                
                quantity = str(product.quantity)
                quantity_warn = str(product.qntyWarning)
                p_price = str(product.purchacePrice)
                s_price = str(product.sellingPrice)
                if config.digittype == 1:
                    quantity = utility.convertToPersian(quantity)
                    quantity_warn = utility.convertToPersian(quantity_warn)
                    p_price = utility.convertToPersian(p_price)
                    s_price = utility.convertToPersian(s_price)
                
                self.builder.get_object("proCodeEntry").set_text(product.code)
                self.builder.get_object("accGrpEntry" ).set_text(groupcode)
                self.builder.get_object("proNameEntry").set_text(product.name)
                self.builder.get_object("proLocEntry" ).set_text(product.location)
                self.builder.get_object("proDescEntry").set_text(product.productDesc)
                self.builder.get_object("discFormulaEntry").set_text(product.discountFormula)
                self.qntyEntry.set_sensitive(False)
                self.qntyEntry.set_text(quantity)
                self.qntyWrnEntry.set_text(quantity_warn)
                self.purchPriceEntry.set_text(p_price)
                self.sellPriceEntry.set_text(s_price)
                self.builder.get_object("oversell").set_active(product.oversell)
                self.builder.get_object("uMeasureEntry").set_text(product.uMeasurement)
                
                success = False
                while not success :
                    result = dialog.run()
                    if result == 1:
                        code     = unicode(self.builder.get_object("proCodeEntry").get_text())
                        accgrp   = unicode(self.builder.get_object("accGrpEntry" ).get_text())
                        name     = unicode(self.builder.get_object("proNameEntry").get_text())
                        location = unicode(self.builder.get_object("proLocEntry" ).get_text())
                        desc     = unicode(self.builder.get_object("proDescEntry").get_text())
                        formula  = unicode(self.builder.get_object("discFormulaEntry").get_text())
                        quantity = self.qntyEntry.get_float()
                        q_warn   = self.qntyWrnEntry.get_float()
                        p_price  = self.purchPriceEntry.get_float()
                        s_price  = self.sellPriceEntry.get_float()
                        oversell = self.builder.get_object("oversell").get_active()
                        measurement = unicode(self.builder.get_object("uMeasureEntry").get_text())
                    
                        success = self.saveProduct(code, accgrp, name, location, desc, quantity, q_warn, p_price, s_price, oversell, formula , measurement,id, iter)
                    else:
                        break
                
                dialog.hide()
            
    def saveProduct(self, code, accgrp, name, location, desc, quantity, quantity_warn, 
            purchase_price, sell_price, oversell, formula,uMeasurement="",editId=0, edititer=None):
        msg = ""
        if code == "":
            msg += _("Product code should not be empty.\n")
        if accgrp == "":
            msg += _("Product group should not be empty.\n")
        if name == "":
            msg += _("Product name should not be empty.\n")
    
        if msg != "":
            msgbox =  Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.CLOSE, msg)
            msgbox.set_title(_("Empty fields"))
            msgbox.run()
            msgbox.destroy()
            return False
        result = 0                     
        #Checks if the product code is repeated.
        query = config.db.session.query(count(Products.id))
        query = query.filter(Products.code == code).filter(Products.accGroup == accgrp)
        if edititer !=None:
            query = query.filter(Products.id != editId)                
        result = query.first()[0]        
        if result != 0:
            msg += _("A product with this code already exists.\n")
            
        query = config.db.session.query(ProductGroups).select_from(ProductGroups)
        group = query.filter(ProductGroups.code == accgrp).first()
        if group == None:
            msg += _("Group code is not valid.\n")
        
        if not quantity :
            quantity = 0                     
        else:
            if not purchase_price or  purchase_price =="":
                msg+= _("Product with initial balance must have purchase price. \n ")

        firstnum = 0
        secnum = 0
        try:
            flist = formula.split(u',')
            for elm in flist:
                if elm != '':
                    partlist = elm.split(u':')
                    price = float(partlist[1])                    
                    numlist = partlist[0].split(u'-')
                    if len(numlist) > 0:
                        firstnum = float(numlist[0])
                        if firstnum < secnum:
                            msg += _("Discount formula is not valid")
                            break                        
                        if len(numlist) > 1:
                            secnum = float(numlist[1])                            
                            if firstnum > secnum:
                                msg += _("Discount formula should be typed in ascending order.")
                                break
                            if len(numlist) > 2:
                                msg += _("Discount formula is not valid")
                                break
                    else:
                        msg += _("Discount formula is not valid")
                        break
        except ValueError:
            msg += _("Discount formula is not valid")
            
        if msg != "":
            msgbox =  Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.CLOSE, msg)
            msgbox.set_title(_("Invalid product properties"))
            msgbox.run()
            msgbox.destroy()
            return False    

        if edititer == None:
            product = Products(code, name, quantity_warn, oversell, location, quantity,
                    purchase_price, sell_price, group.id, desc, formula, uMeasurement)    
            config.db.session.add(product)
            config.db.session.commit()

            if quantity >0:
                if config.db.session.query(Bill).filter(Bill.id == 1).first():
                    prevFund = 0
                    query = config.db.session.query(Notebook).filter(Notebook.bill_id == 1)
                    pNote = query.first()
                    if pNote:
                        prevFund = pNote.value 
                    query.delete()
                    val = float(quantity) * float(purchase_price) + abs(prevFund)
                    dbconf = dbconfig.dbConfig()                    
                    config.db.session.add(Notebook(dbconf.get_int('inventories') , 1 , -val , _("Initial balance"))     )
                    config.db.session.add(Notebook(dbconf.get_int('fund') , 1 , val , _("Initial funding (share capital)"))     )
                    config.db.session.add(FactorItems(1,product.id , quantity, purchase_price, 0,0,_("Initial inventory")))

        else:
            product = config.db.session.query(Products).filter(Products.id == editId).first()
            product.code            = code
            product.name            = name
            product.oversell        = oversell
            product.location        = location
            product.quantity        = quantity
            product.accGroup        = group.id
            product.productDesc     = desc
            product.qntyWarning     = quantity_warn
            product.sellingPrice    = sell_price
            product.purchacePrice   = purchase_price
            product.discountFormula = formula
            product.uMeasurement    = uMeasurement
                    
        config.db.session.commit()
        
        #Show new product in table

        self.fillTreeview()
        try:
            parent_iter = self.treestore.get_iter_first()
        except AttributeError:
            #skip if there is no table to show
            pass
        else:
            if not parent_iter:
                return True            
            while self.treestore.iter_is_valid(parent_iter):
                itercode = self.treestore.get_value(parent_iter, 0)
                if itercode == accgrp:
                    break
                parent_iter = self.treestore.iter_next(parent_iter)
                open_iter = parent_iter
                
            if edititer == None:
                i = 0
                child = 1
                while child:
                    child = self.treestore.iter_nth_child(parent_iter, i)
                    i += 1
                    if code == self.treestore.get_value(child, 0):
                        open_iter = child
                        break

                path = self.treestore.get_path(open_iter)
                self.treeview.expand_to_path(path)
                self.treeview.scroll_to_cell(path, None, False, 0, 0)
                self.treeview.set_cursor(path, None, False)
                self.treeview.grab_focus()
            
            # self.saveRow(edititer, (code, name, utility.LN(quantity), 
                                    # utility.LN(purchase_price), utility.LN(sell_price) ) )
                
        return True

        
    def deleteProductsAndGrps(self, sender):
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        
        if iter != None:
            msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL, _("Are you sure to remove this row?"))
            msgbox.set_title(_("Are you sure?"))
            result = msgbox.run();
            msgbox.destroy() 
            if result != Gtk.ResponseType.OK : 
                return             
            if self.treestore.iter_parent(iter) == None:
            #Iter points to a product group
                self.deleteProductGroup(sender)
            else:
                #Iter points to a product
                id = unicode(self.treestore.get_value(iter, 6))
                query = config.db.session.query(Products)
                product = query.filter(Products.id == id).first()
                
                #TODO check if this product is used somewhere else
                
                config.db.session.delete(product)
                config.db.session.commit()
                self.treestore.remove(iter)
                
    
    #@param treeiter: the TreeIter which data should be saved in
    #@param data: a tuple containing data to be saved
    def saveRow(self, treeiter, data):
        if len(data) == 4:
            #A product group should be saved, just set code and name.
            self.treestore.set(treeiter, 0, data[0], 1, data[1])
        elif len(data) == 5:
            #A product should be saved, set all given data.
            self.treestore.set(treeiter, 0, data[0], 1, data[1], 2, data[2], 3, data[3], 4, data[4])

    def highlightProduct(self, code , group):
        iter = self.treestore.get_iter_first()
        if code != "":
            code = code.decode('utf-8')
            
            query = config.db.session.query(ProductGroups)
            query = query.select_from(outerjoin(ProductGroups, Products, ProductGroups.id == Products.accGroup))
            group = query.filter(Products.code == code).filter(Products.accGroup== group).first()
            
            if group:
                tcode = group.code
                #First check parents to find related group
                pre = iter
                while iter:
                    itercode = self.treestore.get_value(iter, 0).decode('utf-8')
                    if  itercode < tcode:
                        pre = iter
                        iter = self.treestore.iter_next(iter)
                    elif itercode == tcode:
                        pre = iter
                        tcode = code
                        #Now check children(products) to find product row
                        iter = self.treestore.iter_children(iter)
                    else:
                        #iter = pre
                        break
                        
                iter = pre
                        
        path = self.treestore.get_path(iter)
        self.treeview.expand_to_path(path)
        self.treeview.scroll_to_cell(path, None, False, 0, 0)
        self.treeview.set_cursor(path, None, False)
        self.treeview.grab_focus()
        
    #Called when a row of product table get activated by mouse double-click or Enter key
    def selectProductFromList(self, treeview, path, view_column):
        iter = self.treestore.get_iter(path)
        if self.treestore.iter_parent(iter) != None:
            code = utility.convertToLatin(self.treestore.get_value(iter, 0))
            parent_iter = self.treestore.iter_parent(iter)
            group = utility.convertToLatin(self.treestore.get_value(parent_iter , 0) )
            query = config.db.session.query(Products).select_from(Products)
            query = query.filter(Products.code == code).filter(Products.accGroup== group)
            product_id = query.first().id            
            self.emit("product-selected", product_id, code)
        
    def selectProductGroup(self, sender):
        obj = productgroup.ProductGroup()
        obj.connect("group-selected", self.groupSelected)
        obj.viewProductGroups()
        
        code = self.builder.get_object("accGrpEntry").get_text()
        obj.highlightGroup(unicode(code))

    def groupSelected(self, sender, id, code):
        self.builder.get_object("accGrpEntry").set_text(code)
        
        lastProCode = config.db.session.query(Products.code).filter(Products.accGroup==code).order_by(Products.code.desc()).first()
        if lastProCode:
            lastProCode = lastProCode.code    
        lastProCode = unicode(int(lastProCode)+1 ) if lastProCode else ""        
        self.builder.get_object("proCodeEntry").set_text(lastProCode)
        sender.window.destroy()
        

GObject.type_register(Product)
GObject.signal_new("product-selected", Product, GObject.SignalFlags.RUN_LAST,
                   None, (GObject.TYPE_INT, GObject.TYPE_STRING))
