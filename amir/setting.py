from gi.repository import Gtk
import os
from gi.repository import GObject

import class_subject
import upgrade
import database
import dbconfig
import subjects
from share import share
from helpers import get_builder, comboInsertItems
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

config = share.config

class Setting(GObject.GObject):    
    def __init__(self):
        GObject.GObject.__init__(self)
        
        self.builder = get_builder("setting")
        
        self.window = self.builder.get_object("window1")
        
        self.filechooser = self.builder.get_object("filechooser")
        self.filename = self.builder.get_object("filename")
        
        self.treeview = self.builder.get_object("databases-table")
        self.treeview.set_direction(Gtk.TextDirection.LTR)
        self.liststore = Gtk.ListStore(GObject.TYPE_BOOLEAN, str, str)
        # if Gtk.widget_get_default_direction() == Gtk.TextDirection.RTL :
        #     halign = 1
        # else:
        #     halign = 0
            
        crtoggle = Gtk.CellRendererToggle()
        crtoggle.set_radio(True)
#        crtoggle.set_activatable(True)
        crtoggle.connect('toggled', self.changeCurrentDb, 0)
        column = Gtk.TreeViewColumn(_("Current"),  crtoggle, active=0)
        # column.set_alignment(halign)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = Gtk.TreeViewColumn(_("Name"), Gtk.CellRendererText(), text=1)
        # column.set_alignment(halign)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)
        column = Gtk.TreeViewColumn(_("Path"), Gtk.CellRendererText(), text=2)
        # column.set_alignment(halign)
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
        comboInsertItems(self.dateorder, config.dateorders)
        # for order in config.dateorders:
        #     self.dateorder.append_text(order[0] + " - " + order[1] + " - " + order[2])
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
        
        # paper_size = Gtk.paper_size_new_from_ppd(config.paper_ppd, config.paper_name, config.paper_width, config.paper_height)
        self.page_setup = Gtk.PageSetup()
        # self.page_setup.set_paper_size(paper_size)
        self.page_setup.set_orientation(config.paper_orientation)
        self.builder.get_object("papersize").set_text(config.paper_name)

        self.setup_config_tab()    
        self.builder.connect_signals(self)
        
    def changeCurrentDb(self, cell, path, column):
        cpath = self.liststore.get_string_from_iter(self.active_iter)
        if cpath != path:
            iter = self.liststore.get_iter_from_string(path)
            self.liststore.set(self.active_iter, column, False)
            self.liststore.set(iter, column, True)
            self.active_iter = iter
        
    def selectDbFile(self, sender):
        self.filechooser.set_action(Gtk.FileChooserAction.OPEN)
        self.filechooser.set_current_folder (os.path.dirname (config.db.dbfile))
        result = self.filechooser.run()
        if result == Gtk.ResponseType.OK:
            self.filename.set_text(self.filechooser.get_filename())
        self.filechooser.hide()
        
