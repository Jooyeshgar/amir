import pygtk
import gtk
from datetime import date

import numberentry
import dateentry
import subjects
import utility
from database import *

class NotebookReport:
    
    def __init__(self, subjectfilter=False):
        self.builder = gtk.Builder()
        self.builder.set_translation_domain("amir")
        self.builder.add_from_file("../data/ui/report.glade")
        
        self.window = self.builder.get_object("window1")
        self.window.set_title(_("Daily NoteBook"))
        
        self.code = numberentry.NumberEntry()
        box = self.builder.get_object("codebox")
        box.add(self.code)
        self.code.show()
        
        self.date = dateentry.DateEntry()
        box = self.builder.get_object("datebox")
        box.add(self.date)
        self.date.set_sensitive(False)
        self.date.show()
        
        self.fdate = dateentry.DateEntry()
        box = self.builder.get_object("fdatebox")
        box.add(self.fdate)
        self.fdate.set_sensitive(False)
        self.fdate.show()
        
        self.tdate = dateentry.DateEntry()
        box = self.builder.get_object("tdatebox")
        box.add(self.tdate)
        self.tdate.set_sensitive(False)
        self.tdate.show()
        
        self.fnum = numberentry.NumberEntry()
        box = self.builder.get_object("fnumbox")
        box.add(self.fnum)
        self.fnum.set_sensitive(False)
        self.fnum.show()
        
        self.tnum = numberentry.NumberEntry()
        box = self.builder.get_object("tnumbox")
        box.add(self.tnum)
        self.tnum.set_sensitive(False)
        self.tnum.show()
        
        self.builder.get_object("allcontent").set_active(True)
        
        self.session = db.session
        self.window.show_all()
        self.builder.connect_signals(self)
        
        if subjectfilter == False:
            self.builder.get_object("subjectbox").hide()
            
    def createReport(self):
        if self.builder.get_object("allcontent").get_active() == True:
            pass
        else:
            if self.builder.get_object("atdate").get_active() == True:
                pass
            else:
                if self.builder.get_object("betweendates").get_active() == True:
                    fdate = self.fdate.getDateObject()
                    tdate = self.tdate.getDateObject()
                    if tdate < fdate:
                        msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, 
                                                   "Second date value shouldn't precede the first one.")
                        msgbox.set_title(_("Invalid date order"))
                        msgbox.run()
                        msgbox.destroy()
                        return
                else:
                    fnumber = int(self.fnum.get_text())
                    tnumber = int(self.tnum.get_text())
                    if tnumber < fnumber:
                        msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, 
                                                   "Second document number shouldn't be greater than the first one.")
                        msgbox.set_title(_("Invalid document order"))
                        msgbox.run()
                        msgbox.destroy()
                        return
    
    def previewReport(self, sender):
        self.createReport()
    
    def printReport(self, sender):
        self.createReport()
    
    def exportToCSV(self, sender):
        self.createReport()
    
    def selectSubject(self, sender):
        subject_win = subjects.Subjects()
        subject_win.connect("subject-selected", self.subjectSelected)
    
    def subjectSelected(self, sender, id, code, name):
        self.code.set_text(code)
        sender.window.destroy()
        
    def atdate_toggled(self, sender):
        self.date.set_sensitive(sender.get_active())
        
    def betweendates_toggled(self, sender):
        active = sender.get_active()
        self.fdate.set_sensitive(active)
        self.tdate.set_sensitive(active)
        
    def betweendocs_toggled(self, sender):
        active = sender.get_active()
        self.fnum.set_sensitive(active)
        self.tnum.set_sensitive(active)
    