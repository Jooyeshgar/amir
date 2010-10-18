import  numberentry
import  subjects
import  gobject
import  groups
import  pygtk
import  gtk

from    helpers                 import      get_builder
from    sqlalchemy.orm.util     import      outerjoin
from    amirconfig              import      config
from    datetime                import      date
from    database                import      *


###################################################################################
##
## Class ViewProducts:    Displays all the warehousing registered products. 
##
###################################################################################
class ViewProducts:
        
    #--------------------------------------------------------------------
    #    initializing method
    #--------------------------------------------------------------------
    def __init__(   self,   number = 0  ):
        """
        This class will show the products and groups in a tree view, letting the user
        to view the current entries and edit or delete them.
        """
        
        #----- Getting the ui from the file "addProduct.glade" in the data/ui folder.
        self.builder    = get_builder(                  "warehousing"           )
        self.window     = self.builder.get_object(      "viewProductsWindow"    )
        self.session    = config.db.session
        
        # ------------- OBJECTS OF THE FORM:
        self.productTreeView    = self.builder.get_object(  "productsTreeView"  )
        self.proListStore  = gtk.ListStore(    str,    str,    int,    int,    int         )

        #=================================================================================
        query   = self.session.query(   Products    ).select_from(  Products    ).order_by(Products.id.desc())
        for row in query:
            self.proListStore.append((row.code,row.name,row.quantity,row.purchacePrice,row.sellingPrice))
        #=================================================================================
        
        column      = gtk.TreeViewColumn(   _("Code"), 
                                            gtk.CellRendererText(),
                                            text = 0                )
        column.set_spacing(                 5                       )
        column.set_resizable(               True                    )
        self.productTreeView.append_column( column                  )
        
        column      = gtk.TreeViewColumn(   _("Name"), 
                                            gtk.CellRendererText(),
                                            text = 1                )
        column.set_spacing(                 5                       )
        column.set_resizable(               True                    )
        self.productTreeView.append_column( column                  )
        
        column      = gtk.TreeViewColumn(   _("Quantity"), 
                                            gtk.CellRendererText(),
                                            text = 2                )
        column.set_spacing(                 5                       )
        column.set_resizable(               True                    )
        self.productTreeView.append_column( column                  )
        
        column      = gtk.TreeViewColumn(   _("Purchase Price"), 
                                            gtk.CellRendererText(),
                                            text = 3                )
        column.set_spacing(                 5                       )
        column.set_resizable(               True                    )
        self.productTreeView.append_column( column                  )

        column      = gtk.TreeViewColumn(   _("Selling Price"), 
                                            gtk.CellRendererText(),
                                            text = 4                )
        column.set_spacing(                 5                       )
        column.set_resizable(               True                    )
        self.productTreeView.append_column( column                  )

        columnsInSetting    = 0
        # Later we can read this from the setting, which helps us show the needed values of the user
        
        if columnsInSetting: 
            column  = gtk.TreeViewColumn(   _("Accounting Group"), 
                                            gtk.CellRendererText(),     
                                            text = 5                )
            column.set_spacing(             5                       )
            column.set_resizable(           True                    )
            self.productTreeView.append_column(     column          )
    
            column  = gtk.TreeViewColumn(   _("Product Location"), 
                                            gtk.CellRendererText(),
                                            text = 6                )
            column.set_spacing(             5                       )
            column.set_resizable(           True                    )
            self.productTreeView.append_column(     column          )
            
            column  = gtk.TreeViewColumn(   _("Quantity Warning"),
                                            gtk.CellRendererText(),
                                            text = 7                )
            column.set_spacing(             5                       )
            column.set_resizable(           True                    )
            self.productTreeView.append_column(     column          )
    
            column  = gtk.TreeViewColumn(   _("Over-Sell"), 
                                            gtk.CellRendererText(),
                                            text = 8                )
            column.set_spacing(             5                       )
            column.set_resizable(           True                    )
            self.productTreeView.append_column(     column          )
    
            column  = gtk.TreeViewColumn(   _("Discount Formula"), 
                                            gtk.CellRendererText(),
                                            text = 9                )
            column.set_spacing(             5                       )
            column.set_resizable(           True                    )
            self.productTreeView.append_column(     column          )
    
            column  = gtk.TreeViewColumn(   _("Description"), 
                                            gtk.CellRendererText(),
                                            text = 10               )
            column.set_spacing(             5                       )
            column.set_resizable(           True                    )
            self.productTreeView.append_column(     column          )


        self.productTreeView.get_selection().set_mode(  gtk.SELECTION_SINGLE    )
        self.productTreeView.set_model(     self.proListStore       )
        self.window.show_all(                                       )
        

        self.addProductBtn      = self.builder.get_object(      "addProductBtn"         )
        self.addProductBtn.connect(             "clicked",      self.addNewProduct      )
        self.addGroupBtn        = self.builder.get_object(      "addGroupBtn"           )
        self.addGroupBtn.connect(               "clicked",      self.addGroup           )
        self.editBtn            = self.builder.get_object(      "editBtn"               )
        self.editBtn.connect(                   "clicked",      self.edit               )
        self.deleteBtn          = self.builder.get_object(      "deleteBtn"             )
        self.deleteBtn.connect(                 "clicked",      self.delete             )

    #--------------------------------------------------------------------
    # addNewProduct():    Method to open the "Add Product" dialog
    #--------------------------------------------------------------------
    def addNewProduct(  self,   sender = 0  ):
        product         = AddNewProduct(                                                )
        
    #--------------------------------------------------------------------
    # addGroup():    Method to open the "Add Group" dialog
    #--------------------------------------------------------------------
    def addGroup(       self,   sender = 0  ):
        group           = groups.AddGroup(                                              )
        
    #--------------------------------------------------------------------
    # edit():    Method to edit group/product in the database
    #--------------------------------------------------------------------
    def edit(           self,   sender = 0  ):
        print "Edit"
        
    #--------------------------------------------------------------------
    # delete():    Method to delete group/product from the database
    #--------------------------------------------------------------------
    def delete(         self,   sender = 0  ):
        print "Delete"


