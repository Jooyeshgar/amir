from weasyprint import HTML
import os
import gi
gi.require_version('Poppler', '0.18')
from gi.repository import GLib, Gtk, Poppler
import subprocess
import sys
import time
from share import share
config = share.config

class PrintingApp:
    def __init__(self, file_uri):
        self.operation = Gtk.PrintOperation()

        self.operation.connect('begin-print', self.begin_print, None)
        self.operation.connect('draw-page', self.draw_page, None)

        self.doc = Poppler.Document.new_from_file(file_uri)

    def begin_print(self, operation, print_ctx, print_data):
        operation.set_n_pages(self.doc.get_n_pages())

    def draw_page(self, operation, print_ctx, page_num, print_data):
        cr = print_ctx.get_cairo_context()
        page = self.doc.get_page(page_num)
        page.render(cr)

    def run(self, parent=None):
        result = self.operation.run(Gtk.PrintOperationAction.PRINT_DIALOG,
                                    parent)

        if result == Gtk.PrintOperationResult.ERROR:
            message = self.operation.get_error()

            dialog = Gtk.MessageDialog(parent,
                                       0,
                                       Gtk.MessageType.ERROR,
                                       Gtk.ButtonsType.CLOSE,
                                       message)

            dialog.run()
            dialog.destroy()

        Gtk.main_quit()

class WeasyprintReport:
    def __init__(self):                  
        self.subjectHeaderStyle = 'style="text-align:center;"'
        if config.locale == 'en_US':
            self.direction = 'left'
        else:
            self.direction = 'right'
    def doPrint(self, html):
        HTML(string=html).write_pdf('report.pdf')
        file_uri = GLib.filename_to_uri(os.path.abspath('report.pdf'))
        main_window = Gtk.OffscreenWindow()
        app = PrintingApp(file_uri)
        GLib.idle_add(app.run, main_window)
        Gtk.main()
        os.remove('report.pdf');
    def showPreview(self, html):
        HTML(string=html).write_pdf('report.pdf')
        if sys.platform == 'linux2':
            subprocess.call(["xdg-open", 'report.pdf'])
        else:
            os.startfile('report.pdf')
        time.sleep(1)
        os.remove('report.pdf');
    def createTable(self,report_header,report_data):
        if config.locale == 'en_US':
            html = '<table style="width:100%"><tr>'
            for header in report_header:
                html += '<th>' + header + '</th>'
            html += '</tr>'
            for row in report_data:
                html += '<tr>'
                for data in row:
                    html += '<td>' + data + '</td>'
                html += '</tr>'
            html += '</table>'
        else:
            html = '<table style="width:100%"><tr>'
            report_header = report_header[::-1]
            for header in report_header:
                html += '<th>' + header + '</th>'
            html += '</tr>'
            for row in report_data:
                row = row[::-1]
                html += '<tr>'
                for data in row:
                    html += '<td>' + data + '</td>'
                html += '</tr>'
            html += '</table>'
        return html