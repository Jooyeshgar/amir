import pygtk
import gtk
from datetime import date

from sqlalchemy import or_
from sqlalchemy.orm.util import outerjoin
from sqlalchemy.sql import between
from sqlalchemy.sql.functions import sum
from sqlalchemy.sql.expression import ColumnOperators

import numberentry
import subjects
import utility
import printreport
from database import *
from dateentry import *
from amirconfig import config
from helpers import get_builder

class NotebookReport:
    DAILY = 1
    LEDGER = 2
    SUBLEDGER = 3
    
    def __init__(self, type=1):
        self.builder = get_builder("report")
        
        self.window = self.builder.get_object("window1")
        self.window.set_title(_("Daily NoteBook"))
        
        self.code = numberentry.NumberEntry()
        box = self.builder.get_object("codebox")
        box.add(self.code)
        self.code.show()
        self.code.connect("activate", self.selectSubject)
        
        self.date = DateEntry()
        box = self.builder.get_object("datebox")
        box.add(self.date)
        self.date.set_sensitive(False)
        self.date.set_activates_default(True)
        self.date.show()
        
        self.fdate = DateEntry()
        box = self.builder.get_object("fdatebox")
        box.add(self.fdate)
        self.fdate.set_sensitive(False)
        self.fdate.set_activates_default(True)
        self.fdate.show()
        
        self.tdate = DateEntry()
        box = self.builder.get_object("tdatebox")
        box.add(self.tdate)
        self.tdate.set_sensitive(False)
        self.tdate.set_activates_default(True)
        self.tdate.show()
        
        self.fnum = numberentry.NumberEntry()
        box = self.builder.get_object("fnumbox")
        box.add(self.fnum)
        self.fnum.set_sensitive(False)
        self.fnum.set_activates_default(True)
        self.fnum.show()
        
        self.tnum = numberentry.NumberEntry()
        box = self.builder.get_object("tnumbox")
        box.add(self.tnum)
        self.tnum.set_sensitive(False)
        self.tnum.set_activates_default(True)
        self.tnum.show()
        
        self.builder.get_object("allcontent").set_active(True)
        
        self.type = type
        self.subcode = ""
        self.subname = ""
        
        self.session = config.db.session
        self.window.show_all()
        self.builder.connect_signals(self)
        
        if type == self.__class__.DAILY:
            self.builder.get_object("subjectbox").hide()
            
    def createReport(self):
        report_header = []
        report_data = []
        col_width = []
        remaining = 0
        query1 = self.session.query(Notebook, Subject.code, Bill)
        query1 = query1.select_from(outerjoin(outerjoin(Notebook, Subject, Notebook.subject_id == Subject.id), 
                                            Bill, Notebook.bill_id == Bill.id))
        query2 = self.session.query(sum(Notebook.value)).select_from(outerjoin(Notebook, Bill, Notebook.bill_id == Bill.id))
        
        # Check if the subject code is valid in ledger and subledger reports
        if self.type != self.__class__.DAILY:
            code = utility.convertToLatin(self.code.get_text())
            query3 = self.session.query(Subject.name)
            query3 = query3.select_from(Subject).filter(Subject.code == code)
            names = query3.first()
            if names == None:
                errorstr = _("No subject is registered with the code: %s") % self.code.get_text()
                msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK, errorstr)
                msgbox.set_title(_("No subjects found"))
                msgbox.run()
                msgbox.destroy()
                return
            else:
                self.subname = names[0]
                self.subcode = code
                query1 = query1.filter(Subject.code.startswith(code))
                query2 = query2.filter(Subject.code.startswith(code))
            
        searchkey = unicode(self.builder.get_object("searchentry").get_text())
        if searchkey != "":
            try:
                value = int(utility.convertToLatin(searchkey))
            except UnicodeEncodeError:
                value = 0
                
            if value != 0:
                query1 = query1.filter(or_(Notebook.desc.match(searchkey), Notebook.value == value))
            else:
                query1 = query1.filter(Notebook.desc.match(searchkey))        
        # Check the report parameters  
        if self.builder.get_object("allcontent").get_active() == True:
            query1 = query1.order_by(Bill.date.asc(), Bill.number.asc())
            remaining = 0
        else:
            if self.builder.get_object("atdate").get_active() == True:
                date = self.date.getDateObject()
                query1 = query1.filter(Bill.date == date).order_by(Bill.number.asc())
                query2 = query2.filter(Bill.date < date)
            else:
                if self.builder.get_object("betweendates").get_active() == True:
                    fdate = self.fdate.getDateObject()
                    tdate = self.tdate.getDateObject()
                    if tdate < fdate:
                        msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, 
                                                   _("Second date value shouldn't precede the first one."))
                        msgbox.set_title(_("Invalid date order"))
                        msgbox.run()
                        msgbox.destroy()
                        return
                    query1 = query1.filter(Bill.date.between(fdate, tdate)).order_by(Bill.date.asc(), Bill.number.asc())
                    query2 = query2.filter(Bill.date < fdate)
                else:
                    fnumber = int(unicode(self.fnum.get_text()))
                    tnumber = int(unicode(self.tnum.get_text()))
                    if tnumber < fnumber:
                        msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, 
                                                   _("Second document number shouldn't be greater than the first one."))
                        msgbox.set_title(_("Invalid document order"))
                        msgbox.run()
                        msgbox.destroy()
                        return
                    query1 = query1.filter(Bill.number.between(fnumber, tnumber)).order_by(Bill.date.asc(), Bill.number.asc())
                    query2 = query2.filter(Bill.number < fnumber)
        
        #Prepare report data for PrintReport class
        res = query1.all()
        if self.type == self.__class__.DAILY:
            report_header = [_("Doc. Number"), _("Date"), _("Subject Code"), _("Description"), _("Debt"), _("Credit")]
            col_width = [55, 56, 58, 220, 70, 70 ]
            for n, code, b in res:
                desc = n.desc
                if n.value < 0:
                    credit = utility.convertToPersian("0")
                    debt = utility.showNumber(-(n.value))
                else:
                    credit = utility.showNumber(n.value)
                    debt = utility.convertToPersian("0")
                    desc = "   " + desc
                
                billnumber = str(b.number)   
                if config.digittype == 1:
                    code = utility.convertToPersian(code)
                    billnumber = utility.convertToPersian(billnumber)
                report_data.append((billnumber, dateToString(b.date), code, desc, debt, credit))
        else:
            remaining = query2.first()[0]
            diagnose = ""
            
            #if self.type == self.__class__.LEDGER:
            report_header = [_("Doc. Number"), _("Date"), _("Description"), _("Debt"), _("Credit"), _("Diagnosis"), _("Remaining")]
            col_width = [55, 56, 182, 70, 70, 20, 70]
            for n, code, b in res:
                if n.value < 0:
                    credit = utility.convertToPersian("0")
                    debt = utility.showNumber(-(n.value))
                else:
                    credit = utility.showNumber(n.value)
                    debt = utility.convertToPersian("0")
                    
                remaining += n.value
                billnumber = str(b.number)
                if config.digittype == 1:
                    billnumber = utility.convertToPersian(billnumber)
                if remaining < 0:
                    diagnose = _("deb")
                    report_data.append((billnumber, dateToString(b.date), n.desc, debt, credit, diagnose, utility.showNumber(-(remaining))))
                else:
                    if remaining == 0:
                        diagnose = _("equ")
                    else:
                        diagnose = _("cre")
                    report_data.append((billnumber, dateToString(b.date), n.desc, debt, credit, diagnose, utility.showNumber(remaining)))
    
