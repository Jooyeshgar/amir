import  numberentry
import  dateentry
import  subjects
import  utility

import  gobject
import  pygtk
import  gtk

from    sqlalchemy.orm              import  sessionmaker, join
from    sqlalchemy.orm.util         import  outerjoin
from    sqlalchemy.orm.query        import  aliased
from    sqlalchemy.sql              import  and_, or_
from    sqlalchemy.sql.functions    import  *

from    helpers                     import  get_builder
from    amirconfig                  import  config
from    datetime                    import  date
from    database                    import  *

pygtk.require('2.0')

class ProductGroup(gobject.GObject):
    
    def __init__(self):
        gobject.GObject.__init__(self)
        
        self.builder    = get_builder("warehousing" )
        self.window = None
        self.treestore = None
        
        self.grpCodeEntry = numberentry.NumberEntry()
        box = self.builder.get_object("grpCodeBox")
        box.add(self.grpCodeEntry)
        self.grpCodeEntry.show()
        
        self.sellCodeEntry = numberentry.NumberEntry()
        box = self.builder.get_object("sellCodeBox")
        box.add(self.sellCodeEntry)
        self.sellCodeEntry.show()
        self.sellCodeEntry.connect("activate", self.selectSellingSubject)
        self.sellCodeEntry.set_tooltip_text(_("Press Enter to see available subjects."))
        
        self.buyCodeEntry = numberentry.NumberEntry()
        box = self.builder.get_object("buyCodeBox")
        box.add(self.buyCodeEntry)
        self.buyCodeEntry.show()
        self.buyCodeEntry.connect("activate", self.selectBuyingSubject)
        self.buyCodeEntry.set_tooltip_text(_("Press Enter to see available subjects."))
        
        self.builder.connect_signals(self)
    
            
    def viewProductGroups(self):
        self.window = self.builder.get_object("viewProGroupsWindow")
        
        self.treeview = self.builder.get_object("GroupsTreeView")
        self.treestore = gtk.TreeStore(str, str, str)
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
        
        column = gtk.TreeViewColumn(_("Buy ID"), gtk.CellRendererText(), text = 2)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        
        column = gtk.TreeViewColumn(_("Sell ID"), gtk.CellRendererText(), text = 3)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        
        self.treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        self.treestore.set_sort_column_id(0, gtk.SORT_ASCENDING)
        
        #Fill groups treeview
        query = config.db.session.query(ProductGroups).select_from(ProductGroups)
        result = query.all()
        
        for group in result:
	    code = group.code
	    buyId = group.buyId
	    sellId = group.sellId
            if config.digittype == 1:
                code = utility.convertToPersian(code)
                buyId = utility.convertToPersian(buyId)
                sellId = utility.convertToPersian(sellId)
            self.treestore.append(None, (code, group.name, buyId, sellId))
            
        self.window.show_all()
        
    def addProductGroup(self, sender):
        dialog = self.builder.get_object("addProductGroupDlg")
        dialog.set_title(_("Add new group"))
        self.grpCodeEntry.set_text("")
        self.builder.get_object("groupNameEntry").set_text("")
        self.buyCodeEntry.set_text("")
        self.sellCodeEntry.set_text("")
        
        result = dialog.run()
        if result == 1:
            grpcode = self.grpCodeEntry.get_text()
            grpname = self.builder.get_object("groupNameEntry").get_text()
            grpbuycode = self.buyCodeEntry.get_text()
            grpsellcode = self.sellCodeEntry.get_text()
            self.saveProductGroup(grpcode, unicode(grpname), grpbuycode, grpsellcode, None)
                
        dialog.hide()
    
    def editProductGroup(self, sender):
        dialog = self.builder.get_object("addProductGroupDlg")
        dialog.set_title(_("Edit group"))
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        
        if iter != None :
	    grpcode = self.treestore.get(iter, 0)[0]
            if config.digittype == 1:
                code = utility.convertToLatin(grpcode)
            else:
                code = grpcode
                
            BuySub = aliased(Subject, name="bs")
            SellSub = aliased(Subject, name="ss")
            
            query = config.db.session.query(ProductGroups, BuySub.code, SellSub.code)
            query = query.select_from( outerjoin( outerjoin(ProductGroups, BuySub, ProductGroups.buyId == BuySub.id),
                                                  SellSub, ProductGroups.sellId == SellSub.id ) )
            (group, buy_code, sell_code) = query.filter(ProductGroups.code == code).first()
            name = group.name
            if config.digittype == 1:
		buy_code = utility.convertToPersian(buy_code)
		sell_code = utility.convertToPersian(sell_code)
            
            self.grpCodeEntry.set_text(grpcode)
            self.builder.get_object("groupNameEntry").set_text(name)
            self.buyCodeEntry.set_text(buy_code)
            self.sellCodeEntry.set_text(sell_code)
            
            result = dialog.run()
            if result == 1:
                grpcode = self.grpCodeEntry.get_text()
                grpname = self.builder.get_object("groupNameEntry").get_text()
                grpbuycode = self.buyCodeEntry.get_text()
		grpsellcode = self.sellCodeEntry.get_text()
                self.saveProductGroup(grpcode, unicode(grpname), grpbuycode, grpsellcode, iter)
                
            dialog.hide()
                
    def deleteProductGroup(self, sender):
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        if iter != None :
            code = utility.convertToLatin(self.treestore.get(iter, 0)[0])
            
            query = config.db.session.query(ProductGroups, count(Products.id))
            query = query.select_from(outerjoin(ProductGroups, Products, ProductGroups.id == Products.accGroup))
            result = query.filter(ProductGroups.code == code).first()
            
            if result[1] != 0 :
                msgbox =  gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE,
                                    _("Group can not be deleted, Because there are some products registered in it."))
                msgbox.set_title(_("Error deleting group"))
                msgbox.run()
                msgbox.destroy()
            else :
                group = result[0]
                config.db.session.delete(group)
                config.db.session.commit()
                self.treestore.remove(iter)
    
    #@param edititer: None if a new product group is to be saved.
    #                 Otherwise it stores the TreeIter for the group that's been edited.
    def saveProductGroup(self, code, name, buy_code, sell_code, edititer=None):
        msg = "";
        if name == "":
            msg = _("Group name should not be empty")
        elif code == "":
            msg = _("Group code should not be empty")
        #TODO set default values for buyid & sellid if empty
            
        if msg != "":
            msgbox =  gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE, msg)
            msgbox.set_title(_("Empty fields"))
            msgbox.run()
            msgbox.destroy()
            return
        
        if edititer != None:
            pcode = self.treestore.get_value(edititer, 0)
            pcode = utility.convertToLatin(pcode)
            query = config.db.session.query(ProductGroups).select_from(ProductGroups)
            group = query.filter(ProductGroups.code == pcode).first()
            gid = group.id
        
        code = utility.convertToLatin(code)
        buy_code = utility.convertToLatin(buy_code)
        sell_code = utility.convertToLatin(sell_code)
        
        #Checks if the group name or code is repeated.
        query = config.db.session.query(ProductGroups).select_from(ProductGroups)
        query = query.filter(or_(ProductGroups.code == code, ProductGroups.name == name))
        if edititer != None:
            query = query.filter(ProductGroups.id != gid)
        result = query.all()
        msg = ""
        for grp in result:
            if grp.code == code:
                msg += _("A group with this code already exists.\n")
                break
            elif grp.name == name:
                msg += _("A group with this name already exists.\n")
                break
        
        #Check if buy_code & sell_code are valid
        #TODO Check if buying subject is creditor/debtor, and so for selling one.
        query = config.db.session.query(Subject).select_from(Subject)
        buy_sub = query.filter(Subject.code == buy_code).first()
        if buy_sub == None:
	    msg += _("Buying code is not valid.\n")
        
        query = config.db.session.query(Subject).select_from(Subject)
        sell_sub = query.filter(Subject.code == sell_code).first()
        if sell_sub == None:
	    msg += _("Selling code is not valid.\n")
	    
        if msg != "":
            msgbox =  gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, msg)
            msgbox.set_title(_("Invalid group properties"))
            msgbox.run()
            msgbox.destroy()
            return
            
        if edititer == None:
            group = ProductGroups(code, name, buy_sub.id, sell_sub.id)
            
            edititer = self.treestore.append(None)
            path = self.treestore.get_path(edititer)
            self.treeview.scroll_to_cell(path, None, False, 0, 0)
            self.treeview.set_cursor(path, None, False)
        else:
            group.code = code
            group.name = name
            group.buyId = buy_sub.id
            group.sellId = sell_sub.id
            
        config.db.session.add(group)
        config.db.session.commit()
        
        if config.digittype == 1:
            code = utility.convertToPersian(code)
            buy_code = utility.convertToPersian(buy_code)
            sell_code = utility.convertToPersian(sell_code)
        self.saveRow(edititer, (code, name, buy_code, sell_code))
        
        
    #@param treeiter: the TreeIter which data should be saved in
    #@param data: a tuple containing data to be saved
    def saveRow(self, treeiter, data):
        self.treestore.set(treeiter, 0, data[0], 1, data[1], 2, data[2], 3, data[3])
    
    #def highlightGroup(self, code):
