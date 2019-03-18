#import  warehousing
from . import numberentry
from . import dateentry
from . import subjects
from . import utility

# import  gobject
# 
# import  gtk


from    sqlalchemy.orm              import  sessionmaker, join
from    sqlalchemy.orm.util         import  outerjoin
from    sqlalchemy.sql              import  and_, or_
from    sqlalchemy.sql.functions    import  *

from    .helpers                    import  get_builder
from    .share                      import  share
from    datetime                    import  date
from    .database                   import  *
import gi
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk

gi.require_version('Gtk', '3.0')
config  = share.config

class Group(GObject.GObject):
    
    def __init__(self):
        GObject.GObject.__init__(self)
        
        self.builder    = get_builder("customers" )
        self.window = None
        self.treestore = None
        
        self.grpCodeEntry = numberentry.NumberEntry()
        box = self.builder.get_object("grpCodeBox")
        box.add(self.grpCodeEntry)
        self.grpCodeEntry.show()
        
        self.builder.connect_signals(self)
    
            
    def viewCustomerGroups(self):
        self.window = self.builder.get_object("viewCustGroupsWindow")
        
        self.treeview = self.builder.get_object("custGroupsTreeView")
        self.treestore = Gtk.TreeStore(str, str, str)
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
        
        column = Gtk.TreeViewColumn(_("Description"), Gtk.CellRendererText(), text = 2)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        
        self.treeview.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        #self.treestore.set_sort_func(0, self.sortGroupIds)
        self.treestore.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        
        #Fill groups treeview
        query = config.db.session.query(CustGroups).select_from(CustGroups)
        result = query.all()
        
        for group in result:
            self.treestore.append(None, (group.custGrpCode, group.custGrpName, group.custGrpDesc))
            
        self.window.show_all()
        
    def addCustomerGroup(self, sender):
        dialog = self.builder.get_object("addCustGrpDlg")
        dialog.set_title(_("Add new group"))
        self.grpCodeEntry.set_text("")
        self.builder.get_object("grpNameEntry").set_text("")
        self.builder.get_object("grpDescEntry").set_text("")
        
        result = dialog.run()
        if result == 1:
            grpcode = self.grpCodeEntry.get_text()
            grpname = self.builder.get_object("grpNameEntry").get_text()
            grpdesc = self.builder.get_object("grpDescEntry").get_text()
            self.saveCustGroup(grpcode, unicode(grpname), unicode(grpdesc), None)
                
        dialog.hide()
    
    def editCustomerGroup(self, sender):
        dialog = self.builder.get_object("addCustGrpDlg")
        dialog.set_title(_("Edit group"))
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        
        if iter != None :
            if config.digittype == 1:
                code = utility.convertToLatin(self.treestore.get(iter, 0)[0])
            else:
                code = self.treestore.get(iter, 0)[0]
                
            query = config.db.session.query(CustGroups).select_from(CustGroups)
            group = query.filter(CustGroups.custGrpCode == code).first()
            name = group.custGrpName
            desc = group.custGrpDesc
            
            self.grpCodeEntry.set_text(code)
            self.builder.get_object("grpNameEntry").set_text(name)
            self.builder.get_object("grpDescEntry").set_text(desc)
            
            result = dialog.run()
            if result == 1:
                grpcode = self.grpCodeEntry.get_text()
                grpname = self.builder.get_object("grpNameEntry").get_text()
                grpdesc = self.builder.get_object("grpDescEntry").get_text()
                self.saveCustGroup(grpcode, unicode(grpname), unicode(grpdesc), iter)
                
            dialog.hide()
                
    def deleteCustomerGroup(self, sender):
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        if iter != None :
            code = utility.convertToLatin(self.treestore.get(iter, 0)[0])
            
            query = config.db.session.query(CustGroups, count(Customers.custId))
            query = query.select_from(outerjoin(CustGroups, Customers, CustGroups.custGrpId == Customers.custGroup))
            result = query.filter(CustGroups.custGrpCode == code).first()
            
            if result[1] != 0 :
                msgbox =  Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE,
                                    _("Group can not be deleted, Because there are some customers registered in it."))
                msgbox.set_title(_("Error deleting group"))
                msgbox.run()
                msgbox.destroy()
            else :
                group = result[0]
                config.db.session.delete(group)
                config.db.session.commit()
                self.treestore.remove(iter)
    
    #@param edititer: None if a new customer group is to be saved.
    #                 Otherwise it stores the TreeIter for the group that's been edited.
    def saveCustGroup(self, code, name, desc, edititer=None):
        msg = "";
        if name == "":
            msg = _("Group name should not be empty")
        elif code == "":
            msg = _("Group code should not be empty")
            
        if msg != "":
            msgbox =  Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.CLOSE, msg)
            msgbox.set_title(_("Empty fields"))
            msgbox.run()
            msgbox.destroy()
            return
        
        if edititer != None:
            pcode = self.treestore.get_value(edititer, 0)
            pcode = utility.convertToLatin(pcode)
            query = config.db.session.query(CustGroups).select_from(CustGroups)
            group = query.filter(CustGroups.custGrpCode == pcode).first()
            gid = group.custGrpId
        
        code = utility.convertToLatin(code)
        query = config.db.session.query(CustGroups).select_from(CustGroups)
        query = query.filter(or_(CustGroups.custGrpCode == code, CustGroups.custGrpName == name))
        if edititer != None:
            query = query.filter(CustGroups.custGrpId != gid)
        result = query.all()
        msg = ""
        for grp in result:
            if grp.custGrpCode == code:
                msg = _("A group with this code already exists.")
                break
            elif grp.custGrpName == name:
                msg = _("A group with this name already exists.")
                break
        if msg != "":
            msgbox =  Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE, msg)
            msgbox.set_title(_("Duplicate group"))
            msgbox.run()
            msgbox.destroy()
            return
        
        
        if edititer == None:
            group = CustGroups(code, name, desc)
            
            edititer = self.treestore.append(None)
            path = self.treestore.get_path(edititer)
            self.treeview.scroll_to_cell(path, None, False, 0, 0)
            self.treeview.set_cursor(path, None, False)
        else:
            group.custGrpCode = code
            group.custGrpName = name
            group.custGrpDesc = desc
            
        config.db.session.add(group)
        config.db.session.commit()
        
        if config.digittype == 1:
            code = utility.convertToPersian(code)
        self.saveRow(edititer, (code, name, desc))
        
        
    #@param treeiter: the TreeIter which data should be saved in
    #@param data: a tuple containing data to be saved
    def saveRow(self, treeiter, data):
        self.treestore.set(treeiter, 0, data[0], 1, data[1], 2, data[2])
    
    def highlightGroup(self, code):
#        code = code.decode('utf-8')
        iter = self.treestore.get_iter_first()
        pre = iter
        
        while iter:
#            res = self.match_func(iter, (0, part))
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
            self.treeview.grab_focus()

    
    def selectCustGroupFromList(self, treeview, path, view_column):
        iter = self.treestore.get_iter(path)
        code = utility.convertToLatin(self.treestore.get_value(iter, 0))
        
        query = config.db.session.query(CustGroups).select_from(CustGroups)
        query = query.filter(CustGroups.custGrpCode == code)
        group_id = query.first().custGrpId
        self.emit("group-selected", group_id, code)   

GObject.type_register(Group)
GObject.signal_new("group-selected", Group, GObject.SignalFlags.RUN_LAST,
                   None, (GObject.TYPE_INT, GObject.TYPE_STRING))   