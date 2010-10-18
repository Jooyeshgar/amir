import  numberentry
import  subjects
import  products
import  gobject
import  pygtk
import  gtk

from    helpers                 import      get_builder
from    sqlalchemy.orm.util     import      outerjoin
from    amirconfig              import      config
from    datetime                import      date
from    database                import      *


###################################################################################
##
## Class ViewGroups:    List All the Groups. 
##
###################################################################################
class ViewGroups(gobject.GObject):
    
    def __init__(   self,   show = True ):
        """
        This class will show the groups (only) in a tree view, letting the user
        to view the current entries and edit or delete them, and also select 
        group for the product.
        """
        
        gobject.GObject.__init__(self)
        
        #----- Getting the ui from the file "addProduct.glade" in the data/ui folder.
        self.builder    = get_builder(                  "warehousing"       )
        self.window     = self.builder.get_object(      "viewGroupsWindow"  )
        self.session    = config.db.session

        # ------------- OBJECTS OF THE FORM:
        self.groupsTreeView = self.builder.get_object(  "GroupsTreeView"    )
        self.grpListStore   = gtk.ListStore(    str,    str,    str,    str )
        self.groupsTreeView.set_model(      self.grpListStore           )          
        
        column      = gtk.TreeViewColumn(   _("Code"), 
                                            gtk.CellRendererText(),
                                            text = 0                )
        column.set_spacing(                 5                       )
        column.set_resizable(               True                    )
        self.groupsTreeView.append_column(  column                  )
        
        column      = gtk.TreeViewColumn(   _("Name"), 
                                            gtk.CellRendererText(),
                                            text = 1                )
        column.set_spacing(                 5                       )
        column.set_resizable(               True                    )
        self.groupsTreeView.append_column(  column                  )
        
        column      = gtk.TreeViewColumn(   _("Buy ID"), 
                                            gtk.CellRendererText(),
                                            text = 2                )
        column.set_spacing(                 5                       )
        column.set_resizable(               True                    )
        self.groupsTreeView.append_column(  column                  )
        
        column      = gtk.TreeViewColumn(   _("Sell ID"), 
                                            gtk.CellRendererText(),
                                            text = 3                )
        column.set_spacing(                 5                       )
        column.set_resizable(               True                    )
        self.groupsTreeView.append_column(  column                  )


        self.groupsTreeView.get_selection().set_mode( gtk.SELECTION_SINGLE )
        self.populateList(                                          )
        if show:
            self.window.show_all(                                   )

        self.addGroupBtn        = self.builder.get_object(      "addGroupsBtn"          )
        self.addGroupBtn.connect(               "clicked",      self.addGroup           )
        self.editBtn            = self.builder.get_object(      "groupEditBtn"          )
        self.editBtn.connect(                   "clicked",      self.edit               )
        self.deleteBtn          = self.builder.get_object(      "deleteGroupBtn"        )
        self.deleteBtn.connect(                 "clicked",      self.delete             )

    #--------------------------------------------------------------------
    # edit():    Method to edit group in the database
    #--------------------------------------------------------------------
    def edit(           self,   sender = 0  ):
        selection = self.groupsTreeView.get_selection(              )
        iter = selection.get_selected()[1]
        
        if iter:
            print "----------------Edit----------------"
            code = self.grpListStore.get(iter, 0)[0]
            self.addGroup(      code  = code                        )

    #--------------------------------------------------------------------
    # delete():    Method to delete group from the database
    #--------------------------------------------------------------------
    def delete(         self,   sender = 0  ):
        print "Delete"

    #--------------------------------------------------------------------
    # populateList():    Method to refresh the list
    #--------------------------------------------------------------------
    def populateList(    self    ):
        self.grpListStore.clear(                                        )
        query   = self.session.query( Groups ).select_from( Groups ).order_by(Groups.id.asc())
        for group in query:
            selGrp  = self.session.query( Subject ).select_from( Subject ).filter(group.sellId == Subject.id).first()
            buyGrp  = self.session.query( Subject ).select_from( Subject ).filter(group.buyId == Subject.id).first()
            selId   = selGrp.code
            buyId   = buyGrp.code
            grp = ( group.code, group.name, buyId, selId )
            self.grpListStore.append(       grp                         )


    #-----------------------------------------------------
    # addGroup():    Method to add a new Group
    #-----------------------------------------------------
    def addGroup(   self,   sender = 0, code = 0  ):
        if code:
            title       = _("Edit Group: %s") %code
        else:
            title       = "Add New Group"
        
        self.addGrpWindow   = self.builder.get_object(  "addGroup"      )
        self.addGrpWindow.set_title(                    title           )
        
        self.addGrpSaveBtn  = self.builder.get_object(  "saveGroup"     )
        self.addGrpSaveBtn.connect(     "clicked",      self.save       )
             
        self.cancelBtn      = self.builder.get_object(  "cancelGroup"   )
        self.cancelBtn.connect(         "clicked",      self.cancel     )
        
        self.groupSelSlctBtn = self.builder.get_object("groupSelSlctBtn")
        self.groupSelSlctBtn.connect(   "clicked",  self.sellectSellId  )
        
        self.groupBuySlctBtn = self.builder.get_object("groupBuySlctBtn")
        self.groupBuySlctBtn.connect(   "clicked",  self.sellectBuyId   )
        
        self.groupCodeEntry     = numberentry.NumberEntry(              )
        box     = self.builder.get_object(              "grpCodeHBox"   )
        box.add(                        self.groupCodeEntry             )
      
        self.groupNameEntry     = self.builder.get_object(  "groupName" )
        
        self.groupSellIDEntry   = numberentry.NumberEntry(              )
        box     = self.builder.get_object(              "sellIdHBox"    )
        box.add(                self.groupSellIDEntry                   )
        print "self.groupSellIDEntry is created:\t",self.groupSellIDEntry
        self.groupBuyIDEntry    = numberentry.NumberEntry(              )
        print "self.groupBuyIDEntry is created:\t",self.groupBuyIDEntry
        box     = self.builder.get_object(              "buyIdHBox"     )
        box.add(                self.groupBuyIDEntry                    )
        
        self.addGrpWindow.show_all(                                         )

        if code:
            query   = self.session.query( Groups ).select_from( Groups  )
            group   = query.filter( Groups.code == code ).first(        )
            gscd    = self.session.query(Subject).select_from(Subject).filter(Subject.id==group.sellId).first().code
            gbcd    = self.session.query(Subject).select_from(Subject).filter(Subject.id==group.buyId).first().code
            print "gscd:\t",gscd
            print "gbcd:\t",gbcd

            self.groupCodeEntry.set_text(   str(group.code)     )
            self.groupNameEntry.set_text(   str(group.name)     )
            self.groupSellIDEntry.set_text( str(gscd)           )
            self.groupBuyIDEntry.set_text(  str(gbcd)       )
            print "Edit:\tself.groupSellIDEntry\t",self.groupSellIDEntry,"\ttext:\t",self.groupSellIDEntry.get_text()
            print "Edit:\tself.groupBuyIDEntry\t",self.groupBuyIDEntry,"\ttext:\t",self.groupBuyIDEntry.get_text()
            
        else:
            self.groupCodeEntry.set_text(   ""              )
            self.groupNameEntry.set_text(   ""              )
            self.groupSellIDEntry.set_text( ""              )
            self.groupBuyIDEntry.set_text(  ""              )

    #--------------------------------------------------------------------
    # save():    Method to check the data before saving the group
    #--------------------------------------------------------------------
    def save(  self,   sender  = 0):
        groupCode   = self.groupCodeEntry.get_text(                     )
        groupName   = unicode(      self.groupNameEntry.get_text()      )
        groupSellId = self.groupSellIDEntry.get_text(                   )
        groupBuyId  = self.groupBuyIDEntry.get_text(                    )

        print "--------------------------------------\nSave method:"
        print "Code:\t",groupCode
        print "Name:\t",groupName
        print "Sell:\t",groupSellId
        print "Buy: \t",groupBuyId

        empErr  = False
        errMsg  = ""
        if not groupName:
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
            msgbox  = gtk.MessageDialog(    self.addGrpWindow, 
                                            gtk.DIALOG_MODAL, 
                                            gtk.MESSAGE_WARNING, 
                                            gtk.BUTTONS_OK, 
                                            errMsg                      )
            msgbox.set_title(               _("Data Missing!")          )
            msgbox.run(                                                 )
            msgbox.destroy(                                             )
            return
         
        grpSelId    = self.session.query(Subject).select_from(Subject)
        grpSelId    = grpSelId.filter(  Subject.code == groupSellId ).first()
        if not grpSelId:
            errorstr = _("\"Selling Group ID\" which you selected is not a valid ID.")
            msgbox = gtk.MessageDialog(     self.addGrpWindow,
                                            gtk.DIALOG_MODAL,
                                            gtk.MESSAGE_WARNING, 
                                            gtk.BUTTONS_OK, 
                                            errorstr                    )
            msgbox.set_title(               _("Invalid Selling ID")     )
            msgbox.run(                                                 )
            msgbox.destroy(                                             )
            return            
        else:
            groupSellId    = grpSelId.id

        grpBuyId    = self.session.query(Subject).select_from(Subject)
        grpBuyId    = grpBuyId.filter(  Subject.code == groupBuyId ).first()
        if not grpBuyId:
            errorstr = _("\"Buying Group ID\" which you selected is not a valid ID.")
            msgbox = gtk.MessageDialog(     self.addGrpWindow,
                                            gtk.DIALOG_MODAL,
                                            gtk.MESSAGE_WARNING, 
                                            gtk.BUTTONS_OK, 
                                            errorstr                        )
            msgbox.set_title(           _("Invalid Buying ID")  )
            msgbox.run(                                                 )
            msgbox.destroy(                                             )
            return            
        else:
            groupBuyId  = grpBuyId.id

        query   = self.session.query(Groups).select_from(Groups)
        code    = query.filter( Groups.code == groupCode ).first(   )
        name    = query.filter( Groups.name == groupName ).first(   )
            
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
            msgbox  = gtk.MessageDialog(    self.addGrpWindow,
                                            gtk.DIALOG_MODAL,
                                            gtk.MESSAGE_WARNING,
                                            gtk.BUTTONS_OK,     err         )
            msgbox.set_title(               _("Used Code Selected")         )
            msgbox.run(                                                     )
            msgbox.destroy(                                                 )
            return
        else:
            self.saveGroup( groupCode, groupName, groupSellId, groupBuyId   )

    #--------------------------------------------------------------------
    # saveGroup():    Method to save the group information in the database
    #--------------------------------------------------------------------
    def saveGroup(    self,   code,   name,   sellId  = 1,    buyId   = 2 ):
        """ 
        This method is to be used for saving the new group into the database. 
        
        Arguments:
            code    = Code which is entered for the group
            name    = The group's name
            sellID  = The selling ID
            buyID   = The buying ID
        Output:
            message to show if the product is saved correctly, under which number, 
        """

        grp     = Groups(           code,   name,   buyId,  sellId      )
        self.session.add(           grp                                 )
        self.session.commit(                                            )
        buy     = self.session.query(Subject).select_from(Subject).filter(Subject.id==buyId).first().code
        sell    = self.session.query(Subject).select_from(Subject).filter(Subject.id==sellId).first().code
        grpLS   = ( code, name, buy, sell )
        self.grpListStore.append(       grpLS                         )
        
        self.cancel()
        return True
   
    #--------------------------------------------------------------------
    # cancel():    Method to cancel the adding group
    #--------------------------------------------------------------------
    def cancel(  self,   sender = 0 ):

        self.groupCodeEntry.destroy()
        self.groupSellIDEntry.destroy()
        self.groupBuyIDEntry.destroy()
        self.addGrpWindow.hide_all()
     
