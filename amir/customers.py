import sys
import os

import  warehousing
import  numberentry
import  dateentry
import  subjects
import  customergroup
import  gobject
import  pygtk
import  gtk

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

    def __init__(self,buyerFlg=True,sellerFlg=True,mateFlg=True,agentFlg=True):
        
        self.buyerFlg   = buyerFlg
        self.sellerFlg  = sellerFlg
        self.MateFlg    = mateFlg
        self.AgentFlg   = agentFlg
        self.builder    = get_builder("customers" )
        self.session    = config.db.session
        
        self.grpCodeEntry = numberentry.NumberEntry()
        box = self.builder.get_object("grpCodeBox")
        box.add(self.grpCodeEntry)
        self.grpCodeEntry.show()
        
        self.window = self.builder.get_object("viewCustomersWindow")
        
        self.treeview = self.builder.get_object("customersTreeView")
        self.treestore = gtk.TreeStore(str,str,str,str)
        self.treestore.clear()
        self.treeview.set_model(self.treestore)
        
        headers = (_("Code"),_("Name"),_("Balance"),_("Credit"))
        txt = 0
        for header in headers:
            column = gtk.TreeViewColumn(header, gtk.CellRendererText(), text = txt)
            column.set_spacing(5)
            column.set_resizable(True)
            self.treeview.append_column(column)
            txt += 1
        self.treeview.get_selection().set_mode(  gtk.SELECTION_SINGLE    )
        
#        self.fillCustomersList()
        
        self.window.show_all()
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
            grpIter = self.treestore.append(None, (grpCode, grpName, "", ""))
            
            customers   = self.session.query( Customers ).select_from( Customers )
            customers   = customers.filter( Customers.custGroup == grpId ).all()
            for customer in customers:
                #"Code","Name","Balance","Credit"
                cde = customer.custCode
                nme = customer.custName
                blnc    = customer.custBalance
                crdt    = customer.custCredit
                self.treestore.append(grpIter, (cde, nme, blnc, crdt))
    
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
    
#    def addCustomerGroup(self, sender):
#        dialog = self.builder.get_object("addCustGrpDlg")
#        self.builder.get_object("okGroup").set_label(_("Add"))
#        dialog.run()
        
    def on_addCustomerGroup_response(self, sender, response_id):
        if response_id == 1 :
            grpcode = self.grpCodeEntry.get_text()
            grpname = self.builder.get_object("grpNameEntry").get_text()
            grpdesc = self.builder.get_object("grpDescEntry").get_text()
            msg = ""
            if grpname == "":
                msg = _("Group name should not be empty")
            elif grpcode == "":
                msg = _("Group code should not be empty")
                
            if msg != "":
                msgbox =  gtk.MessageDialog(sender, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE, msg)
                msgbox.set_title(_("Empty fields"))
                msgbox.run()
                msgbox.destroy()
                return
            else:
                self.saveCustGroup(grpcode, unicode(grpname), unicode(grpdesc), False)
        sender.hide()
            
        
    #===========================================================================
    # def groupOKPressed(self, sender):
    #    grpcode = self.grpCodeEntry.get_int()
    #    grpname = self.builder.get_object("grpNameEntry").get_text()
    #    grpdesc = self.builder.get_object("grpDescEntry").get_text()
    #    self.saveCustGroup(grpcode, unicode(grpname), unicode(grpdesc), False)
    # 
    # def groupCancelPressed(self,sender=0,ev=0):
    #    self.addCustGrpDlg.hide_all()
    #    return False
    #===========================================================================
    
#    def saveCustGroup(self, code, name, desc, edit=False):
#        query = config.db.session.query(CustGroups).select_from(CustGroups)
#        query = query.filter(or_(CustGroups.custGrpCode == code, CustGroups.custGrpName == name))
#        result = query.all()
#        msg = ""
#        for grp in result:
#            if grp.custGrpCode == code:
#                msg = _("A group with this code already exists.")
#                break
#            elif grp.custGrpName == name:
#                msg = _("A group with this name already exists.")
#                break
#        if msg != "":
#            msgbox =  gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, msg)
#            msgbox.set_title(_("Duplicate group"))
#            msgbox.run()
#            msgbox.destroy()
#            return
#        
#        group = CustGroups(code, name, desc)
#        config.db.session.add(group)
#        config.db.session.commit()
#        
#        row = self.treestore.append(None, (code, name, "", ""))
#        path = self.treestore.get_path(row)
#        self.treeview.scroll_to_cell(path, None, False, 0, 0)
#        self.treeview.set_cursor(path, None, False)
        
    ############################################################################
    ##  Show Groups Window (Only Groups)
    ############################################################################
    def fillCustGroupsList(self):
        groups  = self.session.query( CustGroups ).select_from( CustGroups ).order_by(CustGroups.custGrpCode.desc()).all()
        for group in groups:
            grpCode = group.custGrpCode
            grpName = group.custGrpName
            grpDesc = group.custGrpDesc
            grpIter = self.custGrpListStore.append(None, (grpCode,grpName,grpDesc))
            
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
