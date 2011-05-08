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
                self.treestore.append(grouprow, (p.code, p.name, str(p.quantity), str(p.purchacePrice), str(p.sellingPrice)))
        
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
        
    #def customerFormCanceled(self,sender=0,ev=0):
        #self.customerForm.hide()
        #return True
        
    #def customerFormOkPressed(self,sender=0,ev=0):
        #result = self.saveCustomer()
        #if result == 0:
            #self.customerForm.hide()
            
    #def on_markedChk_toggled(self,sender=0,ev=0):
        #self.builder.get_object("markedReasonEntry").set_sensitive(self.builder.get_object("markedChk").get_active())
##
##    def submitEditCust(self):
##        print "SUBMIT  EDIT"
##    
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
            
        #Checks if the product code is repeated.
        query = config.db.session.query(count(Products.id)).select_from(Products)
        query = query.filter(Products.code == code)
        #if edititer != None:
            #query = query.filter(Products.id != gid)
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
            
            self.saveRow(edititer, (code, name, quantity, purchase_price, sell_price) )
                
        return True

    def editProductsAndGrps(self, sender):
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        
        if self.treestore.iter_parent(iter) == None:
            #Iter points to a product group
            self.editProductGroup(sender)
        #else:            
            #code = self.treestore.get_value(iter, 0)
            #code = utility.convertToLatin(code)
            #query = config.db.session.query(Customers, CustGroups.custGrpCode)
            #query = query.select_from(outerjoin(CustGroups, Customers, CustGroups.custGrpId == Customers.custGroup))
            #result = query.filter(Customers.custCode == code).first()
            #customer = result[0]
            #groupcode = result[1]
            
            #custCode = utility.showNumber(customer.custCode, False)
            #custGrp = utility.showNumber(groupcode, False)
            #custPhone = utility.showNumber(customer.custPhone, False)
            #custCell = utility.showNumber(customer.custCell, False)
            #custFax = utility.showNumber(customer.custFax, False)
            #custPersonalCode = utility.showNumber(customer.custPersonalCode, False)
            #custPostalCode = utility.showNumber(customer.custPostalCode, False)
            
            #self.customerForm = self.builder.get_object("customersWindow")
            #self.customerForm.set_title(_("Edit Customer"))
            #self.builder.get_object("addCustSubmitBtn").set_label(_("Save Customer"))
            
            #self.builder.get_object("custCodeEntry").set_text(custCode)
            #self.builder.get_object("custNameEntry").set_text(customer.custName)
            #self.builder.get_object("custGrpEntry").set_text(groupcode)
            
            #self.builder.get_object("custEcnmcsCodeEntry").set_text(customer.custEcnmcsCode)
            #self.builder.get_object("custPhoneEntry").set_text(custPhone)
            #self.builder.get_object("custCellEntry").set_text(custCell)
            #self.builder.get_object("custFaxEntry").set_text(custFax)
            #self.builder.get_object("custWebPageEntry").set_text(customer.custWebPage)
            #self.builder.get_object("custEmailEntry").set_text(customer.custEmail)
            #self.builder.get_object("custRepViaEmailChk").set_active(customer.custRepViaEmail)
            #self.builder.get_object("custAddressEntry").set_text(customer.custAddress)
            #self.builder.get_object("callResponsibleEntry").set_text(customer.custResposible)
            #self.builder.get_object("custConnectorEntry").set_text(customer.custConnector)
            #self.builder.get_object("custDescEntry").set_text(customer.custDesc)
            #self.builder.get_object("custTypeBuyerChk").set_active(customer.custTypeBuyer)
            ##----------------------------------
            #self.builder.get_object("custTypeSellerChk").set_active(customer.custTypeSeller)
            #self.builder.get_object("custTypeMateChk").set_active(customer.custTypeMate)
            #self.builder.get_object("custTypeAgentChk").set_active(customer.custTypeAgent)
            #self.builder.get_object("custIntroducerEntry").set_text(customer.custIntroducer)
            #self.boxCommissionRateEntry.set_text(customer.custCommission)
            #self.boxDiscRateEntry.set_text(customer.custDiscRate)
            #self.builder.get_object("markedChk").set_active(customer.custMarked)
            #self.builder.get_object("markedReasonEntry").set_text(customer.custReason)
            ##----------------------------------
            #self.boxBalanceEntry.set_text(utility.showNumber(customer.custBalance, False))
            #self.boxCreditEntry.set_text(utility.showNumber(customer.custCredit, False))
            #self.builder.get_object("custAccName1Entry").set_text(customer.custAccName1)
            #self.builder.get_object("custAccNo1Entry").set_text(customer.custAccNo1)
            #self.builder.get_object("custAccBank1Entry").set_text(customer.custAccBank1)
            #self.builder.get_object("custAccName2Entry").set_text(customer.custAccName2)
            #self.builder.get_object("custAccNo2Entry").set_text(customer.custAccNo2)
            #self.builder.get_object("custAccBank2Entry").set_text(customer.custAccBank2)
            
            #self.personalcodebox.set_text(utility.showNumber(customer.custPersonalCode, False))
            #self.postalcodebox.set_text(utility.showNumber(customer.custPostalCode, False))
            #self.builder.get_object("markedReasonEntry").set_sensitive(self.builder.get_object("markedChk").get_active())
            
            #self.customerForm.show_all()
            
            #self.editCustomer = True
            #self.customerId = customer.custId
            #self.editIter = iter
        
    def deleteProductsAndGrps(self, sender):
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        
        if self.treestore.iter_parent(iter) == None:
            #Iter points to a product group
            self.deleteProductGroup(sender)
        #else:
            ##Iter points to a customer
            #code = self.treestore.get_value(iter, 0)
            #query = config.db.session.query(Customers).select_from(Customers)
            #customer = query.filter(Customers.custCode == code).first()
            
            ##TODO check if this customer is used somewhere else
            
            #config.db.session.delete(customer)
            #config.db.session.commit()
            #self.treestore.remove(iter)
                
    
    #@param treeiter: the TreeIter which data should be saved in
    #@param data: a tuple containing data to be saved
    def saveRow(self, treeiter, data):
        if len(data) == 4:
            #A product group should be saved, just set code and name.
            self.treestore.set(treeiter, 0, data[0], 1, data[1])
        elif len(data) == 5:
            #A product should be saved, set all given data.
            self.treestore.set(treeiter, 0, data[0], 1, data[1], 2, data[2], 3, data[3], 4, data[4])

    #def on_addCustomerBtn_clicked(self, sender):
        #selection = self.treeview.get_selection()
        #iter = selection.get_selected()[1]
        #pcode = ""
        #if (iter != None and self.treestore.iter_parent(iter) == None):
                #pcode = self.treestore.get_value(iter, 0)
        #self.addNewCustomer(sender, pcode)
        
    #def selectGroup(self, sender):
        #obj = customergroup.Group()
        #obj.connect("group-selected", self.groupSelected)
        #obj.viewCustomerGroups()
        
        #code = self.builder.get_object("custGrpEntry").get_text()
        #obj.highlightGroup(code)
    
    #def groupSelected(self, sender, id, code):
        #self.builder.get_object("custGrpEntry").set_text(code)
        #sender.window.destroy()  
             
##----------------------------------------------------------------------
## Creating New Signal to return the selected group when double clicked!
##----------------------------------------------------------------------
##gobject.type_register(                          Customer                )
##
##gobject.signal_new( "customer-selected",        Customer, 
##                    gobject.SIGNAL_RUN_LAST,    gobject.TYPE_NONE, 
##                    (gobject.TYPE_INT,          gobject.TYPE_STRING)    )