#    def selectOldDatabase(self, sender):
#        self.filechooser.set_action(Gtk.FileChooserAction.OPEN)
#        result = self.filechooser.run()
#        if result == Gtk.ResponseType.OK:
#            self.olddb.set_text(self.filechooser.get_filename())
#        self.filechooser.hide()
#        
#    def selectNewDatabase(self, sender):
#        self.filechooser.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
#        result = self.filechooser.run()
#        if result == Gtk.ResponseType.OK:
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
                result = upgrade.checkInputDb(dbfile)
                if result == -2:
                    msg = _("Can not connect to the database. The selected database file may not be a sqlite database or be corrupt.")
                elif result == 0:
                    msg = _("The selected file is compatible with older versions of Amir. First convert it to the new version.")
            
                if msg != "":  
                    msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, msg)
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
            msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL, 
                                       _("Are you sure to remove this database from the list?"))
            msgbox.set_title(_("Are you sure?"))
            result = msgbox.run()
            msgbox.destroy()
            if result == Gtk.ResponseType.OK :
                self.liststore.remove(iter)
                iter = self.liststore.get_iter_first()
                if iter == None:
                    dbfile = os.path.join(os.path.expanduser('~'), '.amir', 'amir.sqlite')
                    dbname = 'amir.sqlite'
                    msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, 
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
        self.msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.INFO, Gtk.ButtonsType.NONE, msg)
        self.msgbox.set_title(_("Repairing database"))
        self.msgbox.show_all()
        
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)

        GObject.timeout_add(1000, self.repairDbFunc)
        
    def repairDbFunc(self):
        config.db.rebuild_nested_set(0, 0)
                    
        self.msgbox.set_markup(_("Repair Operation Completed!"))
        self.msgbox.add_button(Gtk.STOCK_OK, -5)
        self.msgbox.run()
        self.msgbox.destroy()
        return False

    def applyDatabaseSetting(self, checkV=True):
        active_path = self.liststore.get(self.active_iter, 2)[0]
        dbchanged_flag = False
        if active_path != config.dblist[config.currentdb - 1]:
            msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL, 
                       _("You have changed the current database, any unsaved data will be lost.\nAre you sure to continue?"))
            msgbox.set_title(_("Are you sure?"))
            result = msgbox.run()
            msgbox.destroy()
            if result == Gtk.ResponseType.CANCEL :
                return
            elif checkV:
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
#                msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, msg)
#                msgbox.set_title(_("Error opening new database"))
#                msgbox.run()
#                msgbox.destroy()
#                return
#            else:
#                config.db.session.close()
#                config.db = database.Database(dbfile, config.echodbresult)
#                self.infolabel.set_text(dbfile)
#                
#                msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, 
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
#                msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, msg)
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
#                        msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL, msg)
#                        msgbox.set_title(_("Overwrite destination file?"))
#                        result = msgbox.run()
#                        msgbox.destroy()
#                        if result == Gtk.ResponseType.CANCEL:
#                            return
#                        else:
#                            os.remove(newdb)
#                
#                    msg = _("Please wait...")
#                    self.msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.INFO, Gtk.ButtonsType.NONE, msg)
#                    self.msgbox.set_title(_("Converting database"))
#                    self.msgbox.show_all()
#                    
#                    while Gtk.events_pending():
#                        Gtk.main_iteration_do(False)
##                    upgrade.update(olddb, newdb)
##                    
##                    msgbox.set_markup(_("Convert Operation Completed!\nNew databas: %s") % newdb)
##                    msgbox.set_response_sensitive(-5, True)
##                    msgbox.run()
##                    msgbox.destroy()
#                    GObject.timeout_add(1000, self.updateFunc, olddb, newdb)
#                    return
#                    
#                else:
#                    msg = _("The requested directory doesn't exist.")
#            
#            msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, msg)
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
                Gtk.Widget.set_default_direction(Gtk.TextDirection.RTL)
            else:
                Gtk.Widget.set_default_direction(Gtk.TextDirection.LTR)
            
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
        settings = Gtk.PrintSettings()
        self.page_setup = Gtk.print_run_page_setup_dialog(None, self.page_setup, settings)
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
        config.paper_width = paper_size.get_width(Gtk.Unit.POINTS)
        config.paper_height = paper_size.get_height(Gtk.Unit.POINTS)
        config.paper_orientation = int(self.page_setup.get_orientation())
