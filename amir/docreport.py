import gi
from gi.repository import Gtk
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
from weasyprintreport import *

config = share.config

class DocumentReport:
    
    def __init__(self):
        self.builder = get_builder("report")
        
        self.window = self.builder.get_object("window2")
        
        self.number = Gtk.Entry() #numberentry.NumberEntry()
        box = self.builder.get_object("numbox")
        box.add(self.number)
        self.number.set_activates_default(True)
        self.number.show()
        self.builder.get_object("message").set_text("")
        self.window.show_all()
        self.builder.get_object("buttonPreview").connect( "clicked", self.previewReport)
        self.builder.get_object("buttonExport").connect( "clicked", self.exportToCSV)
        self.builder.get_object("buttonPrint").connect( "clicked", self.printReport)       

    def createReport(self):
        number = unicode(self.number.get_text())
        
        if re.match('^\d+$', number) != None:
            self.docnumbers=[int(number)]
        elif re.match('^(\d+)-(\d+)$', number) != None:
            m = re.match('^(\d+)-(\d+)$', number)
            self.docnumbers=range(int(m.group(1)),int(m.group(2))+1)
        else:
            self.builder.get_object("message").set_text( _("Please enter number in correct format \r\nTrue Formats: '2-11' or '2'  ") )
            return
        
        self.builder.get_object("message").set_text("")
        report_header = []
        report_data = []
        #col_width = []
        debt_sum = 0
        credit_sum = 0
        query1 = config.db.session.query(Bill, Notebook, Subject)
        query1 = query1.select_from(outerjoin(outerjoin(Notebook, Subject, Notebook.subject_id == Subject.id), Bill, Notebook.bill_id == Bill.id))
        query1 = query1.filter(Bill.number.in_(self.docnumbers)).order_by(Bill.number.asc(),Notebook.id.asc())
        res = query1.all()
        if len(res) == 0:
            msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, 
                                       _("No document found with the requested number."))
            msgbox.set_title(_("Invalid document number"))
            msgbox.run()
            msgbox.destroy()
            return
        
        self.docdate = res[0][0].date
        report_header = [_("Document No."),_("Index"), _("Date"), _("Subject Code"), _("Subject Name"), _("Description"), _("Debt"), _("Credit")]
        index = 1
        debt_sum = credit_sum = doc_number0 = 0
        prevDoc = res[0][0].number
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
                if doc_number0:
                    report_data.append((doc_number0, str(index), "-", "-" , "-", "Total", utility.LN(debt_sum), utility.LN(credit_sum)) )
                index = 1
                debt_sum = 0
                credit_sum = 0
            debt_sum += utility.getFloatNumber(debt)
            credit_sum += utility.getFloatNumber(credit)            
            doc_number0 = doc_number
            date = dateToString(b.date)
            report_data.append((doc_number, str(index), date, code, s.name, desc, debt, credit))
            index += 1        
            prevDoc = b.number
        report_data.append((doc_number, str(index), "-", "-" , "-", "Total", utility.LN(debt_sum), utility.LN(credit_sum)) )
        return {"data":report_data ,"heading":report_header}
    
    def createPrintJob(self):
        report = self.createReport()
        if report == None:
            return
        #if len(report["data"]) == 0:
        datestr = dateToString(self.docdate)
        docnumber = self.docnumbers[0]
        if config.digittype == 1:
            docnumber = utility.convertToPersian(docnumber)
            
        # printjob.setHeader(_("Accounting Document"), {_("Document Number"):docnumber, _("Date"):datestr})        
        report_header = report['heading']
        report_data = report['data']
        todaystr = dateToString(date.today())
        html = '<p ' + self.reportObj.subjectHeaderStyle + '><u>' + _("Accounting Document") + '</u></p><p style="text-align:center;">' + _("Document Number") + ': ' + str(docnumber) + '</p><p ' + self.reportObj.detailHeaderStyle + '>' + _("Date") + ': ' + todaystr +'</p>'
        html += self.reportObj.createTable(report_header,report_data)

        return html
    
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
        self.reportObj = WeasyprintReport()
        printjob = self.createPrintJob()
        if printjob != None:
            self.reportObj.showPreview(printjob)
    
    def printReport(self, sender):
        self.reportObj = WeasyprintReport()
        printjob = self.createPrintJob()
        if printjob != None:
            self.reportObj.doPrint(printjob)
    
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
            
        dialog = Gtk.FileChooserDialog(None, self.window, Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                                                                                         Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT))
        res = dialog.run()
        if res ==Gtk.ResponseType.ACCEPT :
            filename = os.path.splitext(dialog.get_filename())[0]
            file = open(filename + ".csv", "w")
            file.write(content)
            file.close()
        dialog.destroy()
