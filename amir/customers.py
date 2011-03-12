import  sys
import  os
import  gobject
import  pygtk
import  gtk

import  warehousing
import  numberentry
import  dateentry
import  subjects
import  customergroup
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

class Customer(customergroup.Group):

    def __init__(self):
        customergroup.Group.__init__(self)
        
        self.postalcodeEntry = numberentry.NumberEntry()
        self.postalcodeEntry.set_max_length(10)
        box = self.builder.get_object("postalcodebox")
        box.add(self.postalcodeEntry)
        self.postalcodeEntry.show()
        
        self.personalcodeEntry = numberentry.NumberEntry()
        self.personalcodeEntry.set_max_length(10)
        box = self.builder.get_object("personalcodebox")
        box.add(self.personalcodeEntry)
        self.personalcodeEntry.show()
#===============================================================================
#    def __init__(self,buyerFlg=True,sellerFlg=True,mateFlg=True,agentFlg=True):
#        
#        self.buyerFlg   = buyerFlg
#        self.sellerFlg  = sellerFlg
#        self.MateFlg    = mateFlg
#        self.AgentFlg   = agentFlg
#        self.builder    = get_builder("customers" )
#        self.session    = config.db.session
#        
#        self.grpCodeEntry = numberentry.NumberEntry()
#        box = self.builder.get_object("grpCodeBox")
#        box.add(self.grpCodeEntry)
#        self.grpCodeEntry.show()
#        
#        self.window = self.builder.get_object("viewCustomersWindow")
#        
#        self.treeview = self.builder.get_object("customersTreeView")
#        self.treestore = gtk.TreeStore(str,str,str,str)
#        self.treestore.clear()
#        self.treeview.set_model(self.treestore)
#        
#        headers = (_("Code"),_("Name"),_("Balance"),_("Credit"))
#        txt = 0
#        for header in headers:
#            column = gtk.TreeViewColumn(header, gtk.CellRendererText(), text = txt)
#            column.set_spacing(5)
#            column.set_resizable(True)
#            self.treeview.append_column(column)
#            txt += 1
#        self.treeview.get_selection().set_mode(  gtk.SELECTION_SINGLE    )
#        
# #        self.fillCustomersList()
#        
#        self.window.show_all()
#        self.builder.connect_signals(self)
#===============================================================================

    def viewCustomers(self):
        self.window = self.builder.get_object("viewCustomersWindow")
        
        self.treeview = self.builder.get_object("customersTreeView")
        self.treestore = gtk.TreeStore(str, str, str, str)
        self.treestore.clear()
        self.treeview.set_model(self.treestore)

        column = gtk.TreeViewColumn(_("Code"), gtk.CellRendererText(), text = 0)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(0)
        column.set_sort_indicator(True)
        self.treeview.append_column(column)
        
        column = gtk.TreeViewColumn(_("Name"), gtk.CellRendererText(), text = 1)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        column.set_sort_indicator(True)
        self.treeview.append_column(column)
        
        column = gtk.TreeViewColumn(_("Balance"), gtk.CellRendererText(), text = 2)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        
        column = gtk.TreeViewColumn(_("Credit"), gtk.CellRendererText(), text = 3)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        
        self.treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        #self.treestore.set_sort_func(0, self.sortGroupIds)
        self.treestore.set_sort_column_id(0, gtk.SORT_ASCENDING)
        
        #Fill groups treeview
        query = config.db.session.query(CustGroups, Customers)
        query = query.select_from(outerjoin(CustGroups, Customers, CustGroups.custGrpId == Customers.custGroup))
        query = query.order_by(CustGroups.custGrpId.asc())
        result = query.all()
        
        last_gid = 0
        grouprow = None
        for g, c in result:
            if g.custGrpId != last_gid:
                grouprow = self.treestore.append(None, (g.custGrpCode, g.custGrpName, "", ""))
                last_gid = g.custGrpId
            if c != None:
                self.treestore.append(grouprow, (c.custCode, c.custName, str(c.custBalance), str(c.custCredit)))
        
        self.window.show_all()    

