import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GObject

from sqlalchemy.orm.util import outerjoin
from sqlalchemy.orm.query import aliased
from sqlalchemy.sql.functions import *
from sqlalchemy.sql import and_
from sqlalchemy.orm import sessionmaker, join
from .dateentry import *
from . import decimalentry

from . import numberentry
from .utility import LN, convertToLatin, checkPermission
from .database import *
from .share import share
from .helpers import get_builder
from amir.share import Share
from passlib.hash import bcrypt

import sys
if sys.version_info > (3,):
    unicode = str

# config = share.config
# Users and permissions:
#       create: 2
#       read:   4
#       update: 8
#       delete: 16
#
# Warehouse:
#       create: 32
#       read:   64
#       update: 128
#       delete: 256
#
# Accounting:
#       create: 512
#       read:   1024
#       update: 2048
#       delete: 4096
#
# Reports:
#       create: 8192
#       read:   16384
#       update: 32768
#       delete: 65536
#
# Checque:
#       create: 131072
#       read:   262144
#       update: 524288
#       delete: 1048576
#
# Config:
#       create: 2097152
#       read:   4194304
#       update: 8388608
#       delete: 16777216


class User(GObject.GObject):
    subjecttypes = ["Debtor", "Creditor", "Both"]

    def __init__(self, ledgers_only=False, parent_id=[0, ], multiselect=False):
        GObject.GObject.__init__(self)

        self.builder = get_builder("user")
        self.window = self.builder.get_object("viewUsers")

        self.userTreeview = self.builder.get_object("usersTreeview")

        self.userTreestore = Gtk.TreeStore(int, str, str, str)
        column = Gtk.TreeViewColumn(_("ID"), Gtk.CellRendererText(), text=0)

        column.set_spacing(5)
        column.set_resizable(True)
        self.userTreeview.append_column(column)
        column = Gtk.TreeViewColumn(_("Name"), Gtk.CellRendererText(), text=1)

        column.set_spacing(5)
        column.set_resizable(True)
        self.userTreeview.append_column(column)
        column = Gtk.TreeViewColumn(
            _("Username"), Gtk.CellRendererText(), text=2)

        column.set_spacing(5)
        column.set_resizable(True)
        self.userTreeview.append_column(column)
        column = Gtk.TreeViewColumn(
            _("Permission"), Gtk.CellRendererText(), text=3)

        column.set_spacing(5)
        column.set_resizable(True)
        self.userTreeview.append_column(column)

        # Find top level ledgers (with parent_id equal to 0)
        result = share.config.db.session.query(
            Users.id, Users.name, Users.username, Users.permission).all()

        for a in result:
            permissionName = share.config.db.session.query(Permissions.name).filter(
                Permissions.id == a.permission).first()
            if permissionName:
                iter = self.userTreestore.append(
                    None, (a.id, a.name, a.username, permissionName[0]))

        if ledgers_only == True:
            btn = self.builder.get_object("addsubtoolbutton")
            btn.hide()

        self.userTreeview.set_model(self.userTreestore)
        self.userTreestore.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        self.window.show_all()
        self.builder.connect_signals(self)

        if checkPermission(2):
            self.builder.get_object("addUserButton").hide()
        if checkPermission(8):
            self.builder.get_object("editUserButton").hide()
        if checkPermission(16):
            self.builder.get_object("deleteUserBtn").hide()

        if multiselect:
            self.userTreeview.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
            self.groupTreestore.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
            self.builder.get_object('toolbar4').hide()
            self.builder.get_object('statusbar1').hide()
        else:
            self.builder.get_object('hbox5').hide()
        self.numberOfCheckboxes = 24

    def on_cancel_clicked(self, sender):
        self.window.hide()

    def addUser(self, sender):
        self.window = self.builder.get_object("newUserWindow")
        self.builder.connect_signals(self)
        self.window.show_all()
        self.window.set_title(_("Add User"))

    def addUserSubmit(self, sender):
        username = self.builder.get_object("username").get_text()
        self.builder.get_object("username").set_text("")
        password = self.builder.get_object("password").get_text()
        self.builder.get_object("password").set_text("")
        name = self.builder.get_object("name").get_text()
        self.builder.get_object("name").set_text("")
        self.window.hide()
        self.saveNewUser(unicode(name), unicode(username),
                         unicode(password), type, None)

    def selectGroup(self, sender=0, edit=None):
        self.session = share.config.db.session
        # self.Document = class_document.Document()

        query = self.session.query(Factors.Id).select_from(Factors)
        lastId = query.order_by(Factors.Id.desc()).first()
        if not lastId:
            lastId = 0
        else:
            lastId = lastId.Id
        self.Id = lastId + 1
        self.window1 = self.builder.get_object("viewPermissions")
        self.builder.connect_signals(self)
        self.groupTreeview = self.builder.get_object("groupsTreeView")
        self.groupTreestore = Gtk.TreeStore(int, str)
        column = Gtk.TreeViewColumn(_("ID"), Gtk.CellRendererText(), text=0)
        column.set_spacing(5)
        column.set_resizable(True)
        self.groupTreeview.append_column(column)
        column = Gtk.TreeViewColumn(_("Name"), Gtk.CellRendererText(), text=1)
        column.set_spacing(5)
        column.set_resizable(True)
        self.groupTreeview.append_column(column)

        result = share.config.db.session.query(
            Permissions.id, Permissions.name).all()
        for a in result:
            iter = self.groupTreestore.append(None, (int(a.id), str(a.name)))
        self.groupTreeview.set_model(self.groupTreestore)
        self.groupTreestore.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        self.builder.connect_signals(self)

        self.window1.show_all()
        if checkPermission(2):
            self.builder.get_object("addPermissionButton").hide()
        if checkPermission(8):
            self.builder.get_object("editPermissionButton").hide()
        if checkPermission(16):
            self.builder.get_object("deletePermissionButton").hide()

    def addPermission(self, sender):
        self.window = self.builder.get_object("permissionWindow")
        self.builder.connect_signals(self)
        okButton = self.builder.get_object("okButton")
        okButton.connect("clicked", self.saveNewPermission)
        self.window.show_all()

    def editUser(self, sender):
        self.editUserFlag = True
        self.window = self.builder.get_object("editUserWindow")
        self.builder.connect_signals(self)
        self.window.show_all()
        self.window.set_title(_("Edit User"))
        selection = self.userTreeview.get_selection()
        iter = selection.get_selected()[1]
        id = convertToLatin(self.userTreestore.get(iter, 0)[0])
        self.idEdit = id
        name = self.userTreestore.get(iter, 1)[0]
        username = self.userTreestore.get(iter, 2)[0]
        permission = self.userTreestore.get(iter, 3)[0]

        entry = self.builder.get_object("nameEdit")
        entry.set_text(name)
        entry = self.builder.get_object("usernameEdit")
        entry.set_text(username)
        entry = self.builder.get_object("permissionEdit")
        entry.set_text(permission)

    def editUserSubmit(self, sender):
        userId = self.idEdit
        username = self.builder.get_object("usernameEdit")
        password = self.builder.get_object("passwordEdit")
        name = self.builder.get_object("nameEdit")
        permission = self.builder.get_object("permissionEdit").get_text()
        permissionId = share.config.db.session.query(Permissions.id).filter(
            Permissions.name == permission).first()
        self.groupId = permissionId[0]
        self.saveEditUser(userId, str(name.get_text()), str(
            username.get_text()), str(password.get_text()), type, None,permission)
        self.window.hide()

    def deleteUser(self, sender):
        selection = self.userTreeview.get_selection()
        iter = selection.get_selected()[1]
        if iter != None:
            Subject1 = aliased(Subject, name="s1")
            Subject2 = aliased(Subject, name="s2")

            code = convertToLatin(self.userTreestore.get(iter, 0)[0])
            row = share.config.db.session.query(
                Users).filter(Users.id == code).first()
            share.config.db.session.delete(row)
            share.config.db.session.commit()
            self.userTreestore.remove(iter)

    def deleteGroup(self, sender):
        selection = self.groupTreeview.get_selection()
        iter = selection.get_selected()[1]
        if iter != None:
            code = convertToLatin(self.groupTreestore.get(iter, 0)[0])
            row = share.config.db.session.query(Permissions).filter(
                Permissions.id == code).first()
            share.config.db.session.delete(row)
            share.config.db.session.commit()
            self.groupTreestore.remove(iter)

    def saveNewUser(self, name, username, password, type, iter):
        user = Users(name, username, password, self.groupId)
        share.config.db.session.add(user)

        share.config.db.session.commit()

        child = self.userTreestore.append(
            iter, (user.id, name, username, self.groupName))

        self.temppath = self.userTreestore.get_path(child)
        self.userTreeview.scroll_to_cell(self.temppath, None, False, 0, 0)
        self.userTreeview.set_cursor(self.temppath, None, False)

    def saveEditUser(self, userId, name, username, password, type, iter,permission):
        result = share.config.db.session.query(Users)
        result = result.filter(Users.id == userId)
        result[0].name = name
        result[0].username = username
        if password:
            result[0].password = bcrypt.encrypt(password)
        result[0].permission = self.groupId
        share.config.db.session.commit()

    def getPermission(self):
        permissionResult = 0
        for x in range(1, self.numberOfCheckboxes + 1):
            if self.builder.get_object("checkbutton" + str(x)).get_active() == True:
                permissionResult += 2**x
        return permissionResult

    def setPermission(self, id):
        result = share.config.db.session.query(Permissions)
        result = result.filter(Permissions.id == id)
        permissionResult = int(result[0].value)
        for x in range(self.numberOfCheckboxes, 0, -1):
            if permissionResult >= 2**x:
                self.builder.get_object(
                    "checkbutton" + str(x)).set_active(True)
                permissionResult = permissionResult - 2**x

    def saveNewPermission(self, sender):
        permissionResult = self.getPermission()
        name = self.builder.get_object("nameEntry")
        permission = Permissions(
            unicode(name.get_text()), str(permissionResult))
        share.config.db.session.add(permission)

        share.config.db.session.commit()

        child = self.groupTreestore.append(
            None, (int(permission.id), str(permission.name)))
        self.window.hide()

        self.temppath = self.userTreestore.get_path(child)
        self.window.hide()

    def editPermission(self, sender):
        dialog = self.builder.get_object("permissionWindow")
        dialog.set_title(_("Edit Permission"))
        selection = self.groupTreeview.get_selection()
        iter = selection.get_selected()[1]
        id = convertToLatin(self.groupTreestore.get(iter, 0)[0])
        permissionName = self.groupTreestore.get(iter, 1)[0]
        permissionId = share.config.db.session.query(Permissions.id).filter(
            Permissions.name == permissionName).first()
        self.groupId = permissionId[0]
        self.setPermission(id)
        self.window = self.builder.get_object("permissionWindow")
        self.builder.connect_signals(self)
        entry = self.builder.get_object("nameEntry")
        entry.set_text(permissionName)
        okButton = self.builder.get_object("okButton")
        okButton.connect("clicked", self.saveEditPermission)
        self.window.show_all()

    def saveEditPermission(self, sender):
        permissionResult = self.getPermission()
        name = self.builder.get_object("nameEntry").get_text()
        result = share.config.db.session.query(Permissions).filter(
            Permissions.id == self.groupId)
        result[0].name = name
        result[0].value = permissionResult
        share.config.db.session.commit()
        child = self.groupTreestore.append(
            None, (int(result[0].id), str(name)))
        self.window.hide()

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
        if iter != None:
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

    def selectGroupFromList(self, treeview, path, view_column):
        selection = self.groupTreeview.get_selection()
        if selection.get_mode() == Gtk.SelectionMode.MULTIPLE:
            return

        iter = self.groupTreestore.get_iter(path)
        self.groupId = convertToLatin(self.groupTreestore.get(iter, 0)[0])
        self.groupName = self.groupTreestore.get(iter, 1)[0]
        self.builder.get_object("permissionEdit").set_text(self.groupName)
        self.builder.get_object("permissionNew").set_text(self.groupName)
        self.window1.hide()

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

            query = share.config.db.session.query(Subject).select_from(Subject)
            query = query.filter(Subject.code == code)
            sub_id = query.first().id
            items.append((sub_id, code, name))
        self.emit("subject-multi-selected", items)

    def window_close(self, *args):
        self.window1.hide()
        return True


GObject.type_register(User)
GObject.signal_new("group-selected", User, GObject.SignalFlags.RUN_LAST,
                   None, (GObject.TYPE_INT, GObject.TYPE_STRING, GObject.TYPE_STRING))
GObject.signal_new("subject-multi-selected", User, GObject.SignalFlags.RUN_LAST,
                   None, (GObject.TYPE_PYOBJECT,))
