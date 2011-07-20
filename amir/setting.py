import pygtk
import gtk
import os
import time
import gobject
from sqlalchemy.orm import sessionmaker

import upgrade
import database
from amirconfig import config
from helpers import get_builder, comboInsertItems

class Setting(gobject.GObject):
    
    def __init__(self):
        gobject.GObject.__init__(self)
        
        self.builder = get_builder("setting")
        
        self.window = self.builder.get_object("window1")
        
        self.filechooser = self.builder.get_object("filechooser")
        self.filename = self.builder.get_object("filename")
        
        self.treeview = self.builder.get_object("databases-table")
        self.treeview.set_direction(gtk.TEXT_DIR_LTR)
        self.liststore = gtk.ListStore(gobject.TYPE_BOOLEAN, str, str)
        if gtk.widget_get_default_direction() == gtk.TEXT_DIR_RTL :
            halign = 1
        else:
            halign = 0
            
        crtoggle = gtk.CellRendererToggle()
        crtoggle.set_radio(True)
#        crtoggle.set_activatable(True)
        crtoggle.connect('toggled', self.changeCurrentDb, 0)
        column = gtk.TreeViewColumn(_("Current"),  crtoggle, active=0)
        column.set_alignment(halign)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = gtk.TreeViewColumn(_("Name"), gtk.CellRendererText(), text=1)
        column.set_alignment(halign)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = gtk.TreeViewColumn(_("Path"), gtk.CellRendererText(), text=2)
        column.set_alignment(halign)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        self.treeview.set_model(self.liststore)
        
        i = 0
        for dbpath in config.dblist:
            if i == config.currentdb - 1:
                self.active_iter = self.liststore.append((True, config.dbnames[i], dbpath))
            else:
                self.liststore.append((False, config.dbnames[i], dbpath))
            i += 1
        
#        self.olddb = self.builder.get_object("olddb")
#        self.newdb = self.builder.get_object("newdb")
        self.infolabel = self.builder.get_object("infolabel")
        
        self.infolabel.set_text(config.db.dbfile)
        
        self.langlist = self.builder.get_object("language")
        comboInsertItems(self.langlist, config.langlist)
        self.langlist.set_active(config.localelist.index(config.locale))
        
        self.dateformat = self.builder.get_object("dateformat")
        comboInsertItems(self.dateformat, config.datetypes)
        self.dateformat.set_active(config.datetype)
        
        self.delimiter = self.builder.get_object("delimiter")
        comboInsertItems(self.delimiter, config.datedelims)
        self.delimiter.set_active(config.datedelim)
        
        self.dateorder = self.builder.get_object("dateorder")
        comboInsertItems(self.dateorder, [])
        for order in config.dateorders:
            self.dateorder.append_text(order[0] + " - " + order[1] + " - " + order[2])
        self.dateorder.set_active(config.dateorder)
        
        self.uselatin = self.builder.get_object("uselatin")
        if config.digittype == 0:
            self.uselatin.set_active(True)
        else:
            self.uselatin.set_active(False)
        
        self.repair_atstart = self.builder.get_object("repair_atstart")
        self.repair_atstart.set_active(config.repair_atstart)
        
        self.builder.get_object("topmargin").set_value(config.topmargin)
        self.builder.get_object("botmargin").set_value(config.botmargin)
        self.builder.get_object("rightmargin").set_value(config.rightmargin)
        self.builder.get_object("leftmargin").set_value(config.leftmargin)
            
        self.builder.get_object("namefont").set_value(config.namefont)
        self.builder.get_object("headerfont").set_value(config.headerfont)
        self.builder.get_object("contentfont").set_value(config.contentfont)
        self.builder.get_object("footerfont").set_value(config.footerfont)
        
        paper_size = gtk.paper_size_new_from_ppd(config.paper_ppd, config.paper_name, config.paper_width, config.paper_height)
        self.page_setup = gtk.PageSetup()
        self.page_setup.set_paper_size(paper_size)
        self.page_setup.set_orientation(config.paper_orientation)
        self.builder.get_object("papersize").set_text(config.paper_name)
        
        self.window.show_all()
        self.builder.connect_signals(self)
        
    def changeCurrentDb(self, cell, path, column):
        cpath = self.liststore.get_string_from_iter(self.active_iter)
        if cpath != path:
            iter = self.liststore.get_iter_from_string(path)
            self.liststore.set(self.active_iter, column, False)
            self.liststore.set(iter, column, True)
            self.active_iter = iter
        
    def selectDbFile(self, sender):
        self.filechooser.set_action(gtk.FILE_CHOOSER_ACTION_OPEN)
        self.filechooser.set_current_folder (os.path.dirname (config.db.dbfile))
        result = self.filechooser.run()
        if result == gtk.RESPONSE_OK:
            self.filename.set_text(self.filechooser.get_filename())
        self.filechooser.hide()
        
