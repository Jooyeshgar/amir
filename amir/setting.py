import pygtk
import gtk
import os
import time
import gobject
from sqlalchemy.orm import sessionmaker

import upgrade
import database
from amirconfig import config

class Setting:
    
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.set_translation_domain("amir")
        self.builder.add_from_file("../data/ui/setting.glade")
        self.window = self.builder.get_object("window1")
        
        self.filechooser = self.builder.get_object("filechooser")
        self.filename = self.builder.get_object("filename")
        self.olddb = self.builder.get_object("olddb")
        self.newdb = self.builder.get_object("newdb")
        self.infolabel = self.builder.get_object("infolabel")
        
        self.infolabel.set_text(self.infolabel.get_text() + config.db.dbfile)
        
        self.window.show_all()
        self.builder.connect_signals(self)
        
    def selectDbFile(self, sender):
        self.filechooser.set_action(gtk.FILE_CHOOSER_ACTION_OPEN)
        result = self.filechooser.run()
        if result == gtk.RESPONSE_OK:
            self.filename.set_text(self.filechooser.get_filename())
        self.filechooser.hide()
        
    def selectOldDatabase(self, sender):
        self.filechooser.set_action(gtk.FILE_CHOOSER_ACTION_OPEN)
        result = self.filechooser.run()
        if result == gtk.RESPONSE_OK:
            self.olddb.set_text(self.filechooser.get_filename())
        self.filechooser.hide()
        
    def selectNewDatabase(self, sender):
        self.filechooser.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        result = self.filechooser.run()
        if result == gtk.RESPONSE_OK:
            self.newdb.set_text(self.filechooser.get_filename())
        self.filechooser.hide()
            
    def applyDatabaseSetting(self, sender):
        dbfile = self.filename.get_text()
        if dbfile != "":
            msg = ""
            check = os.path.exists(dbfile)
            
            if check == True:
                result = upgrade.checkInputDb(dbfile)
                if result == -2:
                    msg = _("Can not connect to the database. The selected database file may not be a sqlite database or be corrupt.")
                elif result == 0:
                    msg = _("The selected file is compatible with older versions of Amir. First convert it to the new version.")
            else:
                msg = _("The requested database file doesn' exist.")
            
            if msg != "":  
                msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK, msg)
                msgbox.set_title(_("Error opening new database"))
                msgbox.run()
                msgbox.destroy()
                return
            else:
                config.db.session.close()
                config.db = database.Database(dbfile, config.echodbresult)
                self.infolabel.set_text(self.infolabel.get_text() + dbfile)
        
        olddb = self.olddb.get_text()
        newdb = self.newdb.get_text()
        if olddb != "":
            msg = ""
            check = os.path.exists(olddb)
            if check == True:
                result = upgrade.checkInputDb(olddb)
                if result == -2:
                    msg = _("Can not connect to the database. The selected file for convert may not be a sqlite database or be corrupt.")
                elif result != 0:
                    msg = _("The selected file is not compatible with older versions of Amir.")
            else:
                msg = _("The requested database file doesn't exist.")
                
            if msg != "":  
                msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK, msg)
                msgbox.set_title(_("Error opening database for conversion"))
                msgbox.run()
                msgbox.destroy()
                return
            
            (ofpath, ofname) = os.path.split(olddb)
            (ofshortname, ofext) = os.path.splitext(ofname)
            msg = ""
            res = False
            if newdb == "":
                msg = _("Please select a directory for the converted database.")
            else:
                check = os.path.exists(newdb)
                if check == True:
                    newdb = os.path.join(newdb, ofshortname + ".db")
                    check = os.path.exists(newdb)
                    if check == True:
                        msg = _("File %s already exists in destination directory, Do you want to overwrite it?") % (ofshortname + ".db")
                        msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, msg)
                        msgbox.set_title(_("Overwrite destination file?"))
                        result = msgbox.run()
                        msgbox.destroy()
                        if result == gtk.RESPONSE_CANCEL:
                            return
                        else:
                            os.remove(newdb)
                
                    msg = _("Please wait..")
                    self.msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_NONE, msg)
                    self.msgbox.set_title(_("Converting database"))
                    self.msgbox.show_all()
                    
                    while gtk.events_pending():
                        gtk.main_iteration_do(False)
#                    upgrade.update(olddb, newdb)
#                    
#                    msgbox.set_markup(_("Convert Operation Completed!\nNew databas: %s") % newdb)
#                    msgbox.set_response_sensitive(-5, True)
#                    msgbox.run()
#                    msgbox.destroy()
                    gobject.timeout_add(1000, self.updateFunc, olddb, newdb)
                    return
                    
                else:
                    msg = _("The requested directory doesn't exist.")
            
            msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK, msg)
            msgbox.set_title(_("Error opening destination"))
            msgbox.run()
            msgbox.destroy()
            return

    def updateFunc(self, inputfile, outputfile):
        upgrade.update(inputfile, outputfile)
                    
        self.msgbox.set_markup(_("Convert Operation Completed!\nNew database: %s") % outputfile)
        self.msgbox.add_button(gtk.STOCK_OK, -5)
        self.msgbox.run()
        self.msgbox.destroy()
        return False
