import sys
import os

import  warehousing
import  numberentry
import  dateentry
import  subjects
import  gobject
import  pygtk
import  gtk

from    sqlalchemy.orm              import  sessionmaker, join
from    helpers                     import  get_builder
from    sqlalchemy.orm.util         import  outerjoin
from    amirconfig                  import  config
from    datetime                    import  date
from    sqlalchemy.sql              import  and_
from    sqlalchemy.sql.functions    import  *
from    database                    import  *
import __main__

pygtk.require('2.0')

class Customer(gobject.GObject):
    
    def __init__(self,buyerFlg=True,sellerFlg=True,mateFlg=True,agentFlg=True,show=True):
        
        self.buyerFlg   = buyerFlg
        self.sellerFlg  = sellerFlg
        self.MateFlg    = mateFlg
        self.AgentFlg   = agentFlg
        self.builder    = get_builder(      "customers"               )
        self.session    = config.db.session
        
        self.viewCustWin = self.builder.get_object("viewCustomersWindow")
        
        self.customersTreeView = self.builder.get_object("customersTreeView")
        self.custsListStore = gtk.TreeStore(str,str,str,str)
        self.custsListStore.clear()
        self.customersTreeView.set_model(self.custsListStore)
        
        headers = ("Code","Name","Balance","Credit")
        txt = 0
        for header in headers:
            column = gtk.TreeViewColumn(header,gtk.CellRendererText(),text = txt)
            column.set_spacing(5)
            column.set_resizable(True)
            self.customersTreeView.append_column(column)
            txt += 1
        self.customersTreeView.get_selection().set_mode(  gtk.SELECTION_SINGLE    )
        
        self.fillCustomersList()
        
        self.custGroupsTreeView = self.builder.get_object("custGroupsTreeView")
        self.custGrpListStore = gtk.ListStore(str,str,str)
        self.custGrpListStore.clear()
        self.custGroupsTreeView.set_model(self.custsListStore)

        headers = ("Code","Name","Description")
        txt = 0
        for header in headers:
            column = gtk.TreeViewColumn(header,gtk.CellRendererText(),text = txt)
            column.set_spacing(5)
            column.set_resizable(True)
            self.custGroupsTreeView.append_column(column)
            txt += 1
        self.custGroupsTreeView.get_selection().set_mode(  gtk.SELECTION_SINGLE    )

        self.fillCustGroupsList()

        if show:
            self.viewCustWin.show_all()
        
        self.builder.connect_signals(self)
        
    ############################################################################
    ##  Show Customers and Groups Window
    ############################################################################
    def fillCustomersList(self):