#    def selectOldDatabase(self, sender):
#        self.filechooser.set_action(gtk.FILE_CHOOSER_ACTION_OPEN)
#        result = self.filechooser.run()
#        if result == gtk.RESPONSE_OK:
#            self.olddb.set_text(self.filechooser.get_filename())
#        self.filechooser.hide()
#        
#    def selectNewDatabase(self, sender):
#        self.filechooser.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
#        result = self.filechooser.run()
#        if result == gtk.RESPONSE_OK:
#            self.newdb.set_text(self.filechooser.get_filename())
#        self.filechooser.hide()
    
    def addDatabase(self, sender):
        dialog = self.builder.get_object("dialog1")
        dialog.set_title(_("Add Database"))
        self.filename.set_text("")
        result = dialog.run()
        if result == 1 :
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
                else :
                    self.liststore.append((False, self.builder.get_object("dbname").get_text(), dbfile))
        dialog.hide()
    
    def removeDatabase(self, sender):
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        if iter != None :
            msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, 
                                       _("Are you sure to remove this database from the list?"))
            msgbox.set_title(_("Are you sure?"))
            result = msgbox.run()
            msgbox.destroy()
            if result == gtk.RESPONSE_OK :
                self.liststore.remove(iter)
                iter = self.liststore.get_iter_first()
                if iter == None:
                    dbfile = os.path.join(os.path.expanduser('~'), '.amir', 'amir.sqlite')
                    dbname = 'amir.sqlite'
                    msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, 
                                   _("All databases removed.\nThe default database will be opened for use.") )
                    msgbox.set_title(_("All databases removed"))
                    msgbox.run()
                    msgbox.destroy()
                    self.active_iter = self.liststore.append((True, dbname, dbfile))
                else:
                    self.active_iter = iter
                    self.liststore.set(iter, 0, True)
                
               
    def repairDatabaseNow(self, sender):
        msg = _("Please wait...")
        self.msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_NONE, msg)
        self.msgbox.set_title(_("Repairing database"))
        self.msgbox.show_all()
        
        while gtk.events_pending():
            gtk.main_iteration_do(False)

        gobject.timeout_add(1000, self.repairDbFunc)
        
    def repairDbFunc(self):
        config.db.rebuild_nested_set(0, 0)
                    
        self.msgbox.set_markup(_("Repair Operation Completed!"))
        self.msgbox.add_button(gtk.STOCK_OK, -5)
        self.msgbox.run()
        self.msgbox.destroy()
        return False
        
    def applyDatabaseSetting(self):
        active_path = self.liststore.get(self.active_iter, 2)[0]
        dbchanged_flag = False
        if active_path != config.dblist[config.currentdb - 1]:
            msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, 
                       _("You have changed the current database, any unsaved data will be lost.\nAre you sure to continue?"))
            msgbox.set_title(_("Are you sure?"))
            result = msgbox.run()
            msgbox.destroy()
            if result == gtk.RESPONSE_CANCEL :
                return
            else:
                config.db.session.close()
                config.db = database.Database(active_path, config.db_repository, config.echodbresult)
                dbchanged_flag = True
            
        config.repair_atstart = self.repair_atstart.get_active()
        iter = self.liststore.get_iter_first()
        config.dblist = []
        config.dbnames = []
        i = 1
        while iter != None :
            config.dbnames.append(self.liststore.get(iter, 1)[0])
            path = self.liststore.get(iter, 2)[0]
            config.dblist.append(self.liststore.get(iter, 2)[0])
            if path == active_path:
                config.currentdb = i
            iter = self.liststore.iter_next(iter)
            i += 1
            
        if dbchanged_flag == True:
            self.emit("database-changed", active_path)
            
        self.emit("dblist-changed", active_path)
            
