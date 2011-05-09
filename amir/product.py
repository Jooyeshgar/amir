import  sys
import  os
import  gobject
import  pygtk
import  gtk

import  numberentry
import  dateentry
import  subjects
import  productgroup
import  utility

from    sqlalchemy.orm              import  sessionmaker, join
from    sqlalchemy.orm.util         import  outerjoin
from    sqlalchemy.sql              import  and_, or_
from    sqlalchemy.sql.functions    import  *

from    helpers                     import  get_builder
from    amirconfig                  import  config
from    datetime                    import  date
from    database                    import  *

pygtk.require('2.0')

class Product(productgroup.ProductGroup):

    def __init__(self):
        productgroup.ProductGroup.__init__(self)
    
        self.qntyEntry = numberentry.NumberEntry()
        self.builder.get_object("qntyBox").add(self.qntyEntry)
        self.qntyEntry.show()
        
        self.qntyWrnEntry = numberentry.NumberEntry(10)
        self.builder.get_object("qntyWrnBox").add(self.qntyWrnEntry)
        self.qntyWrnEntry.show()

        self.purchPriceEntry = numberentry.NumberEntry(10)
        self.builder.get_object("purchPriceBox").add(self.purchPriceEntry)
        self.purchPriceEntry.show()
        
        self.sellPriceEntry = numberentry.NumberEntry(10)
        self.builder.get_object("sellPriceBox").add(self.sellPriceEntry)
        self.sellPriceEntry.show()
        

    def viewProducts(self):
        self.window = self.builder.get_object("viewProductsWindow")
        
        self.treeview = self.builder.get_object("productsTreeView")
        self.treestore = gtk.TreeStore(str, str, str, str, str)
        self.treestore.clear()
        self.treeview.set_model(self.treestore)

        column      = gtk.TreeViewColumn(_("Code"), 
                                            gtk.CellRendererText(),
                                            text = 0)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(0)
        column.set_sort_indicator(True)
        self.treeview.append_column(column)
        
        column      = gtk.TreeViewColumn(_("Name"), 
                                            gtk.CellRendererText(),
                                            text = 1)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        column.set_sort_indicator(True)
        self.treeview.append_column(column)
        
        column      = gtk.TreeViewColumn(_("Quantity"), 
                                            gtk.CellRendererText(),
                                            text = 2)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(2)
        column.set_sort_indicator(True)
        self.treeview.append_column(column)
        
        column      = gtk.TreeViewColumn(_("Purchase Price"), 
                                            gtk.CellRendererText(),
                                            text = 3)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)

        column      = gtk.TreeViewColumn(_("Selling Price"), 
                                            gtk.CellRendererText(),
                                            text = 4)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)

        
        self.treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        self.treestore.set_sort_column_id(0, gtk.SORT_ASCENDING)
        
        #Fill groups treeview
        query = config.db.session.query(ProductGroups, Products)
        query = query.select_from(outerjoin(ProductGroups, Products, ProductGroups.id == Products.accGroup))
        query = query.order_by(ProductGroups.id.asc())
        result = query.all()
        
        last_gid = 0
        grouprow = None
        for g, p in result:
            if g.id != last_gid:
		grouprow = self.treestore.append(None, (g.code, g.name, "", "", ""))
                last_gid = g.id
                
            if p != None:
                self.treestore.append(grouprow, (p.code, p.name, utility.showNumber(p.quantity), 
                                      utility.showNumber(p.purchacePrice), utility.showNumber(p.sellingPrice)))
        
        self.window.show_all()    


    def addProduct(self, sender, pcode = ""):
        dialog = self.builder.get_object("addProductDlg")
        dialog.set_title(_("Add New Product"))
        
        self.builder.get_object("proCodeEntry").set_text("")
        self.builder.get_object("accGrpEntry" ).set_text("")
        self.builder.get_object("proNameEntry").set_text("")
        self.builder.get_object("proLocEntry" ).set_text("")
        self.builder.get_object("proDescEntry").set_text("")        
        self.qntyEntry.set_text("")
        self.qntyWrnEntry.set_text("")
        self.purchPriceEntry.set_text("")
        self.sellPriceEntry.set_text("")
        self.builder.get_object("oversell").set_active(False)
        
        success = False
        while not success :
	    result = dialog.run()
	    if result == 1:
		code     = unicode(self.builder.get_object("proCodeEntry").get_text())
		accgrp   = unicode(self.builder.get_object("accGrpEntry" ).get_text())
		name     = unicode(self.builder.get_object("proNameEntry").get_text())
		location = unicode(self.builder.get_object("proLocEntry" ).get_text())
		desc     = unicode(self.builder.get_object("proDescEntry").get_text())
		quantity = self.qntyEntry.get_int()
		q_warn   = self.qntyWrnEntry.get_int()
		p_price  = self.purchPriceEntry.get_int()
		s_price  = self.sellPriceEntry.get_int()
		oversell = self.builder.get_object("oversell").get_active()
		
		success = self.saveProduct(code, accgrp, name, location, desc, quantity, q_warn, p_price, s_price, oversell)
	    else:
		break
		
	dialog.hide()

    def editProductsAndGrps(self, sender):
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        
        if self.treestore.iter_parent(iter) == None:
            #iter points to a product group
            self.editProductGroup(sender)
        else:
	    #iter points to a product
	    dialog = self.builder.get_object("addProductDlg")
	    dialog.set_title(_("Edit Product"))
	    
            code = self.treestore.get_value(iter, 0)
            query = config.db.session.query(Products, ProductGroups.code)
            query = query.select_from(outerjoin(ProductGroups, Products, ProductGroups.id == Products.accGroup))
            result = query.filter(Products.code == code).first()
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
	    self.qntyEntry.set_text(quantity)
	    self.qntyWrnEntry.set_text(quantity_warn)
	    self.purchPriceEntry.set_text(p_price)
	    self.sellPriceEntry.set_text(s_price)
	    self.builder.get_object("oversell").set_active(product.oversell)
            
            success = False
	    while not success :
		result = dialog.run()
		if result == 1:
		    code     = unicode(self.builder.get_object("proCodeEntry").get_text())
		    accgrp   = unicode(self.builder.get_object("accGrpEntry" ).get_text())
		    name     = unicode(self.builder.get_object("proNameEntry").get_text())
		    location = unicode(self.builder.get_object("proLocEntry" ).get_text())
		    desc     = unicode(self.builder.get_object("proDescEntry").get_text())
		    quantity = self.qntyEntry.get_int()
		    q_warn   = self.qntyWrnEntry.get_int()
		    p_price  = self.purchPriceEntry.get_int()
		    s_price  = self.sellPriceEntry.get_int()
		    oversell = self.builder.get_object("oversell").get_active()
		    
		    success = self.saveProduct(code, accgrp, name, location, desc, quantity, q_warn, p_price, s_price, oversell, iter)
		else:
		    break
		    
	    dialog.hide()
            
    def saveProduct(self, code, accgrp, name, location, desc, quantity, quantity_warn, 
		    purchase_price, sell_price, oversell, edititer=None):
        
        msg = ""
        if code == "":
            msg += _("Product code should not be empty.\n")
        if accgrp == "":
            msg += _("Product group should not be empty\n")
        if name == "":
            msg += _("Product name should not be empty\n")
	
	if msg != "":
            msgbox =  gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE, msg)
            msgbox.set_title(_("Empty fields"))
            msgbox.run()
            msgbox.destroy()
            return False
            
        if edititer != None:
            pcode = unicode(self.treestore.get_value(edititer, 0))
            query = config.db.session.query(Products).select_from(Products)
            product = query.filter(Products.code == pcode).first()
            pid = product.id
            
        #Checks if the product code is repeated.
        query = config.db.session.query(count(Products.id)).select_from(Products)
        query = query.filter(Products.code == code)
        if edititer != None:
            query = query.filter(Products.id != pid)
        result = query.first()[0]
        msg = ""
        if result != 0:
	    msg += _("A product with this code already exists.\n")
            
        query = config.db.session.query(ProductGroups).select_from(ProductGroups)
        group = query.filter(ProductGroups.code == accgrp).first()
        if group == None:
	    msg += _("Group code is not valid.\n")
	    
	if msg != "":
            msgbox =  gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE, msg)
            msgbox.set_title(_("Invalid product properties"))
            msgbox.run()
            msgbox.destroy()
            return False
            
        if edititer == None:
            product = Products(code, name, quantity_warn, oversell, location, quantity,
			       purchase_price, sell_price, group.id, desc, u'')
	else:
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
	    product.discountFormula = u''
            
        config.db.session.add(product)
        config.db.session.commit()
        
        #Show new product in table
        if self.treestore != None:
            parent_iter = self.treestore.get_iter_first()
            while self.treestore.iter_is_valid(parent_iter):
                itercode = self.treestore.get_value(parent_iter, 0)
                if itercode == accgrp:
                    break
                parent_iter = self.treestore.iter_next(parent_iter)
                
            if edititer == None:
                edititer = self.treestore.append(parent_iter)
                path = self.treestore.get_path(edititer)
                self.treeview.expand_to_path(path)
		self.treeview.scroll_to_cell(path, None, False, 0, 0)
		self.treeview.set_cursor(path, None, False)
		self.treeview.grab_focus()
            
            self.saveRow(edititer, (code, name, utility.showNumber(quantity), 
                                 utility.showNumber(purchase_price), utility.showNumber(sell_price) ) )
                
        return True

        
    def deleteProductsAndGrps(self, sender):
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        
        if self.treestore.iter_parent(iter) == None:
            #Iter points to a product group
            self.deleteProductGroup(sender)
        else:
            #Iter points to a product
            code = self.treestore.get_value(iter, 0)
            query = config.db.session.query(Products).select_from(Products)
            product = query.filter(Products.code == code).first()
            
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

        
    def selectProductGroup(self, sender):
        obj = productgroup.ProductGroup()
        obj.connect("group-selected", self.groupSelected)
        obj.viewProductGroups()
        
        code = self.builder.get_object("accGrpEntry").get_text()
        obj.highlightGroup(unicode(code))
    
    def groupSelected(self, sender, id, code):
        self.builder.get_object("accGrpEntry").set_text(code)
        sender.window.destroy()
        
             
##----------------------------------------------------------------------
## Creating New Signal to return the selected group when double clicked!
##----------------------------------------------------------------------
##gobject.type_register(                          Customer                )
##
##gobject.signal_new( "customer-selected",        Customer, 
##                    gobject.SIGNAL_RUN_LAST,    gobject.TYPE_NONE, 
##                    (gobject.TYPE_INT,          gobject.TYPE_STRING)    )
