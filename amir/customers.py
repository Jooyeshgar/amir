import  gobject
import  pygtk
import  gtk

#import  warehousing
import  class_subject
import  decimalentry
import  numberentry
import  dateentry
import  subjects
import  customergroup
from    utility                     import  LN,readNumber
from    dbconfig                    import dbconf

from    sqlalchemy.orm              import  sessionmaker, join
from    sqlalchemy.orm.util         import  outerjoin
from    sqlalchemy.sql              import  and_, or_
from    sqlalchemy.sql.functions    import  *

from    helpers                     import  get_builder
from    share                       import  share
from    datetime                    import  date
from    database                    import  *
from amir.dbconfig import dbconf

pygtk.require('2.0')
config = share.config

## \defgroup UserInterface
## @{

## Register or edit a customer and create a subject row
class Customer(customergroup.Group):

    def __init__(self):
        customergroup.Group.__init__(self)
    
        self.custgrpentry = numberentry.NumberEntry(10)
        self.builder.get_object("custGrpBox").add(self.custgrpentry)
        self.custgrpentry.show()

        self.custIntroducerEntry = numberentry.NumberEntry(10)
        self.builder.get_object("custIntroducerBox").add(self.custIntroducerEntry)
        self.custIntroducerEntry.show()

        self.boxCommissionRateEntry = decimalentry.DecimalEntry(10)
        self.builder.get_object("boxCommissionRateEntry").add(self.boxCommissionRateEntry)
        self.boxCommissionRateEntry.show()
        
        self.boxDiscRateEntry = decimalentry.DecimalEntry(10)
        self.builder.get_object("boxDiscRateEntry").add(self.boxDiscRateEntry)
        self.boxDiscRateEntry.show()
                
        self.boxBalanceEntry = decimalentry.DecimalEntry(10)
        self.builder.get_object("boxBalanceEntry").add(self.boxBalanceEntry)
        self.boxBalanceEntry.show()
        
        self.boxCreditEntry = decimalentry.DecimalEntry(10)
        self.builder.get_object("boxCreditEntry").add(self.boxCreditEntry)
        self.boxCreditEntry.show()
    
    ## show list of customer            
    def viewCustomers(self, readonly=False):
        self.window = self.builder.get_object("viewCustomersWindow")
        if readonly :
            self.costmenu = self.builder.get_object("customersToolbar")
            self.costmenu.hide()
            
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

    ## Show add customers window
    def addNewCustomer(self, sender, pcode = ""):
        self.editCustomer = False
        
        self.customerForm = self.builder.get_object("customersWindow")
        self.customerForm.set_title(_("Add New Customer"))
        self.builder.get_object("addCustSubmitBtn").set_label(_("Add Customer"))

        query = config.db.session.query(Subject.code).select_from(Subject).order_by(Subject.id.desc())
        code = query.filter(Subject.parent_id == dbconf.get_int('custSubject')).first()
        if code == None :
            lastcode = "01"
        else :
            lastcode = "%02d" % (int(code[0][-2:]) + 1)
            
        self.builder.get_object("custCodeEntry").set_text(LN(lastcode))
        #self.custgrpentry.set_text("")
        self.builder.get_object("custNameEntry").set_text("")
        self.builder.get_object("custEcnmcsCodeEntry").set_text("")
        self.builder.get_object("custPrsnalCodeEntry").set_text("")

        self.builder.get_object("custPhoneEntry").set_text("")
        self.builder.get_object("custCellEntry").set_text("")
        self.builder.get_object("custFaxEntry").set_text("")
        self.builder.get_object("custWebPageEntry").set_text("")
        self.builder.get_object("custEmailEntry").set_text("")
        self.builder.get_object("custRepViaEmailChk").get_active()
        self.builder.get_object("custAddressEntry").set_text("")
        self.builder.get_object("cusPostalCodeEntry").set_text("")
        
        self.builder.get_object("callResponsibleEntry").set_text("")
        self.builder.get_object("custConnectorEntry").set_text("")

        self.builder.get_object("custDescEntry").set_text("")
        #----------------------------------
        self.builder.get_object("custTypeBuyerChk").set_active(True)
        self.builder.get_object("custTypeSellerChk").set_active(True)
        self.builder.get_object("custTypeMateChk").set_active(False)
        self.builder.get_object("custTypeAgentChk").set_active(False)
        self.custIntroducerEntry.set_text("")
        self.boxCommissionRateEntry.set_text("")
        self.boxDiscRateEntry.set_text("")
        self.builder.get_object("markedChk").set_active(False)
        self.builder.get_object("markedReasonEntry").set_text("")
        #----------------------------------
        self.boxBalanceEntry.set_text("")
        self.boxCreditEntry.set_text("")
        self.builder.get_object("custAccName1Entry").set_text("")
        self.builder.get_object("custAccNo1Entry").set_text("")
        self.builder.get_object("custAccBank1Entry").set_text("")
        self.builder.get_object("custAccName2Entry").set_text("")
        self.builder.get_object("custAccNo2Entry").set_text("")
        self.builder.get_object("custAccBank2Entry").set_text("")
        
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
    ## save customer to database
    #@return: -1 on error, 0 for success
    def saveCustomer(self):
        custCode			= unicode(self.builder.get_object("custCodeEntry").get_text())
        custGrp 			= self.custgrpentry.get_int()
        custName 			= unicode(self.builder.get_object("custNameEntry").get_text())
        custEcnmcsCode      = unicode(self.builder.get_object("custEcnmcsCodeEntry").get_text())
        custPersonalCode    = unicode(self.builder.get_object("custPrsnalCodeEntry").get_text())

        custPhone           = unicode(self.builder.get_object("custPhoneEntry").get_text())
        custCell            = unicode(self.builder.get_object("custCellEntry").get_text())
        custFax             = unicode(self.builder.get_object("custFaxEntry").get_text())
        custWebPage         = unicode(self.builder.get_object("custWebPageEntry").get_text())
        custEmail           = unicode(self.builder.get_object("custEmailEntry").get_text())
        custRepViaEmail     = self.builder.get_object("custRepViaEmailChk").get_active()
        custAddress         = unicode(self.builder.get_object("custAddressEntry").get_text())
        custPostalCode      = unicode(self.builder.get_object("cusPostalCodeEntry").get_text())
        
        callResponsible     = unicode(self.builder.get_object("callResponsibleEntry").get_text())
        custConnector       = unicode(self.builder.get_object("custConnectorEntry").get_text())

        custDesc            = unicode(self.builder.get_object("custDescEntry").get_text())
        #----------------------------------
        custTypeBuyer       = self.builder.get_object("custTypeBuyerChk").get_active()
        custTypeSeller      = self.builder.get_object("custTypeSellerChk").get_active()
        custTypeMate        = self.builder.get_object("custTypeMateChk").get_active()
        custTypeAgent       = self.builder.get_object("custTypeAgentChk").get_active()
        custIntroducer      = self.custIntroducerEntry.get_int()
        custCommission      = self.boxCommissionRateEntry.get_float()
        custDiscRate        = self.boxDiscRateEntry.get_float()
        custMarked          = self.builder.get_object("markedChk").get_active()
        custReason          = unicode(self.builder.get_object("markedReasonEntry").get_text())
        #----------------------------------
        custBalance         = self.boxBalanceEntry.get_float()
        custCredit          = self.boxCreditEntry.get_float()
        custAccName1        = unicode(self.builder.get_object("custAccName1Entry").get_text())
        custAccNo1          = unicode(self.builder.get_object("custAccNo1Entry").get_text())
        custAccBank1        = unicode(self.builder.get_object("custAccBank1Entry").get_text())
        custAccName2        = unicode(self.builder.get_object("custAccName2Entry").get_text())
        custAccNo2          = unicode(self.builder.get_object("custAccNo2Entry").get_text())
        custAccBank2        = unicode(self.builder.get_object("custAccBank2Entry").get_text())
        
        msg = ""
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
        if custName == "":
            msg += _("Customer name should not be empty.\n")
            
        #--------------------
        if msg != "":
            msgbox = gtk.MessageDialog(self.customerForm, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, msg)
            msgbox.set_title(_("Can not save customer"))
            msgbox.run()
            msgbox.destroy()
            return -1

        if not self.editCustomer:
            #New Customer
            sub = class_subject.Subjects()
            custSubj = sub.add(dbconf.get_int('custSubject'), custName)
            customer = Customers(custCode, custName, custSubj, custPhone, custCell, custFax, custAddress,
                                custEmail, custEcnmcsCode, custWebPage, callResponsible, custConnector,
                                groupid, custPostalCode, custPersonalCode, custDesc, custBalance, custCredit,
                                custRepViaEmail, custAccName1, custAccNo1, custAccBank1, custAccName2, custAccNo2, 
                                custAccBank2, custTypeBuyer, custTypeSeller, custTypeMate, custTypeAgent, 
                                custIntroducer, custCommission, custMarked, custReason, custDiscRate )
        else:
            query = config.db.session.query(Customers).select_from(Customers)
            customer = query.filter(Customers.custId == self.customerId).first()
            #customer code not need to change
            #customer.custCode = custCode
            customer.custName = custName
            customer.custPhone = custPhone
            customer.custCell = custCell
            customer.custFax = custFax
            customer.custAddress = custAddress
            customer.custPostalCode = custPostalCode
            customer.custEmail = custEmail
            customer.custEcnmcsCode = custEcnmcsCode
            customer.custPersonalCode = custPersonalCode
            customer.custWebPage = custWebPage
            customer.custResponsible = callResponsible
            customer.custConnector = custConnector
            customer.custGroup = groupid
            customer.custDesc = custDesc
            #----------------------------------
            customer.custTypeBuyer = custTypeBuyer
            customer.custTypeSeller = custTypeSeller
            customer.custTypeMate = custTypeMate
            customer.custTypeAgent = custTypeAgent
            customer.custIntroducer = custIntroducer
            customer.custCommission = custCommission
            customer.custDiscRate = custDiscRate
            customer.custMarked = custMarked
            customer.custReason = custReason
            #----------------------------------
            customer.custBalance = custBalance
            customer.custCredit = custCredit
            customer.custAccName1 = custAccName1
            customer.custAccNo1 = custAccNo1
            customer.custAccBank1 = custAccBank1
            customer.custAccName2 = custAccName2
            customer.custAccNo2 = custAccNo2
            customer.custAccBank2 = custAccBank2
            
        config.db.session.add(customer)
        config.db.session.commit()
        
        #Show new customer in table
        if self.treestore != None:
            parent_iter = self.treestore.get_iter_first()
            while parent_iter:
                itercode = self.treestore.get_value(parent_iter, 0)
                if itercode == str(custGrp):
                    break
                parent_iter = self.treestore.iter_next(parent_iter)
                
            custCode = LN(custCode)
            
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
            code = readNumber(code)
            query = config.db.session.query(Customers, CustGroups.custGrpCode)
            query = query.select_from(outerjoin(CustGroups, Customers, CustGroups.custGrpId == Customers.custGroup))
            result = query.filter(Customers.custCode == code).first()
            customer = result[0]
            groupcode = result[1]
            
            custCode = LN(customer.custCode, False)
            custGrp = LN(groupcode, False)
            custPhone = LN(customer.custPhone, False)
            custCell = LN(customer.custCell, False)
            custFax = LN(customer.custFax, False)
            custPostalCode = LN(customer.custPostalCode, False)
            
            self.customerForm = self.builder.get_object("customersWindow")
            self.customerForm.set_title(_("Edit Customer"))
            self.builder.get_object("addCustSubmitBtn").set_label(_("Save Customer"))
            
            self.builder.get_object("custCodeEntry").set_text(custCode)
            self.builder.get_object("custNameEntry").set_text(customer.custName)
            self.custgrpentry.set_text(groupcode)
            self.builder.get_object("custEcnmcsCodeEntry").set_text(customer.custEcnmcsCode)
            self.builder.get_object("custPrsnalCodeEntry").set_text(customer.custPersonalCode)
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
            self.builder.get_object("custTypeBuyerChk").set_active(customer.custTypeBuyer)
            #----------------------------------
            self.builder.get_object("custTypeSellerChk").set_active(customer.custTypeSeller)
            self.builder.get_object("custTypeMateChk").set_active(customer.custTypeMate)
            self.builder.get_object("custTypeAgentChk").set_active(customer.custTypeAgent)
            #self.custIntroducerEntry.set_text(customer.custIntroducer)
            self.boxCommissionRateEntry.set_text(customer.custCommission)
            self.boxDiscRateEntry.set_text(customer.custDiscRate)
            self.builder.get_object("markedChk").set_active(customer.custMarked)
            self.builder.get_object("markedReasonEntry").set_text(customer.custReason)
            #----------------------------------
            self.boxBalanceEntry.set_text(LN(customer.custBalance, False))
            self.boxCreditEntry.set_text(LN(customer.custCredit, False))
            self.builder.get_object("custAccName1Entry").set_text(customer.custAccName1)
            self.builder.get_object("custAccNo1Entry").set_text(customer.custAccNo1)
            self.builder.get_object("custAccBank1Entry").set_text(customer.custAccBank1)
            self.builder.get_object("custAccName2Entry").set_text(customer.custAccName2)
            self.builder.get_object("custAccNo2Entry").set_text(customer.custAccNo2)
            self.builder.get_object("custAccBank2Entry").set_text(customer.custAccBank2)
            
            self.builder.get_object("cusPostalCodeEntry").set_text(LN(customer.custPostalCode, False))
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
        
        code = self.custgrpentry.get_text()
        obj.highlightGroup(code)
    
    def groupSelected(self, sender, id, code):
        self.custgrpentry.set_text(code)
        sender.window.destroy()  

    def selectcustomer(self, sender):
        obj = Customer()
        obj.connect("customer-selected", self.customerSelected)
        obj.viewCustomers(True)
        
        code = self.custIntroducerEntry.get_int()
        obj.highlightCust(code)
    
    def customerSelected(self, sender, id, code):
        self.custIntroducerEntry.set_text(code)
        sender.window.destroy()
        
    def highlightCust(self, code):
        '''        iter = self.treestore.get_iter_first()
        pre = iter
        
        while iter:
            itercode = self.treestore.get_value(iter, 0)
            if  itercode < code:
                pre = iter
                iter = self.treestore.iter_next(iter)
            elif itercode == code:
                break
            else:
                iter = pre
                break

        if not iter:
            iter = pre
            
        if iter:
            path = self.treestore.get_path(iter)
            self.treeview.scroll_to_cell(path, None, False, 0, 0)
            self.treeview.set_cursor(path, None, False)
            self.treeview.grab_focus()'''
            
	#Called when a row of customer table get activated by mouse double-click or Enter key
    def selectCustomerFromList(self, treeview, path, view_column):
        iter = self.treestore.get_iter(path)
        if self.treestore.iter_parent(iter) != None:
            code = unicode(self.treestore.get_value(iter, 0))
			
            query = config.db.session.query(Customers).select_from(Customers)
            query = query.filter(Customers.custCode == code)
            customer_id = query.first().custId
            self.emit("customer-selected", customer_id, code)
             
gobject.type_register(Customer)
gobject.signal_new("customer-selected", Customer, gobject.SIGNAL_RUN_LAST,
                   gobject.TYPE_NONE, (gobject.TYPE_INT, gobject.TYPE_STRING))

## @}