###################################################################################
##
## Class AddNewProduct:    Adds products to the warehousing system
##
###################################################################################
class AddNewProduct:
        
    #--------------------------------------------------------------------
    #    initializing method
    #--------------------------------------------------------------------
    def __init__(   self    ):
        """
        Class AddNewProduct:
        This class is creating a user interface for the client to add products
        to the warehousing system. User needs to fill the data into the form and
        the dialog will check the data and save them into database if it is OK.
        
        """
        #----- Getting the ui from the file "addProduct.glade" in the data/ui folder.
        self.builder    = get_builder(                  "warehousing"       )
        self.window     = self.builder.get_object(      "addProductWindow"  )
        self.window.show_all(                                               )
        
        self.session    = config.db.session

        # ------------- OBJECTS OF THE FORM:
        #self.accGrp     = self.builder.get_object(      "accGroup"          )
        self.slctBtn    = self.builder.get_object(      "slctBtn"           )
        self.proLoc     = self.builder.get_object(      "proLoc"            )
        
        self.proCode    = numberentry.NumberEntry(                          )
        box             = self.builder.get_object(      "proCodeHBox"       )
        box.add(        self.proCode                                        )
        self.proCode.show(                                                  )
        
        self.proName    = self.builder.get_object(      "proName"           )
        self.proDesc    = self.builder.get_object(      "proDesc"           )
        
        self.proQnty    = numberentry.NumberEntry(                          ) 
        box             = self.builder.get_object(      "qntyHBox"          )
        box.add(                                        self.proQnty        )
        self.proQnty.show(                                                  )
        
        self.accGroup   = numberentry.NumberEntry(                          )
        box             = self.builder.get_object(      "accGrpHBox"        )
        box.add(                                        self.accGroup       )
        self.accGroup.show(                                                 )
        
        self.oversell   = self.builder.get_object(      "oversell"          )
        self.discFormula    = self.builder.get_object(  "discFormula"       )
        self.qntyWarning    = numberentry.NumberEntry(                      )
        box                 = self.builder.get_object(  "qntyWrnHBox"       )
        box.add(                                        self.qntyWarning    )
        self.qntyWarning.show(                                              )
        
        self.sellingPrice   = numberentry.NumberEntry(                      )
        box                 = self.builder.get_object(  "sellPriceHBox"     )
        box.add(                                        self.sellingPrice   )
        self.sellingPrice.show(                                             )
        
        self.purchasePrice  = numberentry.NumberEntry(                      )
        box                 = self.builder.get_object(  "purchPriceHBox"    )
        box.add(                                        self.purchasePrice  )
        self.purchasePrice.show(                                            )
        
        self.saveBtn    = self.builder.get_object(  "saveBtn"               )
        self.canclBtn   = self.builder.get_object(  "cancelBtn"             )
        self.slctBtn    = self.builder.get_object(  "slctBtn"               )
        self.saveBtn.connect(   "clicked",          self.save               )
        self.canclBtn.connect(  "clicked",          self.cancelAddProduct   )
        self.slctBtn.connect(   "clicked",          self.slctAccGrp         )
        
            
    #--------------------------------------------------------------------
    # save():    method to invoke when Save Button is pressed.
    #--------------------------------------------------------------------
    def save(   self,   sender  = 0     ):
        code    = self.proCode.get_text(                                    )
        name    = unicode(                      self.proName.get_text()     )
        warn    = self.qntyWarning.get_int(                                 )
        over    = self.oversell.get_active(                                 )
        pLoc    = unicode(                      self.proLoc.get_text()      )
        qnty    = self.proQnty.get_int(                                     )
        purc    = self.purchasePrice.get_int(                               )
        sell    = self.sellingPrice.get_int(                                )
        accc    = self.accGroup.get_text(                                   )
        desc    = unicode(                      self.proDesc.get_text()     )
        disc    = unicode(                      self.discFormula.get_text() )
        if not code:
            errorstr = _("There must be a \"Code\" saved for each product.")
            msgbox = gtk.MessageDialog(         self.window,
                                                gtk.DIALOG_MODAL, 
                                                gtk.MESSAGE_WARNING,    
                                                gtk.BUTTONS_OK, 
                                                errorstr                    )
            msgbox.set_title(                   _("Missing Data")           )
            msgbox.run(                                                     )
            msgbox.destroy(                                                 )
            return
        elif not name:
            errorstr = _("There is no \"Name\" mentioned for this product.")
            msgbox = gtk.MessageDialog(         self.window,
                                                gtk.DIALOG_MODAL,
                                                gtk.MESSAGE_WARNING,
                                                gtk.BUTTONS_OK,
                                                errorstr                    )
            msgbox.set_title(                   _("Missing Data")           )
            msgbox.run(                                                     )
            msgbox.destroy(                                                 )
            return
        elif not accc:
            errorstr = _("Please sellect one \"Accounting Group\" for this product.")
            msgbox = gtk.MessageDialog(         self.window,
                                                gtk.DIALOG_MODAL,
                                                gtk.MESSAGE_WARNING, 
                                                gtk.BUTTONS_OK, 
                                                errorstr)
            msgbox.set_title(                   _("Missing Data")           )
            msgbox.run(                                                     )
            msgbox.destroy(                                                 )
            return            
        else:
            query   = self.session.query(Products).select_from(Products)
            cde     = query.filter( Products.code == code ).first(          )
            nam     = query.filter( Products.name == name ).first(          )
            
            acgQ    = self.session.query(Groups).select_from(Groups)
            acgQ    = acgQ.filter(  Groups.code == accc ).first()
            if not acgQ:
                errorstr = _("\"Accounting Group\" which you selected does not exist.")
                msgbox = gtk.MessageDialog( self.window,
                                            gtk.DIALOG_MODAL,
                                            gtk.MESSAGE_WARNING, 
                                            gtk.BUTTONS_OK, 
                                            errorstr                        )
                msgbox.set_title(           _("Wrong Accounting Group ID")  )
                msgbox.run(                                                 )
                msgbox.destroy(                                             )
                return            
            else:
                accg    = acgQ.id
             
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
                msgbox  = gtk.MessageDialog(    self.window,    gtk.DIALOG_MODAL,
                                                gtk.MESSAGE_WARNING,
                                                gtk.BUTTONS_OK,     err         )
                msgbox.set_title(               _("Used Code Selected")         )
                msgbox.run(                                                     )
                msgbox.destroy(                                                 )
                return
            else:
                self.saveProduct(  code,   name,   warn,   over,   pLoc,    qnty,   
                                   purc,   sell,   accg,   desc,   disc         )

    #--------------------------------------------------------------------
    # saveProduct():    method to save values in the database.
    #--------------------------------------------------------------------
    def saveProduct(    self,   code,   name,   warn,   over,   pLoc,
                        qnty,   purc,   sell,   accg,   desc,   disc    ):
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
            msgbox  = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK_CANCEL, warnMsg)
            msgbox.set_title(_("Warning: Missing Data"))
            answer  = msgbox.run(                           )
            msgbox.destroy(                                 )
            if answer == gtk.RESPONSE_OK:
                saveFlg = True
            elif answer == gtk.RESPONSE_CANCEL:
                saveFlg = False
        
        if saveFlg:
            pro    = Products( code,   name,   warn,   over,   pLoc,   qnty, 
                               purc,   sell,   accg,   desc,   disc         )
            self.session.add(           pro                                 )
            self.session.commit(                                            )

            self.window.destroy(                                            )


    #--------------------------------------------------------------------
    # slctAccGrp():    method to call "select accounting group" dialog.
    #--------------------------------------------------------------------
    def slctAccGrp(         self,   sender  = 0     ):
        grps_win = groups.ViewGroups(                                    )
#        code        = self.accGroup.get_text(                               )
#        if code != '':
#            subject_win.highlightSubject(               code                )
        grps_win.connect(    "group-selected",     self.setSelectedID  )
        
    #--------------------------------------------------------------------
    # slctAccGrp():    method to call "select accounting group" dialog.
    #--------------------------------------------------------------------
    def setSelectedID(  self,   sender,     id,     code,   name    ):
        self.accGroup.set_text(                     code                )
        self.accGroupCode   = code
        self.accGroupID     = id
        self.accGroupName   = name
        sender.window.destroy(                                          )        
    
    #--------------------------------------------------------------------
    # cancelAddProduct():    method to cancel the product entry.
    #--------------------------------------------------------------------
    def cancelAddProduct(   self,   sender  = 0     ):
        self.window.destroy(                                            )
        
