#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import database
import gettext,locale
import gobject
import os

import subjects
import addeditdoc
import notebookreport
import docreport
import setting
from amirconfig import config
     
class MainWindow:

    def manualDocument(self, sender):
        dialog = addeditdoc.AddEditDoc()

    def quitMainWindow(self, sender):
        pass
    
    def dailyNotebookReport(self, sender):
        reportwin = notebookreport.NotebookReport()
    
    def subjectNotebookReport(self, sender):
        reportwin = notebookreport.NotebookReport(notebookreport.NotebookReport.LEDGER)
            
    def documentReport(self, sender):
        reportwin = docreport.DocumentReport()
        
    def aboutAmir(self, sender):
        pass
    def manageSubjects(self, sender):
        dialog = subjects.Subjects()
        
    def settingsDialog(self, sender):
        window = setting.Setting()
    
    def view_toolbar(self, sender):
        dialog = subjects.Subjects()

    def delete_event(self, widget, event, data=None):
        
     ##TODO uncomment later  
        #=======================================================================
        # msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, "Are you sure to close the app?")
        # msgbox.set_title("Are you sure?")
        # result = msgbox.run();
        # if result == gtk.RESPONSE_CANCEL :
        #    msgbox.destroy()
        #    return True
        # else :
        #    return False
        #=======================================================================

        return False
        # Change FALSE to TRUE and the main window will not be destroyed
        # with a "delete_event".

    def destroy(self, widget, data=None):
        conffile = config.configfile
        conffile.insertStringValue("database", config.db.dbfile)
        gtk.main_quit()

    def __init__(self):
        gobject.threads_init()

        self.builder = gtk.Builder()
        self.builder.set_translation_domain("amir")
        self.builder.add_from_file("../data/ui/mainwin.glade")
        self.window = self.builder.get_object("window1")
        initial = self.builder.get_object("menubar2")
        initial.hide()
        self.builder.connect_signals(self)
        
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(10)
        self.window.show()

    def main(self):
        gtk.main()

if __name__ == "__main__":
     #locale.setlocale(locale.LC_ALL, '')
     #==========================================================================
     # #gettext.install('amir', '/usr/share/locale', unicode=1)
     # #locale.bindtextdomain('amir', '/usr/share/locale')
     # gettext.bindtextdomain('amir', '/usr/share/locale')
     # gettext.textdomain('amir')
     # #lang = gettext.translation('amir', '/usr/share/locale')
     # _ = gettext.gettext
     #==========================================================================
     gettext.install('amir', '/usr/share/locale')


     mainwin = MainWindow()
     mainwin.main()

