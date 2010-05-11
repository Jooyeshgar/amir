import pygtk
import gtk
import gobject

from sqlalchemy.orm.util import outerjoin
from sqlalchemy.orm.query import aliased
from sqlalchemy.sql.functions import count
from sqlalchemy.sql import and_
from sqlalchemy.orm import sessionmaker, join

import utility
from database import *
from amirconfig import config
from helpers import get_builder

class Subjects(gobject.GObject):
    
    subjecttypes = ["Debtor", "Creditor", "Both"]
    
    def __init__ (self, ledgers_only=False):
        gobject.GObject.__init__(self)

        self.builder = get_builder("notebook")
        
        self.window = self.builder.get_object("subjectswindow")
        self.window.set_modal(True)
        
        self.treeview = self.builder.get_object("treeview")
        self.treestore = gtk.TreeStore(str, str, str)
        column = gtk.TreeViewColumn(_("Subject Code"), gtk.CellRendererText(), text=0)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = gtk.TreeViewColumn(_("Subject Name"), gtk.CellRendererText(), text=1)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = gtk.TreeViewColumn(_("Debtor or Creditor"), gtk.CellRendererText(), text=2)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        self.treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        
        self.session = config.db.session
        
        Subject1 = aliased(Subject, name="s1")
        Subject2 = aliased(Subject, name="s2")
        
        #Find top level ledgers (with parent_id equal to 0)
        query = self.session.query(Subject1.code, Subject1.name, Subject1.type, count(Subject2.id))
        query = query.select_from(outerjoin(Subject1, Subject2, Subject1.id == Subject2.parent_id))
        result = query.filter(Subject1.parent_id == 0).group_by(Subject1.id).all()
        for a in result :
            type = _(self.__class__.subjecttypes[a[2]])
            code = a[0]
            if config.digittype == 1:
                code = utility.convertToPersian(code)
            iter = self.treestore.append(None, (code, a[1], type))
            if (a[3] != 0 and ledgers_only == False) :
                #Add empty subledger to show expander for ledgers which have chidren
                self.treestore.append(iter, ("", "", ""))
        
        if ledgers_only == True:
            btn = self.builder.get_object("addsubtoolbutton")
            btn.hide()
        
        self.treeview.set_model(self.treestore)
        self.window.show_all()
        self.builder.connect_signals(self)
        
    def addLedger(self, sender):
        dialog = self.builder.get_object("dialog1")
        hbox = self.builder.get_object("hbox3")
        hbox.hide()
        entry = self.builder.get_object("entry1")
        entry.set_text("")