#            else:
#                if self.type == self.__class__.SUBLEDGER:
#                    report_header = [_("Doc. Number"), _("Date"), _("Description"), _("Debt"), _("Credit"), _("Diagnosis"), _("Remaining")]
#                    col_width = [55, 64, 174, 70, 70, 20, 70]
#                    for n, code, b in res:
#                        if n.value < 0:
#                            credit = "0"
#                            debt = utility.showNumber(-(n.value))
#                        else:
#                            credit = utility.showNumber(n.value)
#                            debt = "0"
#
#                        remaining += n.value
#                        if remaining < 0:
#                            diagnose = _("deb")
#                            report_data.append((str(b.number), dateToString(b.date), n.desc, debt, credit, diagnose, utility.showNumber(-(remaining))))
#                        else:
#                            if remaining == 0:
#                                diagnose = _("equ")
#                            else:
#                                diagnose = _("cre")
#                            report_data.append((str(b.number), dateToString(b.date), n.desc, debt, credit, diagnose, utility.showNumber(remaining)))

        return {"data":report_data, "col-width":col_width ,"heading":report_header}
                
    def createPrintJob(self):
        report = self.createReport()
        if report == None:
            return
        if len(report["data"]) == 0:
            msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, 
                                       _("The requested notebook is empty."))
            msgbox.set_title(_("Empty notebook"))
            msgbox.run()
            msgbox.destroy()
            return
        
        printjob = printreport.PrintReport(report["data"], report["col-width"], report["heading"])
        if self.type == self.__class__.DAILY:
            todaystr = dateToString(date.today())
            printjob.setHeader(_("Daily Notebook"), {_("Date"):todaystr})
            printjob.setDrawFunction("drawDailyNotebook")
        else:
            if config.digittype == 1:
                code = utility.convertToPersian(self.subcode)
            else:
                code = self.subcode
                
            if self.type == self.__class__.LEDGER:
                printjob.setHeader(_("Ledger Notebook"), {_("Subject Name"):self.subname, _("Subject Code"):code})
            else:
                printjob.setHeader(_("Sub-Leger Notebook"), {_("Subject Name"):self.subname, _("Subject Code"):code})
            printjob.setDrawFunction("drawSubjectNotebook")
        return printjob
            
    def previewReport(self, sender):
        printjob = self.createPrintJob()
        if printjob != None:
            printjob.doPrintJob(gtk.PRINT_OPERATION_ACTION_PREVIEW)
    
    def printReport(self, sender):
        printjob = self.createPrintJob()
        if printjob != None:
            printjob.doPrintJob(gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG)
        
    def exportToCSV(self, sender):
        self.createReport()
    
    def selectSubject(self, sender):
        if self.type == self.__class__.LEDGER:
            subject_win = subjects.Subjects(True)
        else:
            subject_win = subjects.Subjects()
        subject_win.connect("subject-selected", self.subjectSelected)
    
    def subjectSelected(self, sender, id, code, name):
        if config.digittype == 1:
            code = utility.convertToPersian(code)
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
    