#        for child in childList:
#            print child
#            child.destroy()
#        self.addGrpWindow.destroy() 
    
    #--------------------------------------------------------------------
    # sellectSellId():    Method to invoke when sellect sell id button is pressed
    #--------------------------------------------------------------------
    def sellectSellId(  self,   sender  = 0):
        subject_win     = subjects.Subjects(                            )
        code    = self.groupSellIDEntry.get_text(                       )
        if code != '':
            subject_win.highlightSubject(           code                )
        subject_win.connect(    "subject-selected", self.sellIdSelected )
        
    #--------------------------------------------------------------------
    # sellIdSelected():    Method to set the sell ID in the entry
    #--------------------------------------------------------------------
    def sellIdSelected(self, sender, id, code, name):
        self.groupSellIDEntry.set_text(             code                )
        sender.window.destroy(                                          )        
    
    #--------------------------------------------------------------------
    # sellectSellId():    Method to invoke when sellect buy id button is pressed
    #--------------------------------------------------------------------
    def sellectBuyId(  self,   sender  = 0):
        subject_win = subjects.Subjects()
        code = self.groupBuyIDEntry.get_text()
        if code != '':
            subject_win.highlightSubject(code)
        subject_win.connect(    "subject-selected", self.buyIdSelected  )
        
    #--------------------------------------------------------------------
    # buyIdSelected():    Method to set the buy ID in the entry
    #--------------------------------------------------------------------
    def buyIdSelected(self, sender, id, code, name):
        self.groupBuyIDEntry.set_text(          code                    )
        sender.window.destroy(                                          )        

    def selectGroupFromList(self, treeview, path, view_column):
        print "yoooooohhhhhhhhhhhhhhhhhhhhhhhoooooooooooooo!"
        iter = self.grpListStore.get_iter(path)
        code = self.grpListStore.get(iter, 0)[0]
        name = self.grpListStore.get(iter, 1)[0]
        
        query = self.session.query( Groups ).select_from( Groups )
        query = query.filter(Groups.code == code)
        grp_id = query.first().id
        self.emit("group-selected", grp_id, code, name)
  