##        code = code.decode('utf-8')
        #iter = self.treestore.get_iter_first()
        #pre = iter
        
        #while iter:
##            res = self.match_func(iter, (0, part))
            #itercode = self.treestore.get_value(iter, 0)
            #if  itercode < code:
                #pre = iter
                #iter = self.treestore.iter_next(iter)
            #elif itercode == code:
                #break
            #else:
                #iter = pre
                #break

        #if not iter:
            #iter = pre
            
        #if iter:
            #path = self.treestore.get_path(iter)
            #self.treeview.scroll_to_cell(path, None, False, 0, 0)
            #self.treeview.set_cursor(path, None, False)
            #self.treeview.grab_focus()
            
    
    #def selectCustGroupFromList(self, treeview, path, view_column):
        #iter = self.treestore.get_iter(path)
        #code = utility.convertToLatin(self.treestore.get_value(iter, 0))
        
        #query = config.db.session.query(CustGroups).select_from(CustGroups)
        #query = query.filter(CustGroups.custGrpCode == code)
        #group_id = query.first().custGrpId
        #self.emit("group-selected", group_id, code)   


    def selectBuyingSubject(self, sender):
        subject_win = subjects.Subjects()
        buy_code = self.buyCodeEntry.get_text()
        subject_win.highlightSubject(buy_code)
        subject_win.connect("subject-selected", self.buyingSubjectSelected)
        
    def buyingSubjectSelected(self, sender, id, code, name):
	if config.digittype == 1:
            code = utility.convertToPersian(code)
        self.buyCodeEntry.set_text(code)
        sender.window.destroy()
        
    def selectSellingSubject(self, sender):
        subject_win = subjects.Subjects()
        sell_code = self.sellCodeEntry.get_text()
        subject_win.highlightSubject(sell_code)
        subject_win.connect("subject-selected", self.sellingingSubjectSelected)
        
    def sellingingSubjectSelected(self, sender, id, code, name):
	if config.digittype == 1:
            code = utility.convertToPersian(code)
        self.sellCodeEntry.set_text(code)
        sender.window.destroy()
#gobject.type_register(Group)
#gobject.signal_new("group-selected", Group, gobject.SIGNAL_RUN_LAST,
                   #gobject.TYPE_NONE, (gobject.TYPE_INT, gobject.TYPE_STRING))   