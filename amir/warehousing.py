import  numberentry
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

###################################################################################
##
## Class Warehousing:    Displays all the warehousing registered products. 
##
###################################################################################
class Warehousing(gobject.GObject):
    
    #--------------------------------------------------------------------
    #    initializing method
    #--------------------------------------------------------------------
    def __init__(self):
        """
        This class is created in order to have all the forms and view of 
        products and groups together.
        Groups are viewed through the "viewGroup" method and added by "addNewGroup" 
        method. 
        Products are viewed by the "ViewProducts" method and added by "addNewProduct"
        method.
        """
        gobject.GObject.__init__(self)
        self.builder    = get_builder("warehousing")
        self.session    = config.db.session
        
        self.proListStore   = gtk.TreeStore(str, str, str, str, str)
        self.grpListStore   = gtk.TreeStore(str, str, str, str)
#        self.grpListStore   = gtk.ListStore(str, str, str, str)
        
        self.groupsList     = []
        self.productsList   = []
        
        self.grpIterDict    = {}
        self.proGrpDict     = {}
        self.proProDict     = {}
        
        self.builder.connect_signals(self)
        
    #--------------------------------------------------------------------
    #    viewProducts():
    #--------------------------------------------------------------------
    def viewProducts(self):
        """
        This class will show the products and groups in a tree view, letting the user
        to view the current entries and edit or delete them.
        """
        
        #----- Getting the ui from the file "addProduct.glade" in the data/ui folder.
        self.viewProsWin    = self.builder.get_object("viewProductsWindow")
        
        # ------------- OBJECTS OF THE FORM:
        self.productTreeView    = self.builder.get_object("productsTreeView")
        self.proListStore.clear()

        column      = gtk.TreeViewColumn(_("Code"), 
                                            gtk.CellRendererText(),
                                            text = 0)
        column.set_spacing(5)
        column.set_resizable(True)
        self.productTreeView.append_column(column)
        
        column      = gtk.TreeViewColumn(_("Name"), 
                                            gtk.CellRendererText(),
                                            text = 1)
        column.set_spacing(5)
        column.set_resizable(True)
        self.productTreeView.append_column(column)
        
        column      = gtk.TreeViewColumn(_("Quantity"), 
                                            gtk.CellRendererText(),
                                            text = 2)
        column.set_spacing(5)
        column.set_resizable(True)
        self.productTreeView.append_column(column)
        
        column      = gtk.TreeViewColumn(_("Purchase Price"), 
                                            gtk.CellRendererText(),
                                            text = 3)
        column.set_spacing(5)
        column.set_resizable(True)
        self.productTreeView.append_column(column)

        column      = gtk.TreeViewColumn(_("Selling Price"), 
                                            gtk.CellRendererText(),
                                            text = 4)
        column.set_spacing(5)
        column.set_resizable(True)
        self.productTreeView.append_column(column)

        columnsInSetting    = 0
        # Later we can read this from the setting, which helps us show the needed values of the user
        
        if columnsInSetting: 
            column  = gtk.TreeViewColumn(_("Accounting Group"), 
                                            gtk.CellRendererText(), 
                                            text = 5)
            column.set_spacing(5)
            column.set_resizable(True)
            self.productTreeView.append_column(column)
    
            column  = gtk.TreeViewColumn(_("Product Location"), 
                                            gtk.CellRendererText(),
                                            text = 6)
            column.set_spacing(5)
            column.set_resizable(True)
            self.productTreeView.append_column(column)
            
            column  = gtk.TreeViewColumn(_("Quantity Warning"),
                                            gtk.CellRendererText(),
                                            text = 7)
            column.set_spacing(5)
            column.set_resizable(True)
            self.productTreeView.append_column(column)
    
            column  = gtk.TreeViewColumn(_("Over-Sell"), 
                                            gtk.CellRendererText(),
                                            text = 8)
            column.set_spacing(5)
            column.set_resizable(True)
            self.productTreeView.append_column(column)
    
            column  = gtk.TreeViewColumn(_("Discount Formula"), 
                                            gtk.CellRendererText(),
                                            text = 9)
            column.set_spacing(5)
            column.set_resizable(True)
            self.productTreeView.append_column(column)
    
            column  = gtk.TreeViewColumn(_("Description"), 
                                            gtk.CellRendererText(),
                                            text = 10)
            column.set_spacing(5)
            column.set_resizable(True)
            self.productTreeView.append_column(column)

        self.productTreeView.get_selection().set_mode(gtk.SELECTION_SINGLE)
        self.productTreeView.set_model(self.proListStore)
        self.populateProList()
        
        self.viewProsWin.show_all()
        
    #--------------------------------------------------------------------
    # populateProList():    Method to populate the Product View List
    #--------------------------------------------------------------------
    def populateProList(self):
        self.proListStore.clear()
        self.proGrpDict     = {}
        self.proProDict     = {}
        grpQry  = self.session.query(Groups.id, Groups.code, Groups.name).select_from(Groups)
        grpQry  = grpQry.order_by(Groups.id.asc()).all()
        for grp in grpQry:
            iter    = self.proListStore.append(None,(grp.code,grp.name,"","",""))
            self.proGrpDict[grp.code]   = iter
            proQry  = self.session.query(Products).select_from(Products)
            proQry  = proQry.filter(Products.accGroup == grp.id)
            proQry  = proQry.order_by(Products.id.asc())
            for pro in proQry:
                listVals    = (pro.code, pro.name, pro.quantity,
                                pro.purchacePrice, pro.sellingPrice)
                proiter     = self.proListStore.append(iter, listVals)
                self.proProDict[ pro.code ] = proiter

    #--------------------------------------------------------------------
    # editProGrp():    Method to edit group/product in the database
    #--------------------------------------------------------------------
    def editProGrp(self, sender = 0):
        selection = self.productTreeView.get_selection()
        iter = selection.get_selected()[1]
        if iter:
            code    = self.proListStore.get(iter, 0)[0]
            qnty    = self.proListStore.get(iter, 2)[0]
            if qnty:    #selected iter is a product
                self.proOldId   = self.session.query(Products).select_from(Products)
                self.proOldId   = self.proOldId.filter(Products.code == code).first().id
                self.oldProCd   = code
                self.proEditIter    = iter
                self.addNewProduct(code = code)
            else:       #selected iter is a group
                self.oldId  = self.session.query(Groups).select_from(Groups)
                self.oldId  = self.oldId.filter(Groups.code == code).first().id
                self.oldGrpCd   = code
                self.editIter   = iter
                self.addGroup(code = code)
        
    #--------------------------------------------------------------------
    # delProGrp():    Method to delete group/product from the database
    #--------------------------------------------------------------------
    def delProGrp(self, sender = 0):
        selection = self.productTreeView.get_selection()
        iter = selection.get_selected()[1]
        if iter:
            code    = self.proListStore.get(iter, 0)[0]
            qnty    = self.proListStore.get(iter, 2)[0]
            if qnty:    #selected iter is a product
                msg     = _("Are you sure you want to delete the product \"%s\"") %code
                msgBox  = gtk.MessageDialog(self.viewProsWin,
                                                gtk.DIALOG_MODAL,
                                                gtk.MESSAGE_QUESTION,
                                                gtk.BUTTONS_OK_CANCEL,
                                                msg)
                msgBox.set_title(_("Are you sure?"))
                answer  = msgBox.run()
                msgBox.destroy()
                if answer == gtk.RESPONSE_OK:
                    query       = self.session.query(Products).select_from(Products)
                    query       = query.filter(Products.code == code).first()
                    self.session.delete(query)
                    self.session.commit()
                    self.proListStore.remove(iter)
                    del self.proProDict[ code ]
                
            else:       #selected iter is a group
                if self.proListStore.iter_has_child(iter):
                    msg     = _("Selected Group has some related products and cannot be deleted.")
                    msgbox  = gtk.MessageDialog(self.viewProsWin,
                                                    gtk.DIALOG_MODAL,
                                                    gtk.MESSAGE_WARNING,
                                                    gtk.BUTTONS_OK, msg)
                    msgbox.set_title(_("Unable to Delete"))
                    msgbox.run()
                    msgbox.destroy()
                    return
                else:
                    msg     = _("Are you sure you want to delete the group \"%s\"") %code
                    msgBox  = gtk.MessageDialog(self.viewProsWin,
                                                    gtk.DIALOG_MODAL,
                                                    gtk.MESSAGE_QUESTION,
                                                    gtk.BUTTONS_OK_CANCEL,
                                                    msg)
                    msgBox.set_title(_("Are you sure?"))
                    answer  = msgBox.run()
                    msgBox.destroy()
                    if answer == gtk.RESPONSE_OK:
                        query       = self.session.query(Groups).select_from(Groups)
                        query       = query.filter(Groups.code == code).first()
                        self.session.delete(query)
                        self.session.commit()
                        self.proListStore.remove(iter)
                        if self.grpIterDict.has_key(code):
                            self.grpListStore.remove(self.grpIterDict[ code ])
                            del self.grpIterDict[ code ]

    #--------------------------------------------------------------------
    # addNewProduct():    Method to add new product
    #--------------------------------------------------------------------
    def addNewProduct(self, sender = 0, code = 0):
        """
        This method is creating a user interface for the client to add products
        to the warehousing system. User needs to fill the data into the form and
        the dialog will check the data and save them into database if it is OK.
        
        """
        #----- Getting the ui from the file "addProduct.glade" in the data/ui folder.
        self.addProWin  = self.builder.get_object("addProductWindow")
        if code:
            name    = self.session.query(Products).select_from(Products)
            name    = name.filter(Products.code == code).first().name
            title   = _("Edit Product:\t%(code)s - %(name)s") % {'code':code,'name':name}
            self.proEditFlg = True
        else:
            title       = "Add New Product"
            self.proEditFlg = False
            
        self.addProWin.set_title(title)

        # ------------- OBJECTS OF THE FORM:
        self.proLoc     = self.builder.get_object("proLoc")
        
        self.proCode    = gtk.Entry()
        box             = self.builder.get_object("proCodeHBox")
        box.add(self.proCode)
        self.proCode.show()
        
        self.proName    = self.builder.get_object("proName")
        self.proDesc    = self.builder.get_object("proDesc")
        
        self.proQnty    = numberentry.NumberEntry() 
        box             = self.builder.get_object("qntyHBox")
        box.add(self.proQnty)
        self.proQnty.show()
        
        self.accGroup   = gtk.Entry()
        box             = self.builder.get_object("accGrpHBox")
        box.add(self.accGroup)
        self.accGroup.show()
        
        self.oversell   = self.builder.get_object("oversell")
        self.discFormula    = self.builder.get_object("discFormula")
        self.qntyWarning    = numberentry.NumberEntry()
        box                 = self.builder.get_object("qntyWrnHBox")
        box.add(self.qntyWarning)
        self.qntyWarning.show()
        
        self.sellingPrice   = numberentry.NumberEntry()
        box                 = self.builder.get_object("sellPriceHBox")
        box.add(self.sellingPrice)
        self.sellingPrice.show()
        
        self.purchasePrice  = numberentry.NumberEntry()
        box                 = self.builder.get_object("purchPriceHBox")
        box.add(self.purchasePrice)
        self.purchasePrice.show()

        self.addProWin.show_all()

        if code:
            query   = self.session.query(Products).select_from(Products)
            group   = query.filter(Products.code == code).first()
            accgrp  = self.session.query(Groups).select_from(Groups)
            accgrp  = accgrp.filter(Groups.id == group.accGroup).first().code
            self.proCode.set_text(group.code)
            self.accGroup.set_text(accgrp)
            self.proName.set_text(group.name)
            self.proLoc.set_text(group.location)
            self.proDesc.set_text(group.productDesc)
            self.proQnty.set_text(str(group.quantity))
            self.qntyWarning.set_text(str(group.qntyWarning))
            if group.oversell:
                self.oversell.set_active(True)
            else:
                self.oversell.set_active(False)                
            self.purchasePrice.set_text(str(group.purchacePrice))
            self.sellingPrice.set_text(str(group.sellingPrice))
            self.discFormula.set_text(group.discountFormula)
            
        else:
            self.proLoc.set_text("")
            self.proCode.set_text("")
            self.proName.set_text("")
            self.proDesc.set_text("")
            self.proQnty.set_text("")
            self.accGroup.set_text("")
            self.discFormula.set_text("")
            self.qntyWarning.set_text("")
            self.sellingPrice.set_text("")
            self.purchasePrice.set_text("")
            self.oversell.set_active(False)
            
    #--------------------------------------------------------------------
    # save():    method to invoke when Save Button is pressed.
    #--------------------------------------------------------------------
    def chkProInfo(self, sender  = 0):
        pCode   = self.proCode.get_text()
        pName   = unicode(self.proName.get_text())
        pWarn   = self.qntyWarning.get_int()
        pOver   = self.oversell.get_active()
        pPLoc   = unicode(self.proLoc.get_text())
        pQnty   = self.proQnty.get_int()
        pPurc   = self.purchasePrice.get_int()
        pSell   = self.sellingPrice.get_int()
        pAccc   = self.accGroup.get_text()
        pDesc   = unicode(self.proDesc.get_text())
        pDisc   = unicode(self.discFormula.get_text())
        if not pCode:
            errorstr = _("There must be a \"Code\" for each product.")
            msgbox = gtk.MessageDialog(self.addProWin,
                                                gtk.DIALOG_MODAL, 
                                                gtk.MESSAGE_WARNING, 
                                                gtk.BUTTONS_OK, 
                                                errorstr)
            msgbox.set_title(_("Missing Data"))
            msgbox.run()
            msgbox.destroy()
            return
        elif not pName:
            errorstr = _("There is no \"Name\" mentioned for this product.")
            msgbox = gtk.MessageDialog(self.addProWin,
                                                gtk.DIALOG_MODAL,
                                                gtk.MESSAGE_WARNING,
                                                gtk.BUTTONS_OK,
                                                errorstr)
            msgbox.set_title(_("Missing Data"))
            msgbox.run()
            msgbox.destroy()
            return
        elif not pAccc:
            errorstr = _("No \"Accounting Group\" is selected for this product.")
            msgbox = gtk.MessageDialog(self.addProWin,
                                                gtk.DIALOG_MODAL,
                                                gtk.MESSAGE_WARNING, 
                                                gtk.BUTTONS_OK, 
                                                errorstr)
            msgbox.set_title(_("Missing Data"))
            msgbox.run()
            msgbox.destroy()
            return            
        else:
            query   = self.session.query(Products).select_from(Products)
            cde     = query.filter(Products.code == pCode).first()
            nam     = query.filter(Products.name == pName).first()
            
            acgQ    = self.session.query(Groups).select_from(Groups)
            acgQ    = acgQ.filter(Groups.code == pAccc).first()
            if not acgQ:
                errorstr = _("\"Accounting Group\" which you selected does not exist.")
                msgbox = gtk.MessageDialog(self.addProWin,
                                            gtk.DIALOG_MODAL,
                                            gtk.MESSAGE_WARNING, 
                                            gtk.BUTTONS_OK, 
                                            errorstr)
                msgbox.set_title(_("Wrong Accounting Group ID"))
                msgbox.run()
                msgbox.destroy()
                return            
            else:
                pAccg    = acgQ.id
            
            if self.proEditFlg:
                query   = self.session.query(Products).select_from(Products)
                codeChk = query.filter(Products.code == pCode).first()
                prcd    = False
                prnm    = False
                if codeChk:
                    if codeChk.id  == self.proOldId:
                        prcd    = False
                    else:
                        prcd    = True
                nameChk = query.filter(Groups.name == pName).first()
                if nameChk:
                    if nameChk.id  == self.proOldId:
                        prnm    = False
                    else:
                        prnm    = True
                        
                dup     = False
                err     = ""
                if prcd and prnm:
                    err = _("Both the product \"Code\" and \"Name\" have already been used for other products.")
                    dup = True
                elif prcd:
                    err = _("The product \"Code\" is used for another product before.")
                    dup = True
                elif prnm:
                    err = _("The product \"Name\" is used for another product before.")
                    dup = True
                    
                if dup:
                    msgbox  = gtk.MessageDialog(self.addProWin,
                                                    gtk.DIALOG_MODAL,
                                                    gtk.MESSAGE_WARNING,
                                                    gtk.BUTTONS_OK, err)
                    msgbox.set_title(_("Used Data Selected"))
                    msgbox.run()
                    msgbox.destroy()
                    return
                
                self.editProduct(pCode, pName, pWarn, pOver, pPLoc, pQnty, 
                                    pPurc, pSell, pAccg, pDesc, pDisc)

            else:
                dup     = False
                err     = ""
                if cde and nam:
                    err = _("Both the product \"Code\" and \"Name\" have already been used for other products.")
                    dup = True
                elif cde:
                    err = _("The product \"Code\" is used for another product before.")
                    dup = True
                elif nam:
                    err = _("The product \"Name\" is used for another product before.")
                    dup = True
                
                if dup:
                    msgbox  = gtk.MessageDialog(self.addProWin, gtk.DIALOG_MODAL,
                                                    gtk.MESSAGE_WARNING,
                                                    gtk.BUTTONS_OK, err)
                    msgbox.set_title(_("Used Data Selected"))
                    msgbox.run()
                    msgbox.destroy()
                    return
                else:
                    self.saveProduct(pCode, pName, pWarn, pOver, pPLoc, pQnty, 
                                        pPurc, pSell, pAccg, pDesc, pDisc)

    #--------------------------------------------------------------------
    # saveProduct():    method to save values in the database.
    #--------------------------------------------------------------------
    def saveProduct(self, code, name, warn, over, pLoc,
                        qnty, purc, sell, accg, desc, disc):
        """ 
        This method is to be used for saving the new products into the database. 
        There is a need for the error and warning messages if the values are having any problem.
        Arguments:
            code    = Code which is entered for the product
            name    = The product's name
            warn    = The least quantity which invokes the warning
            over    = Indicates if we can over-sell the product (even if the quantity is zero)
            pLoc    = Location of the product in the warehouse
            qnty    = Quantity of the product
            purc    = Purchased Price
            sell    = Selling Price
            accg    = Accounting Group
            desc    = Product Description
            disc    = Discount Formula
        Output:
            message to show if the product is saved correctly, under which number, 
        """
        warning     = False
        saveFlg     = True
        warnMsg     = ""
        
        if not over:
            if not qnty:
                warnMsg = _("* \"Quantity\" is not entered or is set to 0. (Over-Sell is off)")
                qnty    = 0
                warning = True
            
        if not purc:
            if warnMsg:
                warnMsg += "\n"
            warnMsg += _("* \"Purchase Price\" is not entered or is set to 0.")
            purc    = 0
            warning = True
            
        if not sell:
            if warnMsg:
                warnMsg += "\n"
            warnMsg += _("* \"Selling Price\" is not entered or is set to 0.")
            sell    = 0
            warning = True
        
        if warning:
            if warnMsg:
                warnMsg += "\n\n The above value(s) will be set to 0."
                warnMsg += " Press \"Ok\" if you want to edit them later"
                warnMsg += " or \"Cancel\" to edit them now."
            msgbox  = gtk.MessageDialog(self.addProWin, 
                                            gtk.DIALOG_MODAL, 
                                            gtk.MESSAGE_INFO, 
                                            gtk.BUTTONS_OK_CANCEL, 
                                            warnMsg)
            msgbox.set_title(_("Warning: Missing Data"))
            answer  = msgbox.run()
            msgbox.destroy()
            if answer == gtk.RESPONSE_OK:
                saveFlg = True
            elif answer == gtk.RESPONSE_CANCEL:
                saveFlg = False
        
        if saveFlg:
            pro     = Products(code, name, warn, over, pLoc, qnty, 
                                purc, sell, accg, desc, disc)
            self.session.add(pro)
            self.session.commit()
            
            parGrpCd    = self.session.query(Groups).select_from(Groups)
            parGrpCd    = parGrpCd.filter(Groups.id == accg).first().code
            if self.proGrpDict.has_key(parGrpCd):
                parIter = self.proGrpDict[ parGrpCd ]
                proIter = self.proListStore.append(parIter, 
                                            (code,name,qnty,purc,sell))
                self.proProDict[ code ] = proIter

            self.cancelAddProduct()
            
    #--------------------------------------------------------------------
    # editProduct():    method to save values in the database.
    #--------------------------------------------------------------------
    def editProduct(self, code, name, warn, over, pLoc,
                        qnty, purc, sell, accg, desc, disc):
        """ 
        This method is to be used for saving the edited products into the database. 
        There is a need for the error and warning messages if the values are having any problem.
        Arguments:
            code    = Code which is entered for the product
            name    = The product's name
            warn    = The least quantity which invokes the warning
            over    = Indicates if we can over-sell the product (even if the quantity is zero)
            pLoc    = Location of the product in the warehouse
            qnty    = Quantity of the product
            purc    = Purchased Price
            sell    = Selling Price
            accg    = Accounting Group
            desc    = Product Description
            disc    = Discount Formula
        Output:
            message to show if the product is saved correctly, under which number, 
        """
        warning     = False
        saveFlg     = True
        warnMsg     = ""
        
        if not over:
            if not qnty:
                warnMsg = _("* \"Quantity\" is not entered or is set to 0. (Over-Sell is off)")
                qnty    = 0
                warning = True
            
        if not purc:
            if warnMsg:
                warnMsg += "\n"
            warnMsg += _("* \"Purchase Price\" is not entered or is set to 0.")
            purc    = 0
            warning = True
            
        if not sell:
            if warnMsg:
                warnMsg += "\n"
            warnMsg += _("* \"Selling Price\" is not entered or is set to 0.")
            sell    = 0
            warning = True
        
        if warning:
            if warnMsg:
                warnMsg += "\n\n The above value(s) will be set to 0."
                warnMsg += " Press \"Ok\" if you want to edit them later"
                warnMsg += " or \"Cancel\" to edit them now."
            msgbox  = gtk.MessageDialog(self.addProWin, 
                                            gtk.DIALOG_MODAL, 
                                            gtk.MESSAGE_INFO, 
                                            gtk.BUTTONS_OK_CANCEL, 
                                            warnMsg)
            msgbox.set_title(_("Warning: Missing Data"))
            answer  = msgbox.run()
            msgbox.destroy()
            if answer == gtk.RESPONSE_OK:
                saveFlg = True
            elif answer == gtk.RESPONSE_CANCEL:
                saveFlg = False
        
        if saveFlg:
            iter    = self.proEditIter
            id      = self.proOldId
            query   = self.session.query(Products).select_from(Products).filter(Products.id==id)
            oldAcId = query.first().accGroup
            newAcId = accg
            updateVals  = {     Products.code : code, 
                                Products.name : name,
                                Products.qntyWarning : warn, 
                                Products.oversell : over, 
                                Products.location : pLoc, 
                                Products.quantity : qnty, 
                                Products.purchacePrice : purc, 
                                Products.sellingPrice : sell, 
                                Products.accGroup : accg, 
                                Products.productDesc : desc, 
                                Products.discountFormula : disc         }

            edit    = query.update(updateVals)
            self.session.commit()
            if oldAcId != newAcId:
                newParCd    = self.session.query(Groups).select_from(Groups)
                newParCd    = newParCd.filter(Groups.id == newAcId).first().code
                newParIter  = self.proGrpDict[newParCd]
                self.proListStore.remove(iter)
                newIter = self.proListStore.append(newParIter, 
                                                (code,name,qnty,purc,sell))
                del self.proProDict[self.oldProCd]
                self.proProDict[ code ] = newIter
                
            else:
                self.proListStore.set(iter, 0,code, 1,name, 2,qnty, 3,purc, 4,sell)
                del self.proProDict[self.oldProCd]
                self.proProDict[ code ] = iter

            self.cancelAddProduct()
            
    #--------------------------------------------------------------------
    # slctAccGrp():    method to call "select accounting group" dialog.
    #--------------------------------------------------------------------
    def slctAccGrp(self, sender  = 0):
        grps_win    = self.viewGroups()
        self.handid = self.connect("group-selected", self.setSelectedID)
        
    #--------------------------------------------------------------------
    # setSelectedID():    method to put the selected accounting group into place
    #--------------------------------------------------------------------
    def setSelectedID(self, sender, id, code):
        self.accGroup.set_text(code)
        self.accGroupCode   = code
        self.accGroupID     = id
        sender.viewGrpWin.destroy()
        self.disconnect(self.handid)
    
    #--------------------------------------------------------------------
    # cancelAddProduct():    method to cancel the product entry.
    #--------------------------------------------------------------------
    def cancelAddProduct(self, sender  = 0, ev = 0):
        self.proCode.destroy()
        self.proQnty.destroy()
        self.accGroup.destroy()
        self.qntyWarning.destroy()
        self.sellingPrice.destroy()
        self.purchasePrice.destroy()
        self.addProWin.hide_all()
        return True

    #--------------------------------------------------------------------
    # viewGroups():    method to create the view groups window
    #--------------------------------------------------------------------
    def viewGroups(self):
        """
        This method will show the groups (only) in a tree view, letting the user
        to view the current entries and edit or delete them, and also select 
        group for the product.
        """
        
        #----- Getting the ui from the file "addProduct.glade" in the data/ui folder.
        self.builder    = get_builder("warehousing")
        self.viewGrpWin = self.builder.get_object("viewGroupsWindow")

        # ------------- OBJECTS OF THE FORM:
        self.groupsTreeView = self.builder.get_object("GroupsTreeView")
        self.grpListStore.clear()
        self.groupsTreeView.set_model(self.grpListStore)          
        
        column      = gtk.TreeViewColumn(_("Code"), 
                                            gtk.CellRendererText(),
                                            text = 0)
        column.set_spacing(5)
        column.set_resizable(True)
        self.groupsTreeView.append_column(column)
        
        column      = gtk.TreeViewColumn(_("Name"), 
                                            gtk.CellRendererText(),
                                            text = 1)
        column.set_spacing(5)
        column.set_resizable(True)
        self.groupsTreeView.append_column(column)
        
        column      = gtk.TreeViewColumn(_("Buy ID"), 
                                            gtk.CellRendererText(),
                                            text = 2)
        column.set_spacing(5)
        column.set_resizable(True)
        self.groupsTreeView.append_column(column)
        
        column      = gtk.TreeViewColumn(_("Sell ID"), 
                                            gtk.CellRendererText(),
                                            text = 3)
        column.set_spacing(5)
        column.set_resizable(True)
        self.groupsTreeView.append_column(column)


        self.groupsTreeView.get_selection().set_mode(gtk.SELECTION_SINGLE)
        
        self.populateGrpList()
        self.viewGrpWin.show_all()
        
        self.builder.connect_signals(self)

    #--------------------------------------------------------------------
    # chkEdit():    Method to check the group before editing in database
    #--------------------------------------------------------------------
    def chkEdit(self, sender = 0):
        selection = self.groupsTreeView.get_selection()
        iter = selection.get_selected()[1]
        
        if iter:
            code = self.grpListStore.get(iter, 0)[0]
            self.editIter       = iter
            query   = self.session.query(Groups).select_from(Groups)
            self.oldId  = query.filter(Groups.code == code).first().id
            self.addGroup(code = code)

    #--------------------------------------------------------------------
    # delGroup():    Method to delete group from the database
    #--------------------------------------------------------------------
    def delGroup(self, sender = 0):
        selection = self.groupsTreeView.get_selection()
        iter = selection.get_selected()[1]
        
        if iter:
            code        = self.grpListStore.get(iter, 0)[0]
            query       = self.session.query(Groups).select_from(Groups)
            deloldId    = query.filter(Groups.code == code).first().id

            chkQuery    = self.session.query(Products).select_from(Products)
            chkChildren = chkQuery.filter(Products.accGroup == deloldId).all()
            if chkChildren:
                msg     = _("Selected Group has some related products and cannot be deleted.")
                msgbox  = gtk.MessageDialog(self.viewGrpWin,
                                                gtk.DIALOG_MODAL,
                                                gtk.MESSAGE_WARNING,
                                                gtk.BUTTONS_OK, msg)
                msgbox.set_title(_("Unable to Delete"))
                msgbox.run()
                msgbox.destroy()
                return
            else:
                msg     = _("Are you sure you want to delete the group \"%s\"") %code
                msgBox  = gtk.MessageDialog(self.viewGrpWin,
                                                gtk.DIALOG_MODAL,
                                                gtk.MESSAGE_QUESTION,
                                                gtk.BUTTONS_OK_CANCEL,
                                                msg)
                msgBox.set_title(_("Are you sure?"))
                answer  = msgBox.run()
                msgBox.destroy()
                if answer == gtk.RESPONSE_OK:
                    query   = self.session.query(Groups).filter(Groups.id == deloldId).first()
                    self.session.delete(query)
                    self.session.commit()
                    self.grpListStore.remove(iter)

    #--------------------------------------------------------------------
    # populateGrpList():    Method to refresh the list
    #--------------------------------------------------------------------
    def populateGrpList(self):
        self.grpListStore.clear()
        query   = self.session.query(Groups).select_from(Groups).order_by(Groups.id.asc())
        self.grpIterDict    = {}
        for group in query:
            selGrp  = self.session.query(Subject).select_from(Subject).filter(group.sellId == Subject.id).first()
            buyGrp  = self.session.query(Subject).select_from(Subject).filter(group.buyId == Subject.id).first()
            selId   = selGrp.code
            buyId   = buyGrp.code
            grp = (group.code, group.name, buyId, selId)
            iter    = self.grpListStore.append(None, grp)
            self.grpIterDict[ str(group.code) ] = iter

    #-----------------------------------------------------
    # addGroup():    Method to add a new Group
    #-----------------------------------------------------
    def addGroup(self, sender = 0, code = 0):
        if code:
            title       = _("Edit Group: %s") %code
            self.editFlg    = True
        else:
            title       = "Add New Group"
            self.editFlg    = False
        
        self.addGrpWindow   = None
        
        self.addGrpWindow   = self.builder.get_object("addGroup")
        self.addGrpWindow.set_title(title)
        
        self.groupCodeEntry     = gtk.Entry()#numberentry.NumberEntry()
        box     = self.builder.get_object("grpCodeHBox")
        box.add(self.groupCodeEntry)
      
        self.groupNameEntry     = self.builder.get_object("groupName")
        
        self.groupSellIDEntry   = gtk.Entry()
        box     = self.builder.get_object("sellIdHBox")
        box.add(self.groupSellIDEntry)

        self.groupBuyIDEntry    = gtk.Entry()
        box     = self.builder.get_object("buyIdHBox")
        box.add(self.groupBuyIDEntry)
        
        self.addGrpWindow.show_all()
        self.builder.connect_signals(self)

        if code:
            query   = self.session.query(Groups).select_from(Groups)
            group   = query.filter(Groups.code == code).first()
            gscd    = self.session.query(Subject).select_from(Subject).filter(Subject.id==group.sellId).first().code
            gbcd    = self.session.query(Subject).select_from(Subject).filter(Subject.id==group.buyId).first().code

            self.groupCodeEntry.set_text(str(group.code))
            self.groupNameEntry.set_text(str(group.name))
            self.groupSellIDEntry.set_text(str(gscd))
            self.groupBuyIDEntry.set_text(str(gbcd))
            
        else:
            self.groupCodeEntry.set_text("")
            self.groupNameEntry.set_text("")
            self.groupSellIDEntry.set_text("")
            self.groupBuyIDEntry.set_text("")

    #--------------------------------------------------------------------
    # chkEntries():    Method to check the data before saving the group
    #--------------------------------------------------------------------
    def chkEntries(self, sender = 0):
        groupCode   = self.groupCodeEntry.get_text()
        groupName   = unicode(self.groupNameEntry.get_text())
        groupSellId = self.groupSellIDEntry.get_text()
        groupBuyId  = self.groupBuyIDEntry.get_text()

        empErr  = False
        errMsg  = ""
        if not groupCode:
            errMsg  += "* Group Code is empty."
            empErr  = True
        if not groupName:
            if errMsg:
                errMsg  += "\n"
            errMsg  += "* Group Name is empty."
            empErr  = True
        if not groupSellId:
            if errMsg:
                errMsg  += "\n"
            errMsg  += "* Group Sell Id is empty."
            empErr  = True
        if not groupBuyId:
            if errMsg:
                errMsg  += "\n"
            errMsg  += "* Group Buy Id is empty."
            empErr  = True
            
        if empErr:
            errMsg  += "\n\nThere should be a valid value for above field(s)."
            msgbox  = gtk.MessageDialog(self.addGrpWindow, 
                                            gtk.DIALOG_MODAL, 
                                            gtk.MESSAGE_WARNING, 
                                            gtk.BUTTONS_OK, 
                                            errMsg)
            msgbox.set_title(_("Data Missing!"))
            msgbox.run()
            msgbox.destroy()
            return
         
        grpSelId    = self.session.query(Subject).select_from(Subject)
        grpSelId    = grpSelId.filter(Subject.code == groupSellId).first()
        if not grpSelId:
            errorstr = _("\"Selling Group ID\" which you selected is not a valid ID.")
            msgbox = gtk.MessageDialog(self.addGrpWindow,
                                            gtk.DIALOG_MODAL,
                                            gtk.MESSAGE_WARNING, 
                                            gtk.BUTTONS_OK, 
                                            errorstr)
            msgbox.set_title(_("Invalid Selling ID"))
            msgbox.run()
            msgbox.destroy()
            return            
        else:
            groupSellId    = grpSelId.id

        grpBuyId    = self.session.query(Subject).select_from(Subject)
        grpBuyId    = grpBuyId.filter(Subject.code == groupBuyId).first()
        if not grpBuyId:
            errorstr = _("\"Buying Group ID\" which you selected is not a valid ID.")
            msgbox = gtk.MessageDialog(self.addGrpWindow,
                                            gtk.DIALOG_MODAL,
                                            gtk.MESSAGE_WARNING, 
                                            gtk.BUTTONS_OK, 
                                            errorstr)
            msgbox.set_title(_("Invalid Buying ID"))
            msgbox.run()
            msgbox.destroy()
            return            
        else:
            groupBuyId  = grpBuyId.id

        if self.editFlg:
            query   = self.session.query(Groups).select_from(Groups)
            codeChk = query.filter(Groups.code == groupCode).first()
            code    = False
            name    = False
            if codeChk:
                if codeChk.id  == self.oldId:
                    code    = False
                else:
                    code    = True
            nameChk = query.filter(Groups.name == groupName).first()
            if nameChk:
                if nameChk.id  == self.oldId:
                    name    = False
                else:
                    name    = True
                    
            dup     = False
            err     = ""
            if code and name:
                err = _("Both the group \"Code\" and \"Name\" have already been used for other groups.")
                dup = True
            elif code:
                err = _("The group \"Code\" is used for another group before.")
                dup = True
            elif name:
                err = _("The group \"Name\" is used for another group before.")
                dup = True
                
            if dup:
                msgbox  = gtk.MessageDialog(self.addGrpWindow,
                                                gtk.DIALOG_MODAL,
                                                gtk.MESSAGE_WARNING,
                                                gtk.BUTTONS_OK, err)
                msgbox.set_title(_("Used Data Selected"))
                msgbox.run()
                msgbox.destroy()
                return
            
            self.editGroup(groupCode, groupName, groupSellId, groupBuyId)

        else:
            query   = self.session.query(Groups).select_from(Groups)
            code    = query.filter(Groups.code == groupCode).first()
            name    = query.filter(Groups.name == groupName).first()
                
            dup     = False
            err     = ""
            if code and name:
                err = _("Both the group \"Code\" and \"Name\" have already been used for other groups.")
                dup = True
            elif code:
                err = _("The group \"Code\" is used for another group before.")
                dup = True
            elif name:
                err = _("The group \"Name\" is used for another group before.")
                dup = True
                
            if dup:
                msgbox  = gtk.MessageDialog(self.addGrpWindow,
                                                gtk.DIALOG_MODAL,
                                                gtk.MESSAGE_WARNING,
                                                gtk.BUTTONS_OK, err)
                msgbox.set_title(_("Used Data Selected"))
                msgbox.run()
                msgbox.destroy()
                return
            
            self.saveGroup(groupCode, groupName, groupSellId, groupBuyId)
            