#        dialog.show_all()
        result = dialog.run()
        if result == 1 :
            if self.builder.get_object("debtor").get_active() == True:
                type = 0
            else:
                if self.builder.get_object("creditor").get_active() == True:
                    type = 1
                else:
                    type = 2
             
            self.saveLedger(unicode(entry.get_text()), type, None, False, dialog)
        dialog.hide()
        
    def addSubLedger(self, sender):
        dialog = self.builder.get_object("dialog1")
        hbox = self.builder.get_object("hbox3")
        hbox.show()
        selection = self.treeview.get_selection()
        parent = selection.get_selected()[1]
        
        if parent != None :
            parentname = self.treestore.get(parent, 1)[0]
            label = self.builder.get_object("label3")
            label.set_text(parentname)
            entry = self.builder.get_object("entry1")
            
            result = dialog.run()
            if result == 1 :
                if self.builder.get_object("debtor").get_active() == True:
                    type = 0
                else:
                    if self.builder.get_object("creditor").get_active() == True:
                        type = 1
                    else:
                        type = 2
                    
                self.saveLedger(unicode(entry.get_text()), type, parent, False, dialog)
            dialog.hide()
        else :
            msgbox =  gtk.MessageDialog(parent, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE,
                                    _("Please select an item from the list, to add subject for it."))
            msgbox.set_title(_("Select a subject"))
            msgbox.run()
            msgbox.destroy()
    
    def editLedger(self, sender):
        dialog = self.builder.get_object("dialog1")
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        
        if iter != None :
            name = self.treestore.get(iter, 1)[0]
            type = self.treestore.get(iter, 2)[0]
            debtor = False
            creditor = False
            both = False
            
            if type == self.__class__.subjecttypes[0]:
                self.builder.get_object("debtor").set_active(True)
            else:
                if type == self.__class__.subjecttypes[1]:
                    self.builder.get_object("creditor").set_active(True)
                else :
                    self.builder.get_object("both").set_active(True) 
            #label = self.builder.get_object("label3")
            #label.set_text(name)
            entry = self.builder.get_object("entry1")
            entry.set_text(name)
            
            hbox = self.builder.get_object("hbox3")
            hbox.hide()
            result = dialog.run()
            
            if result == 1 :
                if self.builder.get_object("debtor").get_active() == True:
                    type = 0
                else:
                    if  self.builder.get_object("creditor").get_active() == True:
                        type = 1
                    else:
                        type = 2
                self.saveLedger(unicode(entry.get_text()), type, iter, True, dialog)
            dialog.hide()
    
    def deleteLedger(self, sender):
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        if iter != None :
            Subject1 = aliased(Subject, name="s1")
            Subject2 = aliased(Subject, name="s2")
            
            code = utility.convertToLatin(self.treestore.get(iter, 0)[0])
            #Check to see if there is any subledger for this ledger.
            query = self.session.query(Subject1.id, count(Subject2.id))
            query = query.select_from(outerjoin(Subject1, Subject2, Subject1.id == Subject2.parent_id))
            result = query.filter(Subject1.code == code).first()
            
            if result[1] != 0 :
                msgbox =  gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE,
                                    _("Subject can not be deleted, because it has some child subjects."))
                msgbox.set_title(_("Error deleting subject"))
                msgbox.run()
                msgbox.destroy()
            else :
                # check to see if there is any document registered for this ledger.
                query = self.session.query(count(Notebook.id))
                query = query.filter(Notebook.subject_id == result[0])
                rowcount = query.first()[0]
                if rowcount != 0 :
                    msgbox =  gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE,
                                    _("Subject can not be deleted, because there are some documents registered for it."))
                    msgbox.set_title(_("Error deleting subject"))
                    msgbox.run()
                    msgbox.destroy()
                else :
                    # Now it's OK to delete ledger
                    row = self.session.query(Subject).filter(Subject.id == result[0]).first()
                    self.session.delete(row)
                    self.session.commit()
                    self.treestore.remove(iter)
    
    def saveLedger(self, name, type, iter, edit, widget):
        if name == "" :
            msgbox = gtk.MessageDialog(widget, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE,
                                    _("Subject name should not be empty."))
            msgbox.set_title(_("Empty subject name"))
            msgbox.run()
            msgbox.destroy()
        else :
            #Check to see if a subject with the given name exists already.
            if iter == None :
                iter_code = ""
                parent_id = 0
            else :
                iter_code = utility.convertToLatin(self.treestore.get(iter, 0)[0])
                query = self.session.query(Subject).select_from(Subject)
                query = query.filter(Subject.code == iter_code)
                sub = query.first()
                if edit == True:
                    iter_id = sub.id
                    parent_id = sub.parent_id
                else : 
                    parent_id = sub.id
                
            query = self.session.query(count(Subject.id)).select_from(Subject)
            query = query.filter(and_(Subject.name == name, Subject.parent_id == parent_id))
            if edit== True:
                query = query.filter(Subject.id != iter_id)
            result = query.first()
            
            if result[0] != 0 :
                msgbox = gtk.MessageDialog(widget, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE,
                                        _("A subject with this name already exists in the current level."))
                msgbox.set_title(_("Duplicate subject name"))
                msgbox.run()
                msgbox.destroy()
            else :
                #Find last subject code.
                if edit == True:
                    query = self.session.query(count(Notebook.id)).select_from(Notebook)
                    query = query.filter(Notebook.subject_id == iter_id)                    
                    rowcount = 0
                    msg = ""
                    if type == 1:
                        rowcounts = query.filter(Notebook.value < 0).first()
                        rowcount = rowcounts[0]
                        msg = _("The type of this subject can not be changed to 'creditor', Because there are \
                                %d documents that use it as debtor.") % rowcount
                    elif type == 0:
                        rowcounts = query.filter(Notebook.value > 0).first()
                        rowcount = rowcounts[0]
                        msg = _("The type of this subject can not be changed to 'debtor', Because there are \
                                %d documents that use it as creditor.") % rowcount
                    if (rowcount > 0):
                        msgbox = gtk.MessageDialog(widget, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, msg)
                        msgbox.set_title(_("Can not change subject type"))
                        msgbox.run()
                        msgbox.destroy()
                        return
                    
                    sub.name = name
                    sub.type = type
                    self.session.commit()
                    self.treestore.set(iter, 1, name, 2, _(self.__class__.subjecttypes[type]))
                else:
                    query = self.session.query(Subject.code).select_from(Subject).order_by(Subject.id.desc())
                    code = query.filter(Subject.parent_id == parent_id).first()
                    if code == None :
                        lastcode = "01"
                    else :
                        lastcode = "%02d" % (int(code[0][-2:]) + 1)
                    
                    lastcode = iter_code + lastcode
                    
                    # If row have not been expanded yet, function 'populateChidren' will be executed and adds children
                    # to the row, then we insert new child in the database and call treeview.append to add it to the 
                    # end of the tree.
                    if iter != None:
                        self.treeview.expand_row(self.treestore.get_path(iter), False)
                        
                    ledger = Subject(lastcode, name, parent_id, type)
                    self.session.add(ledger)
                    self.session.commit()
                    
                    if config.digittype == 1:
                        lastcode = utility.convertToPersian(lastcode)
                    child = self.treestore.append(iter, (lastcode, name, _(self.__class__.subjecttypes[type])))
                    
                    self.temppath = self.treestore.get_path(child)
                    self.treeview.scroll_to_cell(self.temppath, None, False, 0, 0)
                    self.treeview.set_cursor(self.temppath, None, False)
                    
                
    def populateChildren(self, treeview, iter, path):
        chiter = self.treestore.iter_children(iter)
        if chiter != None :
            value = utility.convertToLatin(self.treestore.get(chiter, 0)[0])
            if value == "" :
                value =  utility.convertToLatin(self.treestore.get(iter, 0)[0])
                #remove empty subledger to add real children instead
                self.treestore.remove(chiter)
                
                Sub = aliased(Subject, name="s")
                Child = aliased(Subject, name="c")
                Parent = aliased(Subject, name="p")
                
                query = self.session.query(Sub.code, Sub.name, Sub.type, count(Child.id))
                query = query.select_from(outerjoin(outerjoin(Parent, Sub, Sub.parent_id == Parent.id), Child, Sub.id == Child.parent_id))
                result = query.filter(Parent.code == value).group_by(Sub.id).all()
                for row in result :
                    code = row[0]
                    if config.digittype == 1:
                        code = utility.convertToPersian(code)
                    type = _(self.__class__.subjecttypes[row[2]])
                    chiter = self.treestore.append(iter, (code, row[1], type))
                    if row[3] != 0 :
                        #add empty subledger for those children which have subledgers in turn. (to show expander)
                        self.treestore.append(chiter, ("", "", ""))
        return False
    
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
            
            
    def selectSubjectFromList(self, treeview, path, view_column):
        iter = self.treestore.get_iter(path)
        code = utility.convertToLatin(self.treestore.get(iter, 0)[0])
        name = self.treestore.get(iter, 1)[0]
        
        query = self.session.query(Subject).select_from(Subject)
        query = query.filter(Subject.code == code)
        sub_id = query.first().id
        self.emit("subject-selected", sub_id, code, name)
                            
gobject.type_register(Subjects)
gobject.signal_new("subject-selected", Subjects, gobject.SIGNAL_RUN_LAST,
                   gobject.TYPE_NONE, (gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_STRING))
   