#    ############################################################################
#    #  Add Customers Window
#    ############################################################################
    def addNewCustomer(self, sender, pcode = ""):
        self.editCustomer = False
        
        self.customerForm = self.builder.get_object("customersWindow")
        self.customerForm.set_title(_("Add New Customer"))
        self.builder.get_object("addCustSubmitBtn").set_label(_("Add Customer"))
        
        self.builder.get_object("custCodeEntry").set_text("")
        self.builder.get_object("custNameEntry").set_text("")
        self.builder.get_object("custGrpEntry").set_text(pcode)
        
        self.builder.get_object("custEcnmcsCodeEntry").set_text("")        
        self.builder.get_object("custPhoneEntry").set_text("")
        self.builder.get_object("custCellEntry").set_text("")
        self.builder.get_object("custFaxEntry").set_text("")
        self.builder.get_object("custWebPageEntry").set_text("")
        self.builder.get_object("custEmailEntry").set_text("")
        self.builder.get_object("custRepViaEmailChk").set_active(False)
        self.builder.get_object("custAddressEntry").set_text("")        
        self.builder.get_object("callResponsibleEntry").set_text("")
        self.builder.get_object("custConnectorEntry").set_text("")
        self.builder.get_object("custDescEntry").set_text("")
        self.personalcodeEntry.set_text("")
        self.postalcodeEntry.set_text("")
        
        self.customerForm.show_all()
        
    def customerFormCanceled(self,sender=0,ev=0):
        self.customerForm.hide()
        return True
        
    def customerFormOkPressed(self,sender=0,ev=0):
        result = self.saveCustomer()
        if result == 0:
            self.customerForm.hide()
            
    def on_markedChk_toggled(self,sender=0,ev=0):
        self.builder.get_object("markedReasonEntry").set_sensitive(self.builder.get_object("markedChk").get_active())
#
#    def submitEditCust(self):
#        print "SUBMIT  EDIT"
#    
    #@return: -1 on error, 0 for success
    def saveCustomer(self):
        msg = ""
        custCode = self.builder.get_object("custCodeEntry").get_text()
        custCode = utility.convertToLatin(custCode)
        if custCode == "":
            msg += _("Customer code should not be empty.\n")
        else:
            codeQuery = config.db.session.query( Customers ).select_from( Customers )
            codeQuery = codeQuery.filter( Customers.custCode == custCode )
            if self.editCustomer:
                codeQuery = codeQuery.filter( Customers.custId != self.customerId )
            
            codeQuery = codeQuery.first()
            if codeQuery:
                msg += _("Customer code has been used before.\n")
                
        #--------------------
        custGrp = self.builder.get_object("custGrpEntry").get_text()
        custGrp = utility.convertToLatin(custGrp)
        groupid = 0
        if custGrp == "":
            msg += _("Customer group should not be empty.\n")
        else:
            query = config.db.session.query( CustGroups.custGrpId ).select_from( CustGroups ).filter( CustGroups.custGrpCode == custGrp )
            groupid = query.first()
            if groupid == None:
                msg += _("No customer group registered with code %s.\n") % custGrp
            else:
                groupid = groupid[0]
        
        #--------------------
        custName = self.builder.get_object("custNameEntry").get_text()
        if custName == "":
            msg += _("Customer name should not be empty.\n")
        
        #--------------------
        if msg != "":
            msgbox = gtk.MessageDialog(self.customerForm, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, msg)
            msgbox.set_title(_("Can not save customer"))
            msgbox.run()
            msgbox.destroy()
            return -1
#        #----------------------------------
#        self.custTypeBuyerChk = self.builder.get_object("custTypeBuyerChk")
#        self.custTypeSellerChk = self.builder.get_object("custTypeSellerChk")
#        self.custTypeMateChk = self.builder.get_object("custTypeMateChk")
#        self.custTypeAgentChk = self.builder.get_object("custTypeAgentChk")
#        self.custIntroducerEntry = self.builder.get_object("custIntroducerEntry")
#        self.custCommissionRateEntry = self.builder.get_object("custCommissionRateEntry")
#        self.custDiscRateEntry = self.builder.get_object("custDiscRateEntry")
#        self.markedChk = self.builder.get_object("markedChk")
#        self.markedReasonEntry = self.builder.get_object("markedReasonEntry")
#        #----------------------------------
#        self.custBalanceEntry = self.builder.get_object("custBalanceEntry")
#        self.custCreditEntry = self.builder.get_object("custCreditEntry")
#        self.custAccName1Entry = self.builder.get_object("custAccName1Entry")
#        self.custAccNo1Entry = self.builder.get_object("custAccNo1Entry")
#        self.custAccBank1Entry = self.builder.get_object("custAccBank1Entry")
#        self.custAccName2Entry = self.builder.get_object("custAccName2Entry")
#        self.custAccNo2Entry = self.builder.get_object("custAccNo2Entry")
#        self.custAccBank2Entry = self.builder.get_object("custAccBank2Entry")

        custEcnmcsCode     = self.builder.get_object("custEcnmcsCodeEntry").get_text()
        custPersonalCode   = self.personalcodeEntry.get_text()
        custPhone          = self.builder.get_object("custPhoneEntry").get_text()
        custCell           = self.builder.get_object("custCellEntry").get_text()
        custFax            = self.builder.get_object("custFaxEntry").get_text()
        custWebPage        = self.builder.get_object("custWebPageEntry").get_text()
        custEmail          = self.builder.get_object("custEmailEntry").get_text()
        custRepViaEmail    = self.builder.get_object("custRepViaEmailChk").get_active()
        custAddress        = self.builder.get_object("custAddressEntry").get_text()
        custPostalCode     = self.postalcodeEntry.get_text()
        callResponsible    = self.builder.get_object("callResponsibleEntry").get_text()
        custConnector      = self.builder.get_object("custConnectorEntry").get_text()
        custDesc           = self.builder.get_object("custDescEntry").get_text()
        
        custPhone = utility.convertToLatin(custPhone)
        custCell = utility.convertToLatin(custCell)
        custFax = utility.convertToLatin(custFax)
        custPersonalCode = utility.convertToLatin(custPersonalCode)
        custPostalCode = utility.convertToLatin(custPostalCode)
        #----------------------------------
