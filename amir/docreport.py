import pygtk
import gtk
from datetime import date
import os
import platform
import re

from sqlalchemy.orm.util import outerjoin
from sqlalchemy.sql import between
from sqlalchemy.sql.functions import sum

import numberentry
import utility
import printreport
import previewreport
from database import *
from dateentry import *
from share import share
from helpers import get_builder

config = share.config

class DocumentReport:
    
    def __init__(self):
        self.builder = get_builder("report")
        
        self.window = self.builder.get_object("window2")
        
        self.number = gtk.Entry(max=0) #numberentry.NumberEntry()
        box = self.builder.get_object("numbox")
        box.add(self.number)
        self.number.set_activates_default(True)
        self.number.show()
        
        config.db.session = config.db.session
        self.window.show_all()
        self.builder.connect_signals(self)

    def createReport(self):
        number = unicode(self.number.get_text())
        
        if re.match('^\d+$', number) != None:
            self.docnumbers=[int(number)]
        elif re.match('^(\d+)-(\d+)$', number) != None:
            m = re.match('^(\d+)-(\d+)$', number)
            self.docnumbers=range(int(m.group(1)),int(m.group(2))+1)
        else:
            print 'error'
            return
        
#        self.docnumber = self.number.get_text()
#        if self.docnumber == "":
#            return
        
        report_header = []
        report_data = []
        col_width = []
        debt_sum = 0
        credit_sum = 0
        query1 = config.db.session.query(Bill, Notebook, Subject)
        query1 = query1.select_from(outerjoin(outerjoin(Notebook, Subject, Notebook.subject_id == Subject.id), Bill, Notebook.bill_id == Bill.id))
        query1 = query1.filter(Bill.number.in_(self.docnumbers)).order_by(Bill.number.asc(),Notebook.id.asc())
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
        #define the percentage of table width that each column needs
        col_width = [5, 11, 15, 43, 13, 13 ]
        index = 1
        doc_number0 = 0
        for b, n, s in res:
            desc = n.desc
            if n.value < 0:
                credit = utility.LN(0)
                debt = utility.LN(-(n.value))
            else:
                credit = utility.LN(n.value)
                debt = utility.LN(0)
                desc = "   " + desc
                
            code = utility.LN(s.code)
            doc_number = utility.LN(b.number)
            if doc_number != doc_number0:
                index = 1
                debt_sum = 0
                credit_sum = 0
            debt_sum += int(debt.replace(",", ""))
            credit_sum += int(credit.replace(",", ""))
            strindex = utility.LN(str(index))
            doc_number0 = doc_number
            date = dateToString(b.date)
            report_data.append((strindex, code, s.name, desc, debt, credit, doc_number, date, debt_sum, credit_sum))
            index += 1
        
        return {"data":report_data, "col-width":col_width ,"heading":report_header}
    
    def createPrintJob(self):
        report = self.createReport()
        if report == None:
            return
        #if len(report["data"]) == 0:
        datestr = dateToString(self.docdate)
        docnumber = self.docnumbers[0]
        if config.digittype == 1:
            docnumber = utility.convertToPersian(docnumber)
            
        printjob = printreport.PrintReport(report["data"], report["col-width"], report["heading"])
        printjob.setHeader(_("Accounting Document"), {_("Document Number"):docnumber, _("Date"):datestr})
        printjob.setDrawFunction("drawDocument")
        return printjob
    
    def createPreviewJob(self):
        report = self.createReport()
        if report == None:
            return
        #if len(report["data"]) == 0:
        datestr = dateToString(self.docdate)
        docnumber = self.docnumber
        if config.digittype == 1:
            docnumber = utility.convertToPersian(docnumber)
            
        preview = previewreport.PreviewReport(report["data"], report["heading"])
        #preview.setHeader(_("Accounting Document"), {_("Document Number"):docnumber, _("Date"):datestr})
        preview.setDrawFunction("drawDocument")
        return preview
    
    def previewReport(self, sender):
        if platform.system() == 'Windows':
            printjob = self.createPreviewJob()
            if printjob != None:
                printjob.doPreviewJob()
        else:
            printjob = self.createPrintJob()
            if printjob != None:
                printjob.doPrintJob(gtk.PRINT_OPERATION_ACTION_PREVIEW)
    
    def printReport(self, sender):
        printjob = self.createPrintJob()
        if printjob != None:
            printjob.doPrintJob(gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG)
    
    def exportToCSV(self, sender):
        report = self.createReport()
        if report == None:
            return
        
        content = ""
        for key in report["heading"]:
            content += key.replace(",", "") + ","
        content += "\n"
           
        for data in report["data"]:
            for item in data:
                content += item.replace(",", "") + ","
            content += "\n"
            
        dialog = gtk.FileChooserDialog(None, self.window, gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                                                                         gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))
        dialog.run()
        filename = os.path.splitext(dialog.get_filename())[0]
        file = open(filename + ".csv", "w")
        file.write(content)
        file.close()
        dialog.destroy()