gobject.type_register(                          ViewGroups              )
gobject.signal_new( "group-selected",           ViewGroups, 
                    gobject.SIGNAL_RUN_LAST,    gobject.TYPE_NONE, 
                    (gobject.TYPE_INT,          gobject.TYPE_STRING,
                    gobject.TYPE_STRING)                                )


####################################################################################
###
### Class AddGroup:    Adds product groups to the warehousing system. 
###
####################################################################################
#class AddGroup:
#    
#    #--------------------------------------------------------------------
#    # initializing Method()
#    #--------------------------------------------------------------------
#    def __init__(   self,   id  = 0,    list    = None  ):
#        if list:
#            grp = ( "12", "12_name", "01", "02"   )
#            list.append(       grp                         )
#        self.session    = config.db.session
#        if id:
#            query       = self.session.query(Groups).select_from(Groups)
#            group       = query.filter(Groups.id == id).all(            )
#            title       = _("Edit Group: %s") %id # id Must change to the code of the group
#        else:
#            title       = "Add Group"
#        self.builder    = get_builder(                  "warehousing"   )
#        
#        self.window     = self.builder.get_object(      "addGroup"      )
#        self.window.set_title(                          title           )
#        self.window.show_all(                                           )
#        
#        self.addGrpSaveBtn  = self.builder.get_object(  "saveGroup"     )
#        self.addGrpSaveBtn.connect(     "clicked",      self.save       )
#             
#        self.cancelBtn      = self.builder.get_object(  "cancelGroup"   )
#        self.cancelBtn.connect(         "clicked",      self.cancel     )
#        
#        self.groupSelSlctBtn = self.builder.get_object("groupSelSlctBtn")
#        self.groupSelSlctBtn.connect(   "clicked",  self.sellectSellId  )
#        
#        self.groupBuySlctBtn = self.builder.get_object("groupBuySlctBtn")
#        self.groupBuySlctBtn.connect(   "clicked",  self.sellectBuyId   )
#        
#        self.groupCodeEntry     = numberentry.NumberEntry(              )
#        box     = self.builder.get_object(              "grpCodeHBox"   )
#        box.add(                        self.groupCodeEntry             )
#        self.groupCodeEntry.show(                                       )
#        
#        self.groupNameEntry     = self.builder.get_object(  "groupName" )
#        self.groupSellIDEntry   = numberentry.NumberEntry(              )
#        box     = self.builder.get_object(              "sellIdHBox"    )
#        box.add(                self.groupSellIDEntry                   )
#        self.groupSellIDEntry.show(                                     ) 
#        self.groupBuyIDEntry    = numberentry.NumberEntry(              )
#        box     = self.builder.get_object(              "buyIdHBox"     )
#        box.add(                self.groupBuyIDEntry                    )
#        self.groupBuyIDEntry.show(                                      )
#        
#
#    #--------------------------------------------------------------------
#    # save():    Method to check the data before saving the group
#    #--------------------------------------------------------------------
#    def save(  self,   sender  = 0):
#        groupCode   = self.groupCodeEntry.get_text(                     )
#        groupName   = unicode(      self.groupNameEntry.get_text()      )
#        groupSellId = self.groupSellIDEntry.get_text(                   )
#        groupBuyId  = self.groupBuyIDEntry.get_text(                    )
#
#        empErr  = False
#        errMsg  = ""
#        if not groupName:
#            errMsg  += "* Group Name is empty."
#            empErr  = True
#        if not groupSellId:
#            if errMsg:
#                errMsg  += "\n"
#            errMsg  += "* Group Sell Id is empty."
#            empErr  = True
#        if not groupBuyId:
#            if errMsg:
#                errMsg  += "\n"
#            errMsg  += "* Group Buy Id is empty."
#            empErr  = True
#            
#        if empErr:
#            errMsg  += "\n\nThere should be a valid value for above field(s)."
#            msgbox  = gtk.MessageDialog(        self.window, 
#                                                gtk.DIALOG_MODAL, 
#                                                gtk.MESSAGE_WARNING, 
#                                                gtk.BUTTONS_OK, 
#                                                errMsg                  )
#            msgbox.set_title(                   _("Data Missing!")      )
#            msgbox.run(                                                 )
#            msgbox.destroy(                                             )
#            return
#         
#        grpSelId    = self.session.query(Subject).select_from(Subject)
#        grpSelId    = grpSelId.filter(  Subject.code == groupSellId ).first()
#        if not grpSelId:
#            errorstr = _("\"Selling Group ID\" which you selected is not a valid ID.")
#            msgbox = gtk.MessageDialog( self.window,
#                                            gtk.DIALOG_MODAL,
#                                            gtk.MESSAGE_WARNING, 
#                                            gtk.BUTTONS_OK, 
#                                            errorstr                        )
#            msgbox.set_title(           _("Invalid Selling ID")  )
#            msgbox.run(                                                 )
#            msgbox.destroy(                                             )
#            return            
#        else:
#            groupSellId    = grpSelId.id
#
#        grpBuyId    = self.session.query(Subject).select_from(Subject)
#        grpBuyId    = grpBuyId.filter(  Subject.code == groupBuyId ).first()
#        print grpBuyId
#        print grpBuyId.id,"---",grpBuyId.code,"---",grpBuyId.name
#        print "------------------------------"
#        return
#        if not grpBuyId:
#            errorstr = _("\"Buying Group ID\" which you selected is not a valid ID.")
#            msgbox = gtk.MessageDialog( self.window,
#                                            gtk.DIALOG_MODAL,
#                                            gtk.MESSAGE_WARNING, 
#                                            gtk.BUTTONS_OK, 
#                                            errorstr                        )
#            msgbox.set_title(           _("Invalid Buying ID")  )
#            msgbox.run(                                                 )
#            msgbox.destroy(                                             )
#            return            
#        else:
#            groupBuyId  = grpBuyId.id
#
#
#        query   = self.session.query(Groups).select_from(Groups)
#        code    = query.filter( Groups.code == groupCode ).first(   )
#        name    = query.filter( Groups.name == groupName ).first(   )
#            
#        dup     = False
#        err     = ""
#        if code and name:
#            err = _("Both the group \"Code\" and \"Name\" have already been used for other groups.")
#            dup = True
#        elif code:
#            err = _("The group \"Code\" is used for another group before.")
#            dup = True
#        elif name:
#            err = _("The group \"Name\" is used for another group before.")
#            dup = True
#            
#        if dup:
#            msgbox  = gtk.MessageDialog(    self.window,    gtk.DIALOG_MODAL,
#                                            gtk.MESSAGE_WARNING,
#                                            gtk.BUTTONS_OK,     err         )
#            msgbox.set_title(               _("Used Code Selected")         )
#            msgbox.run(                                                     )
#            msgbox.destroy(                                                 )
#            return
#        else:
#            self.saveGroup( groupCode, groupName, groupSellId, groupBuyId   )
#
#    #--------------------------------------------------------------------
#    # saveGroup():    Method to save the group information in the database
#    #--------------------------------------------------------------------
#    def saveGroup(    self,   code,   name,   sellId  = 1,    buyId   = 2 ):
#        """ 
#        This method is to be used for saving the new group into the database. 
#        
#        Arguments:
#            code    = Code which is entered for the group
#            name    = The group's name
#            sellID  = The selling ID
#            buyID   = The buying ID
#        Output:
#            message to show if the product is saved correctly, under which number, 
#        """
#
#        grp     = Groups(   code,   name,   buyId,  sellId                  )
#        self.session.add(           grp                                     )
#        self.session.commit(                                                )
#        
#        self.window.destroy(                                                )
#        return True
#   
#    #--------------------------------------------------------------------
#    # cancel():    Method to cancel the adding group
#    #--------------------------------------------------------------------
#    def cancel(  self,   sender = 0 ):
#        self.window.destroy()
#        
#    
#    #--------------------------------------------------------------------
#    # sellectSellId():    Method to invoke when sellect sell id button is pressed
#    #--------------------------------------------------------------------
#    def sellectSellId(  self,   sender  = 0):
#        subject_win = subjects.Subjects()
#        code = self.groupSellIDEntry.get_text()
#        if code != '':
#            subject_win.highlightSubject(code)
#        subject_win.connect(    "subject-selected", self.sellIdSelected )
#        
#    #--------------------------------------------------------------------
#    # sellIdSelected():    Method to set the sell ID in the entry
#    #--------------------------------------------------------------------
#    def sellIdSelected(self, sender, id, code, name):
#        self.groupSellIDEntry.set_text(code)
#        sender.window.destroy(                                          )        
#    
#    #--------------------------------------------------------------------
#    # sellectSellId():    Method to invoke when sellect buy id button is pressed
#    #--------------------------------------------------------------------
#    def sellectBuyId(  self,   sender  = 0):
#        subject_win = subjects.Subjects()
#        code = self.groupBuyIDEntry.get_text()
#        if code != '':
#            subject_win.highlightSubject(code)
#        subject_win.connect(    "subject-selected", self.buyIdSelected  )
#        
#    #--------------------------------------------------------------------
#    # buyIdSelected():    Method to set the buy ID in the entry
#    #--------------------------------------------------------------------
#    def buyIdSelected(self, sender, id, code, name):
#        self.groupBuyIDEntry.set_text(          code                    )
#        sender.window.destroy(                                          )        
