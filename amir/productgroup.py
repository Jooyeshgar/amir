from . import numberentry
from . import dateentry
from . import subjects
from . import utility

import  gobject


from    sqlalchemy.orm              import  sessionmaker, join
from    sqlalchemy.orm.util         import  outerjoin
from    sqlalchemy.orm.query        import  aliased
from    sqlalchemy.sql              import  and_, or_
from    sqlalchemy.sql.functions    import  *

from    .helpers                    import  get_builder
from    .share                      import  share
from    datetime                    import  date
from    .database                   import  *
import gi
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

import sys
if sys.version_info > (3,):
    unicode = str

config = share.config

gi.require_version('Gtk', '3.0')

class ProductGroup(GObject.GObject):
    
    def __init__(self):
        GObject.GObject.__init__(self)
        
        self.builder    = get_builder("warehousing" )
        self.window = None
        self.treestore = None
        
        #self.grpCodeEntry = numberentry.NumberEntry()
        #box = self.builder.get_object("grpCodeBox")
        #box.add(self.grpCodeEntry)
        #self.grpCodeEntry.show()
        
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
        self.treestore = Gtk.TreeStore(str, str, str, str)
        self.treestore.clear()
        self.treeview.set_model(self.treestore)

        column = Gtk.TreeViewColumn(_("Code"), Gtk.CellRendererText(), text = 0)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(0)
        column.set_sort_indicator(True)
        self.treeview.append_column(column)
        
        column = Gtk.TreeViewColumn(_("Name"), Gtk.CellRendererText(), text = 1)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        column.set_sort_indicator(True)
        self.treeview.append_column(column)
        
        column = Gtk.TreeViewColumn(_("Buy ID"), Gtk.CellRendererText(), text = 2)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        
        column = Gtk.TreeViewColumn(_("Sell ID"), Gtk.CellRendererText(), text = 3)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        
        self.treeview.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        self.treestore.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        
        #Fill groups treeview
        query = config.db.session.query(ProductGroups).select_from(ProductGroups)
        result = query.all()
        
        for group in result:
            code = group.code
            buyId = group.buyId
            sellId = group.sellId
            if config.digittype == 1:
                #code = utility.convertToPersian(code)
                buyId = utility.convertToPersian(buyId)
                sellId = utility.convertToPersian(sellId)
            self.treestore.append(None, (utility.readNumber(code), str(group.name), utility.readNumber(buyId), utility.readNumber(sellId)))
            
        self.window.show_all()
        self.window.grab_focus()
        
    def addProductGroup(self, sender):
        dialog = self.builder.get_object("addProductGroupDlg")
        dialog.set_title(_("Add new group"))
        self.builder.get_object("groupCodeEntry").set_text("")
        self.builder.get_object("groupNameEntry").set_text("")
        self.buyCodeEntry.set_text("")
        self.sellCodeEntry.set_text("")
        
        success = False
        while not success :
            result = dialog.run()
            if result == 1:
                grpcode = self.builder.get_object("groupCodeEntry").get_text()
                grpname = self.builder.get_object("groupNameEntry").get_text()
                grpbuycode = self.buyCodeEntry.get_text()
                grpsellcode = self.sellCodeEntry.get_text()
                success = self.saveProductGroup(unicode(grpcode), unicode(grpname), grpbuycode, grpsellcode, None)
            else:
                break
                
        dialog.hide()
    
    def editProductGroup(self, sender):
        dialog = self.builder.get_object("addProductGroupDlg")
        dialog.set_title(_("Edit group"))
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        
        if iter != None :
            grpcode = unicode(self.treestore.get(iter, 0)[0])
            #if config.digittype == 1:
                #code = utility.convertToLatin(grpcode)
            #else:
                #code = grpcode
                
            BuySub = aliased(Subject, name="bs")
            SellSub = aliased(Subject, name="ss")
            
            query = config.db.session.query(ProductGroups, BuySub.code, SellSub.code)
            query = query.select_from( outerjoin( outerjoin(ProductGroups, BuySub, ProductGroups.buyId == BuySub.id),
                                                  SellSub, ProductGroups.sellId == SellSub.id ) )
            (group, buy_code, sell_code) = query.filter(ProductGroups.code == grpcode).first()
            name = group.name
            if config.digittype == 1:
                buy_code = utility.convertToPersian(buy_code)
                sell_code = utility.convertToPersian(sell_code)
            
            self.builder.get_object("groupCodeEntry").set_text(grpcode)
            self.builder.get_object("groupNameEntry").set_text(name)
            self.buyCodeEntry.set_text(buy_code)
            self.sellCodeEntry.set_text(sell_code)
            
            success = False
            while not success :
                result = dialog.run()
                if result == 1:
                    grpcode = self.builder.get_object("groupCodeEntry").get_text()
                    grpname = self.builder.get_object("groupNameEntry").get_text()
                    grpbuycode = self.buyCodeEntry.get_text()
                    grpsellcode = self.sellCodeEntry.get_text()
                    success = self.saveProductGroup(unicode(grpcode), unicode(grpname), grpbuycode, grpsellcode, iter)
                else:
                    break
                
            dialog.hide()
                
    def deleteProductGroup(self, sender):
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        if iter != None :
            #code = utility.convertToLatin(self.treestore.get(iter, 0)[0])
            code = unicode(self.treestore.get(iter, 0)[0])
            
            query = config.db.session.query(ProductGroups, count(Products.id))
            query = query.select_from(outerjoin(ProductGroups, Products, ProductGroups.id == Products.accGroup))
            result = query.filter(ProductGroups.code == code).first()
            
            if result[1] != 0 :
                msgbox =  Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE,
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
        msg = ""
        if code == "":
            msg += _("Group code should not be empty.\n")
        if name == "":
            msg = _("Group name should not be empty.\n")
        #TODO set default values for buyid & sellid if empty
            
        if msg != "":
            msgbox =  Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.CLOSE, msg)
            msgbox.set_title(_("Empty fields"))
            msgbox.run()
            msgbox.destroy()
            return False
        
        if edititer != None:
            pcode = unicode(self.treestore.get_value(edititer, 0))
            #pcode = utility.convertToLatin(pcode)
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
            msgbox =  Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE, msg)
            msgbox.set_title(_("Invalid group properties"))
            msgbox.run()
            msgbox.destroy()
            return False
            
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
            #code = utility.convertToPersian(code)
            buy_code = utility.convertToPersian(buy_code)
            sell_code = utility.convertToPersian(sell_code)
        self.saveRow(edititer, (code, name, buy_code, sell_code))
        return True
        
        
    #@param treeiter: the TreeIter which data should be saved in
    #@param data: a tuple containing data to be saved
    def saveRow(self, treeiter, data):
        self.treestore.set(treeiter, 0, data[0], 1, data[1], 2, data[2], 3, data[3])
    
    def highlightGroup(self, code):
        code = code.decode('utf-8')
        l = len(code)
        iter = self.treestore.get_iter_first()
        pre = iter
        
        while iter:
            itercode = self.treestore.get_value(iter, 0).decode('utf-8')[0:l]
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
            self.treeview.grab_focus()
            
    
    def selectGroupFromList(self, treeview, path, view_column):
        iter = self.treestore.get_iter(path)
        code = unicode(self.treestore.get_value(iter, 0))
        
        query = config.db.session.query(ProductGroups).select_from(ProductGroups)
        query = query.filter(ProductGroups.code == code)
        group_id = query.first().id
        self.emit("group-selected", group_id, code)
        
    def on_button_press_event(self, sender, event):
        if event.type == Gdk.EventType._2BUTTON_PRESS:
            selection = self.treeview.get_selection()
            iter = selection.get_selected()[1]
            if iter != None :
                self.emit("item-activated")
            else:
                self.emit("blank-activated")

    def on_key_release_event(self, sender, event):
        expand = 0
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        if iter != None :
            if Gdk.keyval_name(event.keyval) == "Left":
                if self.treeview.get_direction() != Gtk.TextDirection.LTR:
                    expand = 1
                else:
                    expand = -1
                    
            if Gdk.keyval_name(event.keyval) == "Right":
                if self.treeview.get_direction() != Gtk.TextDirection.RTL:
                    expand = 1
                else:
                    expand = -1
             
            if expand == 1:
                if self.treestore.iter_has_child(iter):
                    path = self.treestore.get_path(iter)
                    self.treeview.expand_row(path, False)
                    return
            elif expand == -1:
                path = self.treestore.get_path(iter)
                if self.treeview.row_expanded(path):
                    self.treeview.collapse_row(path)
                else: 
                    parent = self.treestore.iter_parent(iter)
                    if parent != None:
                        path = self.treestore.get_path(parent)
                        self.treeview.collapse_row(path)
                        self.treeview.set_cursor(path, None, False)
                        self.treeview.grab_focus()
                return
                
                
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
        
    def selectProductGroup(self, sender):    
        return
        
GObject.type_register(ProductGroup)
GObject.signal_new("group-selected", ProductGroup, GObject.SignalFlags.RUN_LAST,
                   None, (GObject.TYPE_INT, GObject.TYPE_STRING))
GObject.signal_new("item-activated", ProductGroup, GObject.SignalFlags.RUN_LAST,
                   None, ())
GObject.signal_new("blank-activated", ProductGroup, GObject.SignalFlags.RUN_LAST,
                   None, ())