#        dbfile = self.filename.get_text()
#        if dbfile != "":
#            msg = ""
#            check = os.path.exists(dbfile)
#            
#            if check == True:
#                result = upgrade.checkInputDb(dbfile)
#                if result == -2:
#                    msg = _("Can not connect to the database. The selected database file may not be a sqlite database or be corrupt.")
#                elif result == 0:
#                    msg = _("The selected file is compatible with older versions of Amir. First convert it to the new version.")
#            else:
#                msg = _("The requested database file doesn' exist.")
#            
#            if msg != "":  
#                msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK, msg)
#                msgbox.set_title(_("Error opening new database"))
#                msgbox.run()
#                msgbox.destroy()
#                return
#            else:
#                config.db.session.close()
#                config.db = database.Database(dbfile, config.echodbresult)
#                self.infolabel.set_text(dbfile)
#                
#                msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, 
#                                   _("Database changed successfully.\nNew database: %s") % dbfile )
#                msgbox.set_title(_("Successfully changed"))
#                msgbox.run()
#                msgbox.destroy()

        
        
#        olddb = self.olddb.get_text()
#        newdb = self.newdb.get_text()
#        if olddb != "":
#            msg = ""
#            check = os.path.exists(olddb)
#            if check == True:
#                result = upgrade.checkInputDb(olddb)
#                if result == -2:
#                    msg = _("Can not connect to the database. The selected file for convert may not be a sqlite database or be corrupt.")
#                elif result != 0:
#                    msg = _("The selected file is not compatible with older versions of Amir.")
#            else:
#                msg = _("The requested database file doesn't exist.")
#                
#            if msg != "":  
#                msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK, msg)
#                msgbox.set_title(_("Error opening database for conversion"))
#                msgbox.run()
#                msgbox.destroy()
#                return
#            
#            (ofpath, ofname) = os.path.split(olddb)
#            (ofshortname, ofext) = os.path.splitext(ofname)
#            msg = ""
#            res = False
#            if newdb == "":
#                msg = _("Please select a directory for the converted database.")
#            else:
#                check = os.path.exists(newdb)
#                if check == True:
#                    newdb = os.path.join(newdb, ofshortname + ".db")
#                    check = os.path.exists(newdb)
#                    if check == True:
#                        msg = _("File %s already exists in destination directory, Do you want to overwrite it?") % (ofshortname + ".db")
#                        msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, msg)
#                        msgbox.set_title(_("Overwrite destination file?"))
#                        result = msgbox.run()
#                        msgbox.destroy()
#                        if result == gtk.RESPONSE_CANCEL:
#                            return
#                        else:
#                            os.remove(newdb)
#                
#                    msg = _("Please wait...")
#                    self.msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_NONE, msg)
#                    self.msgbox.set_title(_("Converting database"))
#                    self.msgbox.show_all()
#                    
#                    while gtk.events_pending():
#                        gtk.main_iteration_do(False)
##                    upgrade.update(olddb, newdb)
##                    
##                    msgbox.set_markup(_("Convert Operation Completed!\nNew databas: %s") % newdb)
##                    msgbox.set_response_sensitive(-5, True)
##                    msgbox.run()
##                    msgbox.destroy()
#                    gobject.timeout_add(1000, self.updateFunc, olddb, newdb)
#                    return
#                    
#                else:
#                    msg = _("The requested directory doesn't exist.")
#            
#            msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK, msg)
#            msgbox.set_title(_("Error opening destination"))
#            msgbox.run()
#            msgbox.destroy()
#            return

    def applyFormatSetting(self):
        langindex = self.langlist.get_active()
        if langindex != config.localelist.index(config.locale):
            config.locale = config.localelist[langindex]
            self.emit("locale-changed", config.locale)
            
            if config.directionlist[langindex] == "rtl":
                gtk.widget_set_default_direction(gtk.TEXT_DIR_RTL)
            else:
                gtk.widget_set_default_direction(gtk.TEXT_DIR_LTR)
            
        config.datetype = self.dateformat.get_active()
        config.datedelim = self.delimiter.get_active()
        config.dateorder = self.dateorder.get_active()
        for i in range(0,3):
            field = config.dateorders[config.dateorder][i]
            config.datefields[field] = i
        if self.uselatin.get_active() == True:
            config.digittype = 0
        else:
            config.digittype = 1
            
    def reportPaperSetup(self, sender):
        settings = gtk.PrintSettings()
        self.page_setup = gtk.print_run_page_setup_dialog(None, self.page_setup, settings)
        self.builder.get_object("papersize").set_text(self.page_setup.get_paper_size().get_display_name())
        
    def applyReportSetting(self):
        config.topmargin = self.builder.get_object("topmargin").get_value_as_int()
        config.botmargin = self.builder.get_object("botmargin").get_value_as_int()
        config.rightmargin = self.builder.get_object("rightmargin").get_value_as_int()
        config.leftmargin = self.builder.get_object("leftmargin").get_value_as_int()
        
        config.namefont = self.builder.get_object("namefont").get_value_as_int()
        config.headerfont = self.builder.get_object("headerfont").get_value_as_int()
        config.contentfont = self.builder.get_object("contentfont").get_value_as_int()
        config.footerfont = self.builder.get_object("footerfont").get_value_as_int()
        
        paper_size = self.page_setup.get_paper_size()
        config.paper_ppd = paper_size.get_ppd_name()
        config.paper_name = paper_size.get_display_name()
        config.paper_width = paper_size.get_width(gtk.UNIT_POINTS)
        config.paper_height = paper_size.get_height(gtk.UNIT_POINTS)
        config.paper_orientation = int(self.page_setup.get_orientation())
