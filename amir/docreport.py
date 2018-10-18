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
        number = utility.convertToLatin(unicode(self.number.get_text()) )
        
        if re.match('^\d+$', number) != None:
            self.docnumbers=[int(number)]
        elif re.match('^(\d+)-(\d+)$', number) != None:
            m = re.match('^(\d+)-(\d+)$', number)
            self.docnumbers=range(int(m.group(1)),int(m.group(2))+1)
        else:
            self.builder.get_object("message").set_text( _("Please enter number in correct format \r\nTrue Formats: '2-11' or '2'  ") )
            return
        
        self.builder.get_object("message").set_text("")
        report_header = [_("Index"), _("Subject Code"), _("Subject Name"), _("Description"), _("Debt"), _("Credit")]
        html = "" 
        bills = config.db.session.query(Bill).filter(Bill.number.in_(self.docnumbers)).order_by(Bill.number.asc()).all()
        if config.locale == 'en_US':
            doDirection = 'left'
            daDirection = 'right'
            text_align = "left"
        else:
            doDirection = 'right'
            daDirection = 'left'
            text_align = "right"
        todaystr = dateToString(date.today())
        billCount = 1
        for b in bills:
            report_data = []       
            query = config.db.session.query(Notebook,Subject).select_from(outerjoin(Notebook, Subject, Notebook.subject_id == Subject.id)).filter(Notebook.bill_id==b.id).order_by(Notebook.id.asc())
            res = query.all()            
            if len(res) == 0:
                msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, 
                                           _("No document found with the requested number."))
                msgbox.set_title(_("Invalid document number"))
                msgbox.run()
                msgbox.destroy()
                return

            self.docdate = b.date            
            index = 1
            debt_sum = credit_sum =  0
            datestr = dateToString(self.docdate)
            docnumber = b.number
            if config.digittype == 1:
                docnumber = utility.convertToPersian(docnumber)

            html += '<p ' + self.reportObj.subjectHeaderStyle + '><u>' + _("Accounting Document") + '</u></p>\
                <div style="text-align:' + doDirection + '; font-size:12px;float:'+doDirection+'">' + _("Document Number") + ': ' + str(docnumber) + '</div>\
                <div style="text-align:' + daDirection + '; font-size:12px;float:'+daDirection+'">' + _("Date") + ': ' + todaystr +'</div> <br/>'
            for n , s in res :
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

                debt_sum += utility.getFloatNumber(debt)
                credit_sum += utility.getFloatNumber(credit)                            
                report_data.append(( str(index), code, s.name, desc, debt, credit))
                index += 1                        
                
            html += '<table class="notebooks"><thead><tr>'
            if config.locale == 'en_US':                            
                for header in report_header:
                    html += '<th>' + header + '</th>'
                html += '</tr></thead><tbody>'
                for row in report_data:
                    html += '<tr>'
                    for data in row:
                        html += '<td>' + str(data) + '</td>'
                    html += '</tr>'                
            else:                
                report_header = report_header[::-1]
                for header in report_header:
                    html += '<th>' + header + '</th>'
                html += '</tr></thead><tbody>'
                for row in report_data:
                    row = row[::-1]
                    html += '<tr>'
                    for data in row:
                        html += '<td>' + str(data) + '</td>'
                    html += '</tr>'
            row = ['<td colspan="4" >'+unicode(_("Total")+'</td>'),'<td>'+unicode(utility.LN(debt_sum)+'</td>'),'<td>'+unicode(utility.LN(credit_sum))+'</td>' ]
            signaturesRow = [unicode(_("Accounting")), unicode(_("Financial Manager")) , unicode(_("Managing Director")) ]
            if config.locale != 'en_US':   
                row = row[::-1]     
                signaturesRow = signaturesRow[::-1]       
            html+= '<tr style="border:1px solid black;">'+row[0]+ row[1]+row[2]+'</tr>'
            html += '</tbody></table> <br/><br/>'
            html+= '<table class="signatures" > \
                    <tr style="border:0px" ><td>'+signaturesRow[0]+'</td> <td>'+signaturesRow[1]+'</td> <td>'+signaturesRow[2]+'</td> </tr>\
                    <tr></tr> \
                    </table>'
            billCount +=1
            if billCount <= len(bills):
                html+= '<p style="page-break-before: always" ></p>'

        html = '<!DOCTYPE html> <html> <head> \
                <style> @font-face {font-family: "Vazir"; src: url(data/font/Vazir.woff); }\
                table {border-collapse: collapse;  text-align:'+text_align+'; width:100%;} \
                th {border:1px solid black; padding: 10px;font-size:10px;}\
                thead {display: table-header-group;} \
                .notebooks td {border-left:1px solid; border-right:1px solid; padding: 10px;font-size:10px;} \
                .signatures {border:0px; font-size:14px; text-align:center}\
                </style> <meta charset="UTF-8"> </head> <body>' + html + '</body> </html>'                     
        return html

    def createPrintJob(self):       
        return   self.createReport()
    
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


    def createTable (self,report_header, report_data):
        if config.locale == 'en_US':
            text_align = "left"
            html = '<table style="width:100%"><tr>'
            for header in report_header:
                html += '<th>' + header + '</th>'
            html += '</tr>'
            for row in report_data:
                html += '<tr>'
                for data in row:
                    html += '<td>' + str(data) + '</td>'
                html += '</tr>'
            html += '</table>'
        else:
            text_align =  "right"
            html = '<table style="width:100%; "><tr>'
            report_header = report_header[::-1]
            for header in report_header:
                html += '<th>' + header + '</th>'
            html += '</tr>'
            for row in report_data:
                row = row[::-1]
                html += '<tr>'
                for data in row:
                    html += '<td>' + str(data) + '</td>'
                html += '</tr>'
            html += '</table>'
        # html = '<!DOCTYPE html> <html> <head> \
        #         <style> @font-face {font-family: Vazir; src: url(data/font/Vazir.woff); } html {font-family: myFirstFont; } \
        #         table {border-collapse: collapse;  text-align:'+text_align+';} \
        #         table, th {border-top: 2px solid; border-bottom: 2px solid; border-left:1px solid; border-right:1px solid black; padding: 10px;font-size:10px;}\
        #          td {border-left:1px solid; border-right:1px solid; padding: 10px;} </style> <meta charset="UTF-8"> </head> <body>' + html + '</body> </html>'        
        return html