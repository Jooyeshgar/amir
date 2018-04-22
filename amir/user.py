import gi
from gi.repository import Gtk
from gi.repository import GObject

from sqlalchemy.orm.util import outerjoin
from sqlalchemy.orm.query import aliased
from sqlalchemy.sql.functions import *
from sqlalchemy.sql import and_
from sqlalchemy.orm import sessionmaker, join

import numberentry
from utility import LN,convertToLatin
from database import *
from share import share
from helpers import get_builder
from amir.share import Share

config = share.config

class User(GObject.GObject):
    subjecttypes = ["Debtor", "Creditor", "Both"]
    
    def __init__ (self, ledgers_only=False, parent_id=[0,], multiselect=False):
        GObject.GObject.__init__(self)

        self.builder = get_builder("user")
        
        self.window = self.builder.get_object("subjectswindow")
        self.window.set_modal(True)
        
        self.treeview = self.builder.get_object("treeview")
            
        self.treestore = Gtk.TreeStore(int, str, str)
        column = Gtk.TreeViewColumn(_("ID"), Gtk.CellRendererText(), text=0)

        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = Gtk.TreeViewColumn(_("Name"), Gtk.CellRendererText(), text=1)

        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = Gtk.TreeViewColumn(_("Username"), Gtk.CellRendererText(), text=2)

        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        
        #Find top level ledgers (with parent_id equal to 0)
        result = config.db.session.query(Users.id, Users.name, Users.username).all()

        for a in result :            
            iter = self.treestore.append(None, (a.id, a.name, a.username))
        
        if ledgers_only == True:
            btn = self.builder.get_object("addsubtoolbutton")
            btn.hide()
        
        self.treeview.set_model(self.treestore)
        self.treestore.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        self.window.show_all()
        self.builder.connect_signals(self)

        if multiselect:
            self.treeview.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
            self.builder.get_object('toolbar4').hide()
            self.builder.get_object('statusbar1').hide()
        else:
            self.builder.get_object('hbox5').hide()
        
    def addUser(self, sender):
        dialog = self.builder.get_object("dialog1")
        dialog.set_title(_("Add User"))
        hbox = self.builder.get_object("hbox3")
        hbox.hide()

        username = self.builder.get_object("username")
        username.set_text("")
        password = self.builder.get_object("password")
        password.set_text("")
        name = self.builder.get_object("name")
        name.set_text("")
        
        result = dialog.run()
        if result == 1 :             
            self.saveNewUser(unicode(name.get_text()),unicode(username.get_text()), unicode(password.get_text()), type, None, dialog)
        dialog.hide()
        
    
    def editUser(self, sender):
        dialog = self.builder.get_object("dialog1")
        dialog.set_title(_("Edit User"))
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        id = convertToLatin(self.treestore.get(iter, 0)[0])
        name = self.treestore.get(iter, 1)[0]
        username = self.treestore.get(iter, 2)[0]
        
        if iter != None :
            entry = self.builder.get_object("name")
            entry.set_text(name)
            
            entry = self.builder.get_object("username")
            entry.set_text(username)

            result = dialog.run()
            
            if result == 1:
                userId = convertToLatin(self.treestore.get(iter, 0)[0])
                username = self.builder.get_object("username")
                password = self.builder.get_object("password")
                name = self.builder.get_object("name")
                self.saveEditUser(userId, unicode(name.get_text()),unicode(username.get_text()), unicode(password.get_text()), type, None, dialog)
            dialog.hide()
    
    def deleteUser(self, sender):
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        if iter != None :
            Subject1 = aliased(Subject, name="s1")
            Subject2 = aliased(Subject, name="s2")
            
            code = convertToLatin(self.treestore.get(iter, 0)[0])
            row = config.db.session.query(Users).filter(Users.id == code).first()
            config.db.session.delete(row)
            config.db.session.commit()
            self.treestore.remove(iter)
    
    def saveNewUser(self, name, username, password, type, iter, widget):
        #Now create new subject:
        user = Users(name, username, password)
        config.db.session.add(user)
        
        config.db.session.commit()
        
        child = self.treestore.append(iter, (user.id, name, username))
        
        self.temppath = self.treestore.get_path(child)
        self.treeview.scroll_to_cell(self.temppath, None, False, 0, 0)
        self.treeview.set_cursor(self.temppath, None, False)

    def saveEditUser(self, userId, name, username, password, type, iter, widget):
        print userId
        print name
        print username
        print password
        result = config.db.session.query(Users)
        result.filter(Users.id == userId)
        result[0].name = name
        result[0].username = username
        result[0].password = password
        config.db.session.commit()
        
        # self.treestore.set( ('Name','Username'), (name, username))
        
        # self.temppath = self.treestore.get_path(child)
        # self.treeview.scroll_to_cell(self.temppath, None, False, 0, 0)
        # self.treeview.set_cursor(self.temppath, None, False)
        
    def match_func(self, iter, data):
        (column, key) = data   # data is a tuple containing column number, key
        value = self.treestore.get_value(iter, column)
        if value < key:
            return -1
        elif value == key:
            return 0
        else:
            return 1

    def highlightSubject(self, code):
        i = 2
        code = code.decode('utf-8')
        part = code[0:i]
        iter = self.treestore.get_iter_first()
        parent = iter
        
        while iter:
            res = self.match_func(iter, (0, part))
            if res < 0:
                iter = self.treestore.iter_next(iter)
            elif res == 0:
                if len(code) > i:
                    parent = iter
                    iter = self.treestore.iter_children(parent)
                    if iter:
                        if self.treestore.get_value(iter, 0) == "":
                            self.populateChildren(self.treeview, parent, None)
                            iter = self.treestore.iter_children(parent)
                        i += 2
                        part = code[0:i]
                else:
                    break
            else:
                break

        if not iter:
            iter = parent
            
        if iter:
            path = self.treestore.get_path(iter)
            self.treeview.expand_to_path(path)
            self.treeview.scroll_to_cell(path, None, False, 0, 0)
            self.treeview.set_cursor(path, None, False)
            self.treeview.grab_focus()
     
    def on_key_release_event(self, sender, event):
        expand = 0
        selection = self.treeview.get_selection()
        if selection.get_mode() == Gtk.SelectionMode.MULTIPLE:
            return

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
#            if Gdk.keyval_name(event.keyval) == Ri:
            
    def selectSubjectFromList(self, treeview, path, view_column):
        selection = self.treeview.get_selection()
        if selection.get_mode() == Gtk.SelectionMode.MULTIPLE:
            return

        iter = self.treestore.get_iter(path)
        code = convertToLatin(self.treestore.get(iter, 0)[0])
        name = self.treestore.get(iter, 1)[0]
        
        query = config.db.session.query(Subject).select_from(Subject)
        query = query.filter(Subject.code == code)
        sub_id = query.first().id
        self.emit("subject-selected", sub_id, code, name)

    def dbChanged(self, sender, active_dbpath):
        self.window.destroy()

    def on_select_clicked(self, button):
        selection = self.treeview.get_selection()
        items = []
        model, pathes = selection.get_selected_rows()
        for path in pathes:
            iter = self.treestore.get_iter(path)
            code = convertToLatin(self.treestore.get(iter, 0)[0])
            name = self.treestore.get(iter, 1)[0]

            query = config.db.session.query(Subject).select_from(Subject)
            query = query.filter(Subject.code == code)
            sub_id = query.first().id
            items.append((sub_id, code, name))
        self.emit("subject-multi-selected", items)

GObject.type_register(User)
GObject.signal_new("subject-selected", User, GObject.SignalFlags.RUN_LAST,
                   None, (GObject.TYPE_INT, GObject.TYPE_STRING, GObject.TYPE_STRING))
GObject.signal_new("subject-multi-selected", User, GObject.SignalFlags.RUN_LAST,
                   None, (GObject.TYPE_PYOBJECT,))
   
