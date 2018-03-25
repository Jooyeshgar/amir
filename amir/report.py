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
import cairocffi

class Printo:
    def __init__(self, url):
        self.operation = Gtk.PrintOperation()

        document = HTML(string=url).render()

        self.operation.connect('begin-print', self.begin_print, document)
        self.operation.connect('draw-page', self.draw_page, document)

        self.operation.set_use_full_page(False)
        self.operation.set_unit(Gtk.Unit.POINTS)
        self.operation.set_embed_page_setup(True)

        settings = Gtk.PrintSettings()

        directory = GLib.get_user_special_dir(
            GLib.UserDirectory.DIRECTORY_DOCUMENTS) or GLib.get_home_dir()
        ext = settings.get(Gtk.PRINT_SETTINGS_OUTPUT_FILE_FORMAT) or 'pdf'
        uri = 'file://%s/weasyprint.%s' % (directory, ext)
        settings.set(Gtk.PRINT_SETTINGS_OUTPUT_URI, uri)
        self.operation.set_print_settings(settings)

    def run(self):
        self.operation.run(Gtk.PrintOperationAction.PRINT_DIALOG)
        Gtk.main_quit()

    def begin_print(self, operation, print_ctx, document):
        operation.set_n_pages(len(document.pages))

    def draw_page(self, operation, print_ctx, page_num, document):
        page = document.pages[page_num]
        cairo_context = print_ctx.get_cairo_context()
        cairocffi_context = cairocffi.Context._from_pointer(
            cairocffi.ffi.cast(
                'cairo_t **', id(cairo_context) + object.__basicsize__)[0],
            incref=True)
        page.paint(cairocffi_context, left_x=0, top_y=-40, scale=0.75)

class WeasyprintReport:
    def __init__(self):                  
        self.subjectHeaderStyle = 'style="text-align:center;"'
        if config.locale == 'en_US':
            self.direction = 'left'
        else:
            self.direction = 'right'
    def doPrint(self, html):
        app = Printo(html).run()
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