#        if not self.editFlg:
#            self.saveGroup(groupCode, groupName, groupSellId, groupBuyId)
#        else:
#            self.editGroup(groupCode, groupName, groupSellId, groupBuyId)

    #--------------------------------------------------------------------
    # saveGroup():    Method to save the group information in the database
    #--------------------------------------------------------------------
    def saveGroup(self, code, name, sellId  = 1, buyId   = 2):
        """ 
        This method is to be used for saving the new group into the database. 
        
        Arguments:
            code    = Code which is entered for the group
            name    = The group's name
            sellID  = The selling ID
            buyID   = The buying ID 
        """

        grp     = Groups(code, name, buyId, sellId)
        self.session.add(grp)
        self.session.commit()
        buy     = self.session.query(Subject).select_from(Subject).filter(Subject.id==buyId).first().code
        sell    = self.session.query(Subject).select_from(Subject).filter(Subject.id==sellId).first().code
        grpLS   = (code, name, buy, sell)
        giter   = self.grpListStore.append(None, grpLS)
        piter   = self.proListStore.append(None, 
                                            (code, name, "", "", ""))
        self.grpIterDict[ code ]    = giter
        self.proGrpDict[ code ]     = piter
        self.cancel()
   
    #--------------------------------------------------------------------
    # editGroup():    Method to edit the group in TreeView and database
    #--------------------------------------------------------------------
    def editGroup(self, code, name, sellId  = 1, buyId   = 2):
        """ 
        This method is to be used for saving the edited group into the database. 
        
        Arguments:
            code    = Code which is entered for the group
            name    = The group's name
            sellID  = The selling ID
            buyID   = The buying ID
        """
        iter    = self.editIter
        id      = self.oldId
        query   = self.session.query(Groups).select_from(Groups).filter(Groups.id==id)
        sid     = self.groupSellIDEntry.get_text()
        bid     = self.groupBuyIDEntry.get_text()

        if self.grpIterDict.has_key(str(query.first().code)):
            iter    = self.grpIterDict[ str(query.first().code) ]
            self.grpListStore.set(iter, 0,code, 1,name, 2,bid, 3,sid)
            del self.grpIterDict[ str(query.first().code) ]
            self.grpIterDict[ code ]    = iter

        if self.proGrpDict.has_key(str(query.first().code)):
            proIter = self.proGrpDict[ str(query.first().code) ]
            self.proListStore.set(proIter, 0,code, 1,name)
            del self.proGrpDict[ str(query.first().code) ]
            self.proGrpDict[ code ]    = proIter

        updateVals  = {         Groups.code : code, 
                                Groups.name : name,
                                Groups.sellId : sellId,
                                Groups.buyId : buyId        }
        edit    = query.update(updateVals)
        self.session.commit()

        