#        self.custTypeBuyer = self.custTypeBuyerChk.get_active()
#        self.custTypeSeller = self.custTypeSellerChk.get_active()
#        self.custTypeMate = self.custTypeMateChk.get_active()
#        self.custTypeAgent = self.custTypeAgentChk.get_active()
#        self.custIntroducer = self.custIntroducerEntry.get_text()
#        self.custCommissionRate = self.custCommissionRateEntry.get_text()
#        self.custDiscRate = self.custDiscRateEntry.get_text()
#        self.marked = self.markedChk.get_active()
#        self.markedReason = self.markedReasonEntry.get_text()
#        #----------------------------------
#        self.custBalance = self.custBalanceEntry.get_text()
#        self.custCredit = self.custCreditEntry.get_text()
#        self.custAccName1 = self.custAccName1Entry.get_text()
#        self.custAccNo1 = self.custAccNo1Entry.get_text()
#        self.custAccBank1 = self.custAccBank1Entry.get_text()
#        self.custAccName2 = self.custAccName2Entry.get_text()
#        self.custAccNo2 = self.custAccNo2Entry.get_text()
#        self.custAccBank2 = self.custAccBank2Entry.get_text()
        
        if not self.editCustomer:
            customer = Customers(custCode, unicode(custName), custPhone, custCell, custFax, unicode(custAddress), custEmail,
                             unicode(custEcnmcsCode), custWebPage, unicode(callResponsible), unicode(custConnector), groupid, 
                             custPostalCode, custPersonalCode, unicode(custDesc))
        else:
            query = config.db.session.query(Customers).select_from(Customers)
            customer = query.filter(Customers.custId == self.customerId).first()
            customer.custCode = custCode
            customer.custName = unicode(custName)
            customer.custPhone = custPhone
            customer.custCell = custCell
            customer.custFax = custFax
            customer.custAddress = unicode(custAddress)
            customer.custPostalCode = custPostalCode
            customer.custEmail = custEmail
            customer.custEcnmcsCode = unicode(custEcnmcsCode)
            customer.custPersonalCode = custPersonalCode
            customer.custWebPage = custWebPage
            customer.custResponsible = unicode(callResponsible)
            customer.custConnector = unicode(custConnector)
            customer.custGroup = groupid
            customer.custDesc = unicode(custDesc)
            
        config.db.session.add(customer)
        config.db.session.commit()
        
        #Show new customer in table
        if self.treestore != None:
            parent_iter = self.treestore.get_iter_first()
            while self.treestore.iter_is_valid(parent_iter):
                itercode = self.treestore.get_value(parent_iter, 0)
                if itercode == custGrp:
                    break
                parent_iter = self.treestore.iter_next(parent_iter)
                
            if config.digittype == 1:
                custCode = utility.convertToPersian(custCode)
            
            if not self.editCustomer:
                self.treestore.append(parent_iter, (custCode, custName, "0.0", "0.0"))
            else:
                self.treestore.set(self.editIter, 0, custCode, 1, custName)
                
        return 0

    def editCustAndGrps(self, sender):
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        
        if self.treestore.iter_parent(iter) == None:
            #Iter points to a customer group
            self.editCustomerGroup(sender)
        else:            
            code = self.treestore.get_value(iter, 0)
            code = utility.convertToLatin(code)
            query = config.db.session.query(Customers, CustGroups.custGrpCode)
            query = query.select_from(outerjoin(CustGroups, Customers, CustGroups.custGrpId == Customers.custGroup))
            result = query.filter(Customers.custCode == code).first()
            customer = result[0]
            groupcode = result[1]
            
            if config.digittype == 1:
                custCode = utility.convertToPersian(customer.custCode)
                custGrp = utility.convertToPersian(groupcode)
                custPhone = utility.convertToPersian(customer.custPhone)
                custCell = utility.convertToPersian(customer.custCell)
                custFax = utility.convertToPersian(customer.custFax)
                custPersonalCode = utility.convertToPersian(customer.custPersonalCode)
                custPostalCode = utility.convertToPersian(customer.custPostalCode)
            else:
                custCode = customer.custCode
                custGrp = groupcode
                custPhone = customer.custPhone
                custCell = customer.custCell
                custFax = customer.custFax
                custPersonalCode = customer.custPersonalCode
                custPostalCode = customer.custPostalCode
            
            self.customerForm = self.builder.get_object("customersWindow")
            self.customerForm.set_title(_("Edit Customer"))
            self.builder.get_object("addCustSubmitBtn").set_label(_("Save Customer"))
            
            self.builder.get_object("custCodeEntry").set_text(custCode)
            self.builder.get_object("custNameEntry").set_text(customer.custName)
            self.builder.get_object("custGrpEntry").set_text(groupcode)
            
            self.builder.get_object("custEcnmcsCodeEntry").set_text(customer.custEcnmcsCode)
            self.builder.get_object("custPhoneEntry").set_text(custPhone)
            self.builder.get_object("custCellEntry").set_text(custCell)
            self.builder.get_object("custFaxEntry").set_text(custFax)
            self.builder.get_object("custWebPageEntry").set_text(customer.custWebPage)
            self.builder.get_object("custEmailEntry").set_text(customer.custEmail)
            self.builder.get_object("custRepViaEmailChk").set_active(customer.custRepViaEmail)
            self.builder.get_object("custAddressEntry").set_text(customer.custAddress)
            self.builder.get_object("callResponsibleEntry").set_text(customer.custResposible)
            self.builder.get_object("custConnectorEntry").set_text(customer.custConnector)
            self.builder.get_object("custDescEntry").set_text(customer.custDesc)
            self.personalcodeEntry.set_text(custPersonalCode)
            self.postalcodeEntry.set_text(custPostalCode)
            self.builder.get_object("markedReasonEntry").set_sensitive(self.builder.get_object("markedChk").get_active())
            
            self.customerForm.show_all()
            
            self.editCustomer = True
            self.customerId = customer.custId
            self.editIter = iter
        
    def deleteCustAndGrps(self, sender):
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        
        if self.treestore.iter_parent(iter) == None:
            #Iter points to a customer group
            self.deleteCustomerGroup(sender)
        else:
            #Iter points to a customer
            code = self.treestore.get_value(iter, 0)
            query = config.db.session.query(Customers).select_from(Customers)
            customer = query.filter(Customers.custCode == code).first()
            
            #TODO check if this customer is used somewhere else
            
            config.db.session.delete(customer)
            config.db.session.commit()
            self.treestore.remove(iter)
                
    
    #@param treeiter: the TreeIter which data should be saved in
    #@param data: a tuple containing data to be saved
    def saveRow(self, treeiter, data):
        if len(data) == 3:
            #A customer group should be saved, just set code and name.
            self.treestore.set(treeiter, 0, data[0], 1, data[1])
        elif len(data) == 4:
            #A customer should be saved, set all given data.
            self.treestore.set(treeiter, 0, data[0], 1, data[1], 2, data[2], 3, data[3])

    def on_addCustomerBtn_clicked(self, sender):
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        pcode = ""
        if (iter != None and self.treestore.iter_parent(iter) == None):
                pcode = self.treestore.get_value(iter, 0)
        self.addNewCustomer(sender, pcode)
        
    def selectGroup(self, sender):
        obj = customergroup.Group()
        obj.connect("group-selected", self.groupSelected)
        obj.viewCustomerGroups()
        
        code = self.builder.get_object("custGrpEntry").get_text()
        obj.highlightGroup(code)
    
    def groupSelected(self, sender, id, code):
        self.builder.get_object("custGrpEntry").set_text(code)
        sender.window.destroy()  
             
#----------------------------------------------------------------------
# Creating New Signal to return the selected group when double clicked!
#----------------------------------------------------------------------
#gobject.type_register(                          Customer                )
#
#gobject.signal_new( "customer-selected",        Customer, 
#                    gobject.SIGNAL_RUN_LAST,    gobject.TYPE_NONE, 
#                    (gobject.TYPE_INT,          gobject.TYPE_STRING)    )