#        self.page_setup.to_file(config.reportconfig)

    def restoreDefaultsReports(self):
        paper_size = self.page_setup.get_paper_size()
        config.topmargin = int(paper_size.get_default_top_margin(gtk.UNIT_POINTS))
        config.botmargin = int(paper_size.get_default_bottom_margin(gtk.UNIT_POINTS))
        config.rightmargin = int(paper_size.get_default_right_margin(gtk.UNIT_POINTS))
        config.leftmargin = int(paper_size.get_default_left_margin(gtk.UNIT_POINTS))
        
        config.restoreDefaultFonts()
        
        self.builder.get_object("topmargin").set_value(config.topmargin)
        self.builder.get_object("botmargin").set_value(config.botmargin)
        self.builder.get_object("rightmargin").set_value(config.rightmargin)
        self.builder.get_object("leftmargin").set_value(config.leftmargin)
            
        self.builder.get_object("namefont").set_value(config.namefont)
        self.builder.get_object("headerfont").set_value(config.headerfont)
        self.builder.get_object("contentfont").set_value(config.contentfont)
        self.builder.get_object("footerfont").set_value(config.footerfont)
   
    def on_cancel_clicked(self, sender):
        self.window.destroy()

    def on_apply_clicked(self, sender):
        self.applyFormatSetting()
        self.applyDatabaseSetting()
        self.applyReportSetting()

    def on_ok_clicked(self, sender):
        self.on_apply_clicked(None)
        self.window.destroy()

    def on_defaults_clicked(self, sender):
        pagenum = self.builder.get_object('notebook1').get_current_page()
        self.restoreDefaultsReports()

    def on_notebook1_switch_page(self, notebook, page, pagenum):
        defaults = self.builder.get_object('defaults')
        if pagenum == 2:
            defaults.set_sensitive(True)
        else:
            defaults.set_sensitive(False)

gobject.type_register(Setting)
gobject.signal_new("database-changed", Setting, gobject.SIGNAL_RUN_LAST,
                   gobject.TYPE_NONE, (gobject.TYPE_STRING,))
gobject.signal_new("dblist-changed", Setting, gobject.SIGNAL_RUN_LAST,
                   gobject.TYPE_NONE, (gobject.TYPE_STRING,))
gobject.signal_new("locale-changed", Setting, gobject.SIGNAL_RUN_LAST,
                   gobject.TYPE_NONE, (gobject.TYPE_STRING,))
