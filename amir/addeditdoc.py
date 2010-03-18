import pygtk
import gtk
from database import *
import numberentry
from amir.amirconfig import config

class AddEditDoc:
    
    def __init__(self, number=0):
        self.builder = gtk.Builder()
        self.builder.set_translation_domain("amir")
        self.builder.add_from_file("../data/document.glade")
        
        self.window = self.builder.get_object("window1")
        
        self.treeview = self.builder.get_object("treeview")
        self.treestore = gtk.TreeStore(int, str, str, str, str, str)
        
        column = gtk.TreeViewColumn(_("Index"), gtk.CellRendererText(), text=0)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = gtk.TreeViewColumn(_("Subject Code"), gtk.CellRendererText(), text=1)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = gtk.TreeViewColumn(_("Subject Name"), gtk.CellRendererText(), text=2)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = gtk.TreeViewColumn(_("Debt"), gtk.CellRendererText(), text=3)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = gtk.TreeViewColumn(_("Credit"), gtk.CellRendererText(), text=4)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = gtk.TreeViewColumn(_("Description"), gtk.CellRendererText(), text=5)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)

        self.treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        
        self.session = db.session
        
        self.treeview.set_model(self.treestore)
        self.window.show_all()
        self.builder.connect_signals(self)
        
    def addRow(self, sender):
        dialog = self.builder.get_object("dialog1")
        dialog.set_title(_("Add new row"))
        
        number = numberentry.NumberEntry()
        box = self.builder.get_object("hbox2")
        box.add(number)
        number.show()
        
        code = self.builder.get_object("code")
        amount = self.builder.get_object("amount")
        desc = self.builder.get_object("desc")
        
        result = dialog.run()
        if result == 1:
            saveRow(code.get_text(), amount.get_text(), desc.get_text())
        
        dialog.hide()
    
    def editRow(self, sender):
        dialog = self.builder.get_object("dialog1")
        dialog.set_title(_("Edit row"))
        
        code = self.builder.get_object("code")
        amount = self.builder.get_object("amount")
        desc = self.builder.get_object("desc")
        
        result = dialog.run()
        if result == 1:
            saveRow(code.get_text(), amount.get_text(), desc.get_text())
        
        dialog.hide()
    
    def saveRow(self, code, amount, desc):
        pass
    
    def deleteRow(self, sender):
        pass
    
    def saveDocument(self, sender):
        pass