#        self.page_setup.to_file(config.reportconfig)

    def restoreDefaultsReports(self):
        paper_size = self.page_setup.get_paper_size()
        config.topmargin = int(paper_size.get_default_top_margin(Gtk.Unit.POINTS))
        config.botmargin = int(paper_size.get_default_bottom_margin(Gtk.Unit.POINTS))
        config.rightmargin = int(paper_size.get_default_right_margin(Gtk.Unit.POINTS))
        config.leftmargin = int(paper_size.get_default_left_margin(Gtk.Unit.POINTS))
        
        config.restoreDefaultFonts()
        
        self.builder.get_object("topmargin").set_value(config.topmargin)
        self.builder.get_object("botmargin").set_value(config.botmargin)
        self.builder.get_object("rightmargin").set_value(config.rightmargin)
        self.builder.get_object("leftmargin").set_value(config.leftmargin)
            
        self.builder.get_object("namefont").set_value(config.namefont)
        self.builder.get_object("headerfont").set_value(config.headerfont)
        self.builder.get_object("contentfont").set_value(config.contentfont)
        self.builder.get_object("footerfont").set_value(config.footerfont)
   
    def applyConfigSetting(self):
        conf = dbconfig.dbConfig()
        sub  = class_subject.Subjects()
        
        # self.config_items( 0 => item_id, 1 => get_val function, 2 => exists in subjects)
        for item in self.config_items:
            val = item[1]()
            
            if val == None or val == '':
                #TODO Can be return on empty row
                val = conf.get_default(item[3])
            elif item[2] == True:
                ids = ''
                val = unicode(val)
                for name in val.split(','):
                    ids += '%d,' % sub.get_id_from_name(name)
                val = ids[:-1]
            conf.set_value(item[0], val, False)

        config.db.session.commit()

    def on_cancel_clicked(self, sender):
        self.window.destroy()

    def on_apply_clicked(self, sender):
        self.applyFormatSetting()
        self.applyDatabaseSetting()
        self.applyReportSetting()
        self.applyConfigSetting()

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

    def setup_config_tab(self):
        sub = class_subject.Subjects()
        query = config.db.session.query(database.Config).all()

        company  = self.builder.get_object('company_table')
        subjects = self.builder.get_object('subjects_table')
        others   = self.builder.get_object('others_table')
        company_top = subjects_top = others_top = 0

        destroy = lambda table: [widget.destroy() for widget in table.get_children()]
        destroy(company)
        destroy(subjects)
        destroy(others)
        del destroy

        self.config_items = []

        for row in query:
            if   row.cfgCat == 0:
                table = company
                top = company_top = company_top+1
            elif row.cfgCat == 1:
                table = subjects
                top = subjects_top= subjects_top+1
            else:
                table = others
                top = others_top = others_top+1

            # self.config_items( 0 => item_id, 1 => get_val function, 2 => exists in subjects)
            if   row.cfgType == 0:
                widget = Gtk.FileChooserButton(row.cfgKey)
                filt = Gtk.FileFilter()
                filt.set_name('png,jpg')
                filt.add_pattern('*.png')
                filt.add_pattern('*.jpg')
                widget.add_filter(filt)
                filt = Gtk.FileFilter()
                filt.set_name('All files')
                filt.add_pattern('*')
                widget.add_filter(filt)

                if row.cfgValue != '':
                    widget.set_filename(row.cfgValue)
                self.config_items.append((row.cfgId, widget.get_filename, False,row.cfgKey))
            elif row.cfgType in (1, 2, 3):
                widget = Gtk.Entry()
                if row.cfgType == 1:
                    self.config_items.append((row.cfgId, widget.get_text, False, row.cfgKey))
                else:
                    self.config_items.append((row.cfgId, widget.get_text, True , row.cfgKey))

            widget2 = None
            widget3 = None
            widget4 = None
            if   row.cfgType == 0:
                widget2 = Gtk.Button() # clear button
                widget2.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_CLEAR, Gtk.IconSize.MENU))
                widget2.connect('clicked', lambda widget2, widget: widget.unselect_all(), widget)
            elif row.cfgType == 1:
                widget.set_text(row.cfgValue)
            elif row.cfgType in (2, 3):
                txt = ''
                if len(row.cfgValue) != 0:
                    for id in row.cfgValue.split(','):
                        txt += sub.get_name(id)+','
                    txt = txt[:-1]
                widget.set_text(txt)

                widget.set_sensitive(False)
                widget2 = Gtk.Button()         # clear button
                widget2.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_CLEAR, Gtk.IconSize.MENU))
                widget3 = Gtk.Button('Select') # select button
                if   row.cfgType == 2:
                    multivalue = False
                elif row.cfgType == 3:
                    multivalue = True
                widget2.connect('clicked', lambda button, entry: entry.set_text(''), widget)
                widget3.connect('clicked', self.on_select_button_clicked, widget, multivalue)

            if row.cfgCat == 2:
                widget4 = Gtk.Button()         # Delete Button
                widget4.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_DELETE, Gtk.IconSize.MENU))
                widget4.connect('clicked', self.on_delete_row_clicked, row.cfgId)

            table.attach(Gtk.Label(label=row.cfgKey), 0, 1, top-1, top, Gtk.AttachOptions.SHRINK)
            table.attach(widget, 1, 2, top-1, top)
            if widget2:
                table.attach(widget2, 2, 3, top-1, top, Gtk.AttachOptions.SHRINK)
            if widget3:
                table.attach(widget3, 3, 4, top-1, top, Gtk.AttachOptions.SHRINK)
            if widget4:
                table.attach(widget4, 4, 5, top-1, top, Gtk.AttachOptions.SHRINK)
            table.attach(Gtk.Label(label=row.cfgDesc), 5, 6, top-1, top)
            table.show_all()

        if others_top == 0:
            others.attach(Gtk.Label(), 0, 5, 0, 1, Gtk.AttachOptions.SHRINK)

    def on_delete_row_clicked(self, button, id):
        conf = dbconfig.dbConfig()
        conf.delete(id)
        self.setup_config_tab()

    def on_select_button_clicked(self, button, entry, multivalue):
        sub = subjects.Subjects(multiselect=multivalue)
        if multivalue:
            sub.connect('subject-multi-selected', self.on_subject_multi_selected, entry)
        else:
            sub.connect('subject-selected', self.on_subject_selected, entry)

    def on_subject_selected(self, subject, id, code, name, entry):
        entry.set_text(name)
        subject.window.destroy()

    def on_subject_multi_selected(self, subject, items, entry):
        sub = class_subject.Subjects()
        selected = []

        new_txt = ''
        for item in items:
            name = sub.get_name(item[0])
            new_txt += '%s,' % name
        new_txt = new_txt[:-1]
                
        entry.set_text(new_txt)
        subject.window.destroy()

    def on_conf_key_changed(self, entry):
        add   = self.builder.get_object('add_config')

        entry.set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, None)

        key = entry.get_text()
        if len(key) == 0:
            add.set_sensitive(False)
            return

        conf = dbconfig.dbConfig()
        if conf.exists(key):
            entry.set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, Gtk.STOCK_DIALOG_WARNING)
            entry.set_icon_tooltip_text(Gtk.EntryIconPosition.SECONDARY, 'Key already exists')
            add.set_sensitive(False)
            return

        add.set_sensitive(True)


    def on_add_config_clicked(self, button):
        key  = self.builder.get_object('conf_key').get_text()
        desc = self.builder.get_object('conf_desc').get_text()

        if   self.builder.get_object('conf_mode_file').get_active():
            mode = 0
        elif self.builder.get_object('conf_mode_entry').get_active():
            mode = 1
        elif self.builder.get_object('conf_mode_single_subject').get_active():
            mode = 2
        else:
            mode = 3

        self.builder.get_object('conf_key').set_text('')
        self.builder.get_object('conf_desc').set_text('')
        self.builder.get_object('conf_mode_file').set_active(True)

        conf = dbconfig.dbConfig()
        conf.add(key, mode, desc)

        self.setup_config_tab()

GObject.type_register(Setting)
GObject.signal_new("database-changed", Setting, GObject.SignalFlags.RUN_LAST,
                   None, (GObject.TYPE_STRING,))
GObject.signal_new("dblist-changed", Setting, GObject.SignalFlags.RUN_LAST,
                   None, (GObject.TYPE_STRING,))
GObject.signal_new("locale-changed", Setting, GObject.SignalFlags.RUN_LAST,
                   None, (GObject.TYPE_STRING,))