#        clause  = ""
#        if self.buyerFlg == True:
#            clause  = 
#        self.sellerFlg  = sellerFlg
#        self.MateFlg    = MateFlg
#        self.AgentFlg   = AgentFlg

        groups  = self.session.query( CustGroups ).select_from( CustGroups ).all()
        for group in groups:
            grpId   = group.custGrpId
            grpCode = group.custGrpCode
            grpName = group.custGrpName
            grpIter = self.custsListStore.append(None,(grpCode,grpName,"",""))
            
            customers   = self.session.query( Customers ).select_from( Customers )
            customers   = customers.filter( Customers.custGroup == grpId ).all()
            for customer in customers:
                #"Code","Name","Balance","Credit"
                cde = customer.custCode
                nme = customer.custName
                blnc    = customer.custBalance
                crdt    = customer.custCredit
                self.custsListStore.append(grpIter,(cde,nme,blnc,crdt))
    
    def deleteCustAndGrps(self,sender=0):
        pass
    
    def editCustAndGrps(self,sender=0):
        self.editCustomer   = True
        pass
    
    def closeCustGrpsWin(self,sender=0):
        self.viewCustWin.hide_all()
        return False

    ############################################################################
    #  Add Customers Window
    ############################################################################
    def addNewCustomer(self,sender=0,code=0):
        if code:
            title = _("Edit Customer: %s") %code
            self.editCustomer = True
        else:
            title = "Add New Customer"
            self.editCustomer = False
            
        self.customerForm = self.builder.get_object("customersWindow")
        self.customerForm.set_title( title )
        
        self.addBtn = self.builder.get_object("addCustSubmitBtn")
        self.addBtn.set_label("Add Customer")
        
        self.custCodeEntry = self.builder.get_object("custCodeEntry")
        self.custGrpEntry = self.builder.get_object("custGrpEntry")
        self.custNameEntry = self.builder.get_object("custNameEntry")
        self.custEcnmcsCodeEntry = self.builder.get_object("custEcnmcsCodeEntry")
        self.custPhoneEntry = self.builder.get_object("custPhoneEntry")
        self.custCellEntry = self.builder.get_object("custCellEntry")
        self.custFaxEntry = self.builder.get_object("custFaxEntry")
        self.custWebPageEntry = self.builder.get_object("custWebPageEntry")
        self.custEmailEntry = self.builder.get_object("custEmailEntry")
        self.custRepViaEmailChk = self.builder.get_object("custRepViaEmailChk")
        self.custAddressEntry = self.builder.get_object("custAddressEntry")
        self.callResponsibleEntry = self.builder.get_object("callResponsibleEntry")
        self.custConnectorEntry = self.builder.get_object("custConnectorEntry")
        self.custDescEntry = self.builder.get_object("custDescEntry")
        #----------------------------------
        self.custTypeBuyerChk = self.builder.get_object("custTypeBuyerChk")
        self.custTypeSellerChk = self.builder.get_object("custTypeSellerChk")
        self.custTypeMateChk = self.builder.get_object("custTypeMateChk")
        self.custTypeAgentChk = self.builder.get_object("custTypeAgentChk")
        self.custIntroducerEntry = self.builder.get_object("custIntroducerEntry")
        self.custCommissionRateEntry = self.builder.get_object("custCommissionRateEntry")
        self.custDiscRateEntry = self.builder.get_object("custDiscRateEntry")
        self.markedChk = self.builder.get_object("markedChk")
        self.markedReasonEntry = self.builder.get_object("markedReasonEntry")
        #----------------------------------
        self.custBalanceEntry = self.builder.get_object("custBalanceEntry")
        self.custCreditEntry = self.builder.get_object("custCreditEntry")
        self.custAccName1Entry = self.builder.get_object("custAccName1Entry")
        self.custAccNo1Entry = self.builder.get_object("custAccNo1Entry")
        self.custAccBank1Entry = self.builder.get_object("custAccBank1Entry")
        self.custAccName2Entry = self.builder.get_object("custAccName2Entry")
        self.custAccNo2Entry = self.builder.get_object("custAccNo2Entry")
        self.custAccBank2Entry = self.builder.get_object("custAccBank2Entry")

        self.customerForm.show_all()
        
    def customerFormCanceled(self,sender=0,ev=0):
        self.customerForm.hide_all()
        return False
        
    def customerFormOkPressed(self,sender=0,ev=0):
        if self.editCustomer:
            self.submitEditCust()
        else:
            self.submitAddCust()
    
    def submitEditCust(self):
        print "SUBMIT  EDIT"
    
    def submitAddCust(self):
        self.custCode = self.custCodeEntry.get_text()
        if self.custCode == "":
            print "ERROR - Customer Code Cannot be Empty!"
        else:
            codeQuery = self.session.query( Customers ).select_from( Customers )
            codeQuery = codeQuery.filter( Customers.custCode == self.custCode ).first()
            if codeQuery:
                print "ERROR - customer code has been used before!"
                return
        #--------------------
        self.custGrp = self.custGrpEntry.get_text()
        if self.custGrp == "":
            print "ERROR - Customer Group Cannot be Empty!"
        else:
            grpQuery = self.session.query( CustGroups ).select_from( CustGroups ).filter( Customers.custCode == self.custCode ).first()
            if codeQuery:
                print "ERROR - customer code has been used before!"
                return
        #--------------------
        self.custName = self.custNameEntry.get_text()
        if self.custGrp == "":
            print "ERROR - Customer Group Cannot be Empty!"
        else:
            grpQuery = self.session.query( CustGroups ).select_from( CustGroups ).filter( Customers.custCode == self.custCode ).first()
            if codeQuery:
                print "ERROR - customer code has been used before!"
                return
        #--------------------
        self.custEcnmcsCode = self.custEcnmcsCodeEntry.get_text()
        self.custPhone = self.custPhoneEntry.get_text()
        self.custCell = self.custCellEntry.get_text()
        self.custFax = self.custFaxEntry.get_text()
        self.custWebPage = self.custWebPageEntry.get_text()
        self.custEmail = self.custEmailEntry.get_text()
        self.custRepViaEmail = self.custRepViaEmailChk.get_active()
        self.custAddress = self.custAddressEntry.get_text()
        self.callResponsible = self.callResponsibleEntry.get_text()
        self.custConnector = self.custConnectorEntry.get_text()
        self.custDesc = self.custDescEntry.get_text()
        #----------------------------------
        self.custTypeBuyer = self.custTypeBuyerChk.get_active()
        self.custTypeSeller = self.custTypeSellerChk.get_active()
        self.custTypeMate = self.custTypeMateChk.get_active()
        self.custTypeAgent = self.custTypeAgentChk.get_active()
        self.custIntroducer = self.custIntroducerEntry.get_text()
        self.custCommissionRate = self.custCommissionRateEntry.get_text()
        self.custDiscRate = self.custDiscRateEntry.get_text()
        self.marked = self.markedChk.get_active()
        self.markedReason = self.markedReasonEntry.get_text()
        #----------------------------------
        self.custBalance = self.custBalanceEntry.get_text()
        self.custCredit = self.custCreditEntry.get_text()
        self.custAccName1 = self.custAccName1Entry.get_text()
        self.custAccNo1 = self.custAccNo1Entry.get_text()
        self.custAccBank1 = self.custAccBank1Entry.get_text()
        self.custAccName2 = self.custAccName2Entry.get_text()
        self.custAccNo2 = self.custAccNo2Entry.get_text()
        self.custAccBank2 = self.custAccBank2Entry.get_text()


    ############################################################################
    ##  Add Groups Window
    ############################################################################
    
    def addCustomerGroup(self,sender=0,ev=0):
        self.addCustGrpDlg = self.builder.get_object("addCustGrpDlg")        
        self.addCustGrpDlg.show_all()
        
    def groupOKPressed(self,sender=0,ev=0):
        pass
    
    def groupCancelPressed(self,sender=0,ev=0):
        self.addCustGrpDlg.hide_all()
        return False
    
    ############################################################################
    ##  Show Groups Window (Only Groups)
    ############################################################################
    def fillCustGroupsList(self):
        groups  = self.session.query( CustGroups ).select_from( CustGroups ).order_by(CustGroups.custGrpCode.desc()).all()
        for group in groups:
            grpCode = group.custGrpCode
            grpName = group.custGrpName
            grpDesc = group.custGrpDesc
            grpIter = self.custGrpListStore.append((grpCode,grpName,grpDesc))
            
    def showCustGroups(self,sender=0,ev=0):
        self.viewGroupsWin = self.builder.get_object("viewCustGroupsWindow")
        self.viewGroupsWin.show_all()
        
    def closeGroups(self,sender=0,ev=0):
        self.viewGroupsWin.hide_all()
        return False
        
    #---------------------------------------------------
    def slctCustGrp(         self,   sender  = 0     ):
        grps_win    = self.showCustGroups()
        self.handid = self.connect( "custGroup-selected",
                                    self.setSelectedCustGrp )
    #--------------------------------------------------------
    def setSelectedCustGrp(  self,   sender,     id,     code    ):
        self.custGrpEntry.set_text( code )