#        glst    = [ code, name, bid, sid ]
#        plst    = [ code, name, "", "", "" ]
#        for i in range(len(glst)):
#            print "Groups Row:\t",i,"\tValue:\t",glst[i]
#            self.grpListStore.set_value(iter, i, glst[i])
#        print "============================================"
#        for i in range(len(plst)):
#            print "Products Row:\t",i,"\tValue:\t",plst[i]
#            self.proListStore.set_value(iter, i, plst[i])
        self.cancel()
        
    #--------------------------------------------------------------------
    # cancel():    Method to cancel the adding group
    #--------------------------------------------------------------------
    def cancel(self, sender = 0, ev = 0):
        self.groupCodeEntry.destroy()
        self.groupSellIDEntry.destroy()
        self.groupBuyIDEntry.destroy()
        self.addGrpWindow.hide_all()
        return True
     
    #--------------------------------------------------------------------
    # sellectSellId():    Method to invoke when sellect sell id button is pressed
    #--------------------------------------------------------------------
    def sellectSellId(self, sender  = 0):
        subject_win     = subjects.Subjects()
        code    = self.groupSellIDEntry.get_text()
        if code != '':
            subject_win.highlightSubject(code)
        subject_win.connect("subject-selected", self.sellIdSelected)
        
    #--------------------------------------------------------------------
    # sellIdSelected():    Method to set the sell ID in the entry
    #--------------------------------------------------------------------
    def sellIdSelected(self, sender, id, code, name):
        self.groupSellIDEntry.set_text(code)
        sender.window.destroy()        
    
    #--------------------------------------------------------------------
    # sellectSellId():    Method to invoke when sellect buy id button is pressed
    #--------------------------------------------------------------------
    def sellectBuyId(self, sender  = 0):
        subject_win = subjects.Subjects()
        code = self.groupBuyIDEntry.get_text()
        if code != '':
            subject_win.highlightSubject(code)
        subject_win.connect("subject-selected", self.buyIdSelected)
        
    #--------------------------------------------------------------------
    # buyIdSelected():    Method to set the buy ID in the entry
    #--------------------------------------------------------------------
    def buyIdSelected(self, sender, id, code, name):
        self.groupBuyIDEntry.set_text(code)
        sender.window.destroy()        

    #--------------------------------------------------------------------
    # selectGroupFromList()
    #--------------------------------------------------------------------
    def selectGroupFromList(self, treeview, path, view_column):
        iter = self.grpListStore.get_iter(path)
        code = self.grpListStore.get(iter, 0)[0]
        name = self.grpListStore.get(iter, 1)[0]
        
        query = self.session.query(Groups).select_from(Groups)
        query = query.filter(Groups.code == code)
        grp_id = query.first().id

        self.emit("group-selected", grp_id, code)

    #--------------------------------------------------------------------
    # selectProductFromList()
    #--------------------------------------------------------------------
    def selectProductFromList(self, treeview, path, view_column):
        iter = self.proListStore.get_iter(path)
        code = self.proListStore.get(iter, 0)[0]
        name = self.proListStore.get(iter, 1)[0]
        qnty = self.proListStore.get(iter, 2)[0]

        if qnty:
            query = self.session.query(Products).select_from(Products)
            query = query.filter(Products.code == code)
            pro_id = query.first().id
    
            self.emit("product-selected", pro_id, code)
        else:
            pass        

#----------------------------------------------------------------------
# Creating New Signal to return the selected group when double clicked!
#----------------------------------------------------------------------
gobject.type_register(Warehousing)
gobject.signal_new("group-selected", Warehousing, 
                    gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
                    (gobject.TYPE_INT, gobject.TYPE_STRING))

gobject.signal_new("product-selected", Warehousing, 
                    gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
                    (gobject.TYPE_INT, gobject.TYPE_STRING))
