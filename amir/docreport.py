import pygtk
import gtk
from datetime import date

from sqlalchemy.orm.util import outerjoin
from sqlalchemy.sql import between
from sqlalchemy.sql.functions import sum

import numberentry
import utility
import printreport
from database import *
from dateentry import *
from amirconfig import config

class DocumentReport:
    
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.set_translation_domain("amir")
        self.builder.add_from_file("../data/ui/report.glade")
        
        self.window = self.builder.get_object("window2")
        
        self.number = numberentry.NumberEntry()
        box = self.builder.get_object("numbox")
        box.add(self.number)
        self.number.show()
        
        self.session = config.db.session
        self.window.show_all()
        self.builder.connect_signals(self)

    def createReport(self):
        self.docnumber = self.number.get_text()
        report_header = []
        report_data = []
        col_width = []
        query1 = self.session.query(Bill, Notebook, Subject)
        query1 = query1.select_from(outerjoin(outerjoin(Notebook, Subject, Notebook.subject_id == Subject.id), 
                                            Bill, Notebook.bill_id == Bill.id))
        query1 = query1.filter(Bill.number == int(self.docnumber)).order_by(Notebook.id.asc())
        res = query1.all()
        if len(res) == 0:
            msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, 
                                       _("No document found with the requested number."))
            msgbox.set_title(_("Invalid document number"))
            msgbox.run()
            msgbox.destroy()
            return
        
        self.docdate = res[0][0].date
        report_header = [_("Index"), _("Subject Code"), _("Subject Name"), _("Description"), _("Debt"), _("Credit")]
        col_width = [30, 54, 80, 215, 75, 75 ]
        index = 1
        for b, n, s in res:
            desc = n.desc
            if n.value < 0:
                credit = "0"
                debt = utility.showNumber(-(n.value))
            else:
                credit = utility.showNumber(n.value)
                debt = "0"
                desc = "   " + desc
            report_data.append((str(index), s.code, s.name, desc, debt, credit))
            index += 1
        
        return {"data":report_data, "col-width":col_width ,"heading":report_header}
    
    def previewReport(self, sender):
        self.createReport()
    
    def printReport(self, sender):
        report = self.createReport()
        if report == None:
            return
        #if len(report["data"]) == 0:
        datestr = dateToString(self.docdate)
        printjob = printreport.PrintReport(report["data"], report["col-width"], report["heading"])
        printjob.setHeader(_("Accounting Document"), {_("Document Number"):self.docnumber, _("Date"):datestr})
        printjob.setDrawFunction("drawDocument")
        
        printjob.doPrint()
    
    def exportToCSV(self, sender):
        self.createReport()