#        self.accGroupCode   = code
#        self.accGroupID     = id
        sender.viewGroupsWin.destroy(                                      )
        self.disconnect(            self.handid         )
    #----------------------------------------------------------------
    def selectCustGroupFromList(self, treeview, path, view_column ):
        iter = self.custGrpListStore.get_iter(path)
        code = self.custGrpListStore.get(iter, 0)[0]
        name = self.custGrpListStore.get(iter, 1)[0]
        
        query = self.session.query( CustGroups ).select_from( CustGroups )
        query = query.filter(CustGroups.custGrpCode == code)
        grp_id = query.first().custGrpId

        self.emit("custGroup-selected", grp_id, code )
    #--------------------------------------------------------------
    def selectCustomerFromList(self, treeview, path, view_column ):
        iter = self.custsListStore.get_iter(path)
        code = self.custsListStore.get(iter, 0)[0]
        name = self.custsListStore.get(iter, 1)[0]
        blnc = self.custsListStore.get(iter, 2)[0]
        if blnc:
            query = self.session.query( Customers ).select_from( Customers )
            query = query.filter(Customers.custCode == code)
            cust_id = query.first().custId
            self.emit("customer-selected", cust_id, code )
        else:
            pass        
#----------------------------------------------------------------------
# Creating New Signal to return the selected group when double clicked!
#----------------------------------------------------------------------
gobject.type_register(                          Customer                )
gobject.signal_new( "custGroup-selected",       Customer, 
                    gobject.SIGNAL_RUN_LAST,    gobject.TYPE_NONE, 
                    (gobject.TYPE_INT,          gobject.TYPE_STRING)    )

gobject.signal_new( "customer-selected",        Customer, 
                    gobject.SIGNAL_RUN_LAST,    gobject.TYPE_NONE, 
                    (gobject.TYPE_INT,          gobject.TYPE_STRING)    )
