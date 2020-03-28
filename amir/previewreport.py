import gi
from gi.repository import Gtk
import math

from . import utility
from .share import share
from .helpers import get_builder

from gettext import gettext as _

# config = share.config


class PreviewReport:
    def __init__(self, content, heading=None):
        self.content = content
        self.heading = heading
        self.lines_per_page = 20
        self.setDrawFunction("drawDefaultReport")

        self.builder = get_builder("report")
        self.treeview = self.builder.get_object("previewBox")
        self.treeview.set_direction(Gtk.TextDirection.LTR)

        self.liststore = Gtk.ListStore(*([str] * len(self.heading)))
        self.pagecount = self.builder.get_object("pagecount")

        self.pageNumber = self.builder.get_object("pageNumber")
        self.current_page = 1
        self.pageNumber.set_value(self.current_page)

        if Gtk.widget_get_default_direction() == Gtk.TextDirection.RTL:
            halign = 1
        else:
            halign = 0

        index = 0
        for label in self.heading:
            column = Gtk.TreeViewColumn(
                label, Gtk.CellRendererText(), text=index)
            column.set_alignment(halign)
            column.set_spacing(10)
            column.set_resizable(True)
            self.treeview.append_column(column)
            index += 1

        self.treeview.set_model(self.liststore)

        self.window = self.builder.get_object("previewWidget")
        self.window.show_all()
        self.builder.connect_signals(self)

    def setDrawFunction(self, func):
        self.drawfunction = func

    def doPreviewJob(self):
        print("doPreviewJob")
        getattr(self, self.drawfunction)()
        self.pagecount.set_text(str(self.pages))
        self.drawPage(1)

    def drawPage(self, page_nr):
        self.liststore.clear()
        for data in self.content[(self.lines_per_page * (page_nr - 1)): (self.lines_per_page * page_nr)]:
            self.liststore.append((data))

    def showPreviousPage(self, sender):
        if self.current_page > 1:
            self.current_page -= 1
            self.pageNumber.set_value(self.current_page)
            self.drawPage(self.current_page)

    def showNextPage(self, sender):
        if self.current_page < self.pages:
            self.current_page += 1
            self.pageNumber.set_value(self.current_page)
            self.drawPage(self.current_page)

    def showPage(self, sender):
        newvalue = self.pageNumber.get_value_as_int()
        if newvalue < 1:
            newvalue = 1
        elif newvalue > self.pages:
            newvalue = self.pages

        self.current_page = newvalue
        self.pageNumber.set_value(newvalue)
        self.drawPage(newvalue)

    def drawDefaultReport(self):
        self.pages = ((len(self.content) - 1) / (self.lines_per_page)) + 1

    def drawDailyNotebook(self):
        self.pages = ((len(self.content) - 1) / (self.lines_per_page - 2)) + 1
        debtsum = 0
        creditsum = 0
        for page_nr in range(1, self.pages + 1):
            self.content.insert(self.lines_per_page * (page_nr - 1),
                                ("", "", "", _("Sum of previous page"), debtsum, creditsum))
            for data in self.content[(self.lines_per_page * (page_nr - 1) + 1): (self.lines_per_page * page_nr) - 1]:
                debtsum += int(data[4].replace(",", ""))
                creditsum += int(data[5].replace(",", ""))
            self.content.insert((self.lines_per_page * page_nr) - 1,
                                ("", "", "", _("Sum"), debtsum, creditsum))

    def drawSubjectNotebook(self):
        self.pages = ((len(self.content) - 1) / (self.lines_per_page - 2)) + 1
        debtsum = 0
        creditsum = 0
        diagnose = ""
        remaining = int(self.content[0][3].replace(
            ",", "")) - int(self.content[0][4].replace(",", ""))
        if self.content[0][5] == _("deb"):
            remaining -= int(self.content[0][6].replace(",", ""))
        else:
            remaining += int(self.content[0][6].replace(",", ""))
        if remaining < 0:
            diagnose = _("deb")
            sr = utility.LN(-(remaining))
        else:
            if remaining == 0:
                diagnose = _("equ")
            else:
                diagnose = _("cre")
            sr = utility.LN(remaining)

        for page_nr in range(1, self.pages + 1):
            temp = self.lines_per_page * page_nr
            self.content.insert(self.lines_per_page * (page_nr - 1), ("", "",
                                                                      _("Sum of previous page"), debtsum, creditsum, diagnose, sr))

            for data in self.content[(self.lines_per_page * (page_nr - 1) + 1): temp - 1]:
                debtsum += int(data[3].replace(",", ""))
                creditsum += int(data[4].replace(",", ""))
                diagnose = data[5]
                sr = data[6]
            self.content.insert(
                temp - 1, ("", "", _("Sum"), debtsum, creditsum, diagnose, sr))

    def drawDocument(self):
        self.pages = ((len(self.content) - 1) / (self.lines_per_page - 1)) + 1
        debtsum = 0
        creditsum = 0
        for page_nr in range(1, self.pages + 1):
            for data in self.content[(self.lines_per_page * (page_nr - 1)): (self.lines_per_page * page_nr) - 1]:
                debtsum += int(data[4].replace(",", ""))
                creditsum += int(data[5].replace(",", ""))
            self.content.insert((self.lines_per_page * page_nr) - 1,
                                ("", "", "", _("Sum"), debtsum, creditsum))
