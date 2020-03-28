from amir.dateentry import dateToString
from .share import share
from . import utility
import math
import logging
import cairo
import gi
from gi.repository import Pango, Gtk
gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

from gettext import gettext as _

# config = share.config


class PrintReport:
    def __init__(self, content, cols_width, heading=None):
        # self.lines_per_page = 24
        self.cell_margin = 4
        self.line = 2  # the thinest possible width of lines.
        self.row_height = 2 * (share.config.contentfont + self.cell_margin)
        self.header_height = 0
        self.heading_height = 35

        self.operation = Gtk.PrintOperation()
        settings = Gtk.PrintSettings()
        paper_size = Gtk.PaperSize.new_from_ppd(
            share.config.paper_ppd, share.config.paper_name, share.config.paper_width, share.config.paper_height)
        self.page_setup = Gtk.PageSetup()
        self.page_setup.set_paper_size(paper_size)
        self.page_setup.set_orientation(share.config.paper_orientation)
#        self.page_setup = Gtk.print_run_page_setup_dialog(None, self.page_setup, settings)

        self.page_setup.set_top_margin(share.config.topmargin, Gtk.Unit.POINTS)
        self.page_setup.set_bottom_margin(share.config.botmargin, Gtk.Unit.POINTS)
        self.page_setup.set_right_margin(share.config.rightmargin, Gtk.Unit.POINTS)
        self.page_setup.set_left_margin(share.config.leftmargin, Gtk.Unit.POINTS)

        self.operation.set_default_page_setup(self.page_setup)
        self.operation.set_unit(Gtk.Unit.POINTS)

        self.content = content
        tablewidth = self.page_setup.get_page_width(Gtk.Unit.POINTS)
        tablewidth -= (len(cols_width) * (self.line + self.cell_margin)) + \
            self.line + (share.config.rightmargin + share.config.leftmargin)
        self.cols_width = []
        for percent in cols_width:
            self.cols_width.append(math.floor((percent * tablewidth) / 100))
        # self.cols_width = cols_width
        self.heading = heading

        self.operation.connect("begin_print", self.beginPrint)
        self.operation.connect("draw-page", self.printPage)
        self.type = 0
        self.title = ""
        self.fields = {}
        # self.content = data

    def setHeader(self, title, fields):
        self.title = title
        self.fields = fields

    def beginPrint(self, operation, context):
        tableheight = self.page_setup.get_page_height(Gtk.Unit.POINTS)
        name_lineheight = 2 * share.config.namefont
        header_lineheight = 2 * share.config.headerfont
        tableheight -= (math.floor((len(self.fields) + 1) / 2) * header_lineheight) + (share.config.topmargin +
                                                                                       share.config.botmargin) + self.heading_height + name_lineheight + (self.cell_margin * 2)

        self.lines_per_page = int(math.floor(tableheight / self.row_height))
        # Subtract two lines that show "Sum of previous page" and "Sum"
        self.lines_per_page -= 2
        if self.drawfunction == 'drawDocument':
            lencontent = len(self.content)
            rindex = 0
            pages = 0
            self.documents = {}
            while rindex < lencontent:
                docnumber = self.content[rindex][6]
                offset = 0
                self.documents[pages] = []
                while offset < self.lines_per_page and rindex < lencontent:
                    # detect new document
                    if docnumber != self.content[rindex][6]:
                        break
                    self.documents[pages].append(self.content[rindex])
                    rindex += 1
                    offset += 1

                pages += 1
        else:
            pages = ((len(self.content) - 1) / self.lines_per_page) + 1

        operation.set_n_pages(pages)

    def doPrintJob(self, action):
        self.operation.run(action)

    '''Handel the print page signal and call correct draw function'''

    def printPage(self, operation, context, page_nr):
        self.pangolayout = context.create_pango_layout()
        self.cairo_context = context.get_cairo_context()

        self.pangolayout.set_width(-1)
        self.PangoCairo = PangoCairo.create_context(self.cairo_context)

        getattr(self, self.drawfunction)(page_nr)
        # self.drawDailyNotebook(page_nr)

    def formatHeader(self):
        LINE_HEIGHT = 2 * (share.config.namefont)
        # MARGIN = self.page_margin
        # cwidth = context.get_width()
        cwidth = self.page_setup.get_page_width(Gtk.Unit.POINTS)
        logging.info("Paper width: " + str(cwidth))
        cr = self.cairo_context

        fontsize = share.config.namefont
        fdesc = Pango.FontDescription("Sans")
        fdesc.set_size(fontsize * Pango.SCALE)
        self.pangolayout.set_font_description(fdesc)

        if self.title != "":
            self.pangolayout.set_text(self.title, -1)
            (width, height) = self.pangolayout.get_size()
            self.pangolayout.set_alignment(Pango.Alignment.CENTER)
            cr.move_to((cwidth - width / Pango.SCALE) / 2,
                       (LINE_HEIGHT - (height / Pango.SCALE))/2)
            PangoCairo.show_layout(cr, self.pangolayout)

            # cr.move_to((cwidth + width / Pango.SCALE) / 2, LINE_HEIGHT + config.topmargin)
            # cr.line_to((cwidth - width / Pango.SCALE) / 2, LINE_HEIGHT + config.topmargin)
            cr.move_to((cwidth + width / Pango.SCALE) /
                       2, LINE_HEIGHT + self.cell_margin)
            cr.line_to((cwidth - width / Pango.SCALE) /
                       2, LINE_HEIGHT + self.cell_margin)

        addh = LINE_HEIGHT + self.cell_margin
        LINE_HEIGHT = 2 * share.config.headerfont
        fontsize = share.config.headerfont
        fdesc.set_size(fontsize * Pango.SCALE)
        self.pangolayout.set_font_description(fdesc)

        flag = 1
        for k, v in self.fields.items():
            self.pangolayout.set_text(k + ": " + v, -1)
            (width, height) = self.pangolayout.get_size()
            self.pangolayout.set_alignment(Pango.Alignment.CENTER)
            if flag == 1:
                addh += LINE_HEIGHT
                cr.move_to(cwidth - (width / Pango.SCALE) -
                           share.config.rightmargin, addh - (height / Pango.SCALE)/2)
                flag = 0
            else:
                cr.move_to((width / Pango.SCALE) + share.config.leftmargin,
                           addh - (height / Pango.SCALE)/2)
                flag = 1
            PangoCairo.show_layout(cr, self.pangolayout)

        cr.stroke()
        self.header_height = addh + 8

    def drawDailyNotebook(self, page_nr):
        self.formatHeader()

#        RIGHT_EDGE = 570  #(table width + PAGE_MARGIN)
        RIGHT_EDGE = self.page_setup.get_page_width(
            Gtk.Unit.POINTS) - share.config.rightmargin
        HEADER_HEIGHT = self.header_height
        HEADING_HEIGHT = self.heading_height
#        PAGE_MARGIN = self.page_margin
        MARGIN = self.cell_margin
        TABLE_TOP = HEADER_HEIGHT + HEADING_HEIGHT + self.cell_margin
        ROW_HEIGHT = self.row_height
        LINE = self.line

        cr = self.cairo_context
        fontsize = share.config.contentfont
        fdesc = Pango.FontDescription("Sans")
        fdesc.set_size(fontsize * Pango.SCALE)
        self.pangolayout.set_font_description(fdesc)

#        #Table top line
#        cr.move_to(PAGE_MARGIN, TABLE_TOP)
#        cr.line_to(RIGHT_EDGE, TABLE_TOP)

        self.drawTableHeading()

        # Draw table data
        rindex = page_nr * self.lines_per_page
        offset = 0

        right_txt = RIGHT_EDGE
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)

        self.pangolayout.set_text("----", -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)

        for i in range(0, 3):
            right_txt -= MARGIN + LINE
            cr.move_to(right_txt - (width / Pango.SCALE),
                       TABLE_TOP + (ROW_HEIGHT-(height / Pango.SCALE))/2)
            PangoCairo.show_layout(cr, self.pangolayout)
            right_txt -= self.cols_width[i]
            cr.move_to(right_txt, TABLE_TOP)
            cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)

        right_txt -= MARGIN + LINE
        fontsize -= 1
        fdesc.set_size(fontsize * Pango.SCALE)
        self.pangolayout.set_font_description(fdesc)
        self.pangolayout.set_text(_("Sum of previous page"), -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
        cr.move_to(right_txt - (width / Pango.SCALE), TABLE_TOP +
                   (ROW_HEIGHT-(height / Pango.SCALE))/2)
        PangoCairo.show_layout(cr, self.pangolayout)
        right_txt -= self.cols_width[3]
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)

        right_txt -= MARGIN + LINE
        fontsize = share.config.contentfont
        fdesc.set_size(fontsize * Pango.SCALE)
        self.pangolayout.set_font_description(fdesc)
        if page_nr == 0:
            self.pangolayout.set_text(utility.LN(0), -1)
            self.debt_sum = 0
        else:
            self.pangolayout.set_text(utility.LN(self.debt_sum), -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
        cr.move_to(right_txt - (width / Pango.SCALE), TABLE_TOP +
                   (ROW_HEIGHT-(height / Pango.SCALE))/2)
        PangoCairo.show_layout(cr, self.pangolayout)
        right_txt -= self.cols_width[4]
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)

        right_txt -= MARGIN + LINE
        if page_nr == 0:
            self.pangolayout.set_text(utility.LN(0), -1)
            self.credit_sum = 0
        else:
            self.pangolayout.set_text(utility.LN(self.credit_sum), -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
        cr.move_to(right_txt - (width / Pango.SCALE), TABLE_TOP +
                   (ROW_HEIGHT-(height / Pango.SCALE))/2)
        PangoCairo.show_layout(cr, self.pangolayout)
        right_txt -= self.cols_width[5]
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)

        addh = ROW_HEIGHT + TABLE_TOP
        try:
            while offset < self.lines_per_page:
                row = self.content[rindex + offset]

                cr.move_to(RIGHT_EDGE, addh)
                cr.line_to(RIGHT_EDGE, addh+ROW_HEIGHT)

                right_txt = RIGHT_EDGE
                dindex = 0
                for data in row:
                    right_txt -= MARGIN+LINE
                    if dindex == 3:
                        fontsize -= 1
                        fdesc.set_size(fontsize * Pango.SCALE)
                        self.pangolayout.set_font_description(fdesc)
                        self.pangolayout.set_text(data, -1)
                        (width, height) = self.pangolayout.get_size()
                        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
                        cr.move_to(right_txt - (width / Pango.SCALE),
                                   addh + (ROW_HEIGHT-(height / Pango.SCALE))/2)
                        PangoCairo.show_layout(cr, self.pangolayout)
                        fontsize = share.config.contentfont
                        fdesc.set_size(fontsize * Pango.SCALE)
                        self.pangolayout.set_font_description(fdesc)
                    else:
                        self.pangolayout.set_text(data, -1)
                        (width, height) = self.pangolayout.get_size()
                        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
                        cr.move_to(right_txt - (width / Pango.SCALE),
                                   addh + (ROW_HEIGHT-(height / Pango.SCALE))/2)
                        PangoCairo.show_layout(cr, self.pangolayout)

                    right_txt -= self.cols_width[dindex]
                    cr.move_to(right_txt, addh)
                    cr.line_to(right_txt, addh + ROW_HEIGHT)

                    dindex += 1

                self.debt_sum += int(row[4].replace(",", ""))
                self.credit_sum += int(row[5].replace(",", ""))

                addh += ROW_HEIGHT
                offset += 1
        except IndexError:
            pass

        right_txt = RIGHT_EDGE
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)

        self.pangolayout.set_text("----", -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)

        for i in range(0, 3):
            right_txt -= MARGIN + LINE
            cr.move_to(right_txt - (width / Pango.SCALE), addh +
                       (ROW_HEIGHT-(height / Pango.SCALE))/2)
            PangoCairo.show_layout(cr, self.pangolayout)
            right_txt -= self.cols_width[i]
            cr.move_to(right_txt, addh)
            cr.line_to(right_txt, addh + ROW_HEIGHT)

        right_txt -= MARGIN + LINE
        fontsize -= 1
        fdesc.set_size(fontsize * Pango.SCALE)
        self.pangolayout.set_font_description(fdesc)
        self.pangolayout.set_text(_("Sum"), -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
        cr.move_to(right_txt - (width / Pango.SCALE), addh +
                   (ROW_HEIGHT-(height / Pango.SCALE))/2)
        PangoCairo.show_layout(cr, self.pangolayout)
        right_txt -= self.cols_width[3]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)

        right_txt -= MARGIN + LINE
        fontsize = share.config.contentfont
        fdesc.set_size(fontsize * Pango.SCALE)
        self.pangolayout.set_font_description(fdesc)
        self.pangolayout.set_text(utility.LN(self.debt_sum), -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
        cr.move_to(right_txt - (width / Pango.SCALE), addh +
                   (ROW_HEIGHT-(height / Pango.SCALE))/2)
        PangoCairo.show_layout(cr, self.pangolayout)
        right_txt -= self.cols_width[4]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)

        right_txt -= MARGIN + LINE
        self.pangolayout.set_text(utility.LN(self.credit_sum), -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
        cr.move_to(right_txt - (width / Pango.SCALE), addh +
                   (ROW_HEIGHT-(height / Pango.SCALE))/2)
        PangoCairo.show_layout(cr, self.pangolayout)
        right_txt -= self.cols_width[5]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)

        # Table top line
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(RIGHT_EDGE, TABLE_TOP)

        # Table bottom line
        cr.move_to(right_txt, addh + ROW_HEIGHT)
        cr.line_to(RIGHT_EDGE, addh + ROW_HEIGHT)

        cr.stroke()

    def drawSubjectNotebook(self, page_nr):
        self.formatHeader()
#        RIGHT_EDGE = 570  #(table width + PAGE_MARGIN)
        RIGHT_EDGE = self.page_setup.get_page_width(
            Gtk.Unit.POINTS) - share.config.rightmargin
        HEADER_HEIGHT = self.header_height
        HEADING_HEIGHT = self.heading_height
#        PAGE_MARGIN = self.page_margin
        MARGIN = self.cell_margin
        TABLE_TOP = HEADER_HEIGHT + HEADING_HEIGHT + self.cell_margin
        ROW_HEIGHT = self.row_height
        LINE = self.line

        cr = self.cairo_context
        fontsize = share.config.contentfont
        fdesc = Pango.FontDescription("Sans")
        fdesc.set_size(fontsize * Pango.SCALE)
        self.pangolayout.set_font_description(fdesc)

#        #Table top line
#        cr.move_to(PAGE_MARGIN, TABLE_TOP)
#        cr.line_to(RIGHT_EDGE, TABLE_TOP)

        self.drawTableHeading()

        # Draw table data
        rindex = page_nr * self.lines_per_page
        offset = 0

        right_txt = RIGHT_EDGE
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)

        self.pangolayout.set_text("----", -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)

        for i in range(0, 2):
            right_txt -= MARGIN + LINE
            cr.move_to(right_txt - (width / Pango.SCALE),
                       TABLE_TOP + (ROW_HEIGHT-(height / Pango.SCALE))/2)
            PangoCairo.show_layout(cr, self.pangolayout)
            right_txt -= self.cols_width[i]
            cr.move_to(right_txt, TABLE_TOP)
            cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)

        right_txt -= MARGIN + LINE
        fontsize -= 1
        fdesc.set_size(fontsize * Pango.SCALE)
        self.pangolayout.set_font_description(fdesc)
        self.pangolayout.set_text(_("Sum of previous page"), -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
        cr.move_to(right_txt - (width / Pango.SCALE), TABLE_TOP +
                   (ROW_HEIGHT-(height / Pango.SCALE))/2)
        PangoCairo.show_layout(cr, self.pangolayout)
        right_txt -= self.cols_width[2]
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)

        right_txt -= MARGIN + LINE
        fontsize = share.config.contentfont
        fdesc.set_size(fontsize * Pango.SCALE)
        self.pangolayout.set_font_description(fdesc)
        if page_nr == 0:
            self.pangolayout.set_text(utility.LN(0), -1)
            self.debt_sum = 0
        else:
            self.pangolayout.set_text(utility.LN(self.debt_sum), -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
        cr.move_to(right_txt - (width / Pango.SCALE), TABLE_TOP +
                   (ROW_HEIGHT-(height / Pango.SCALE))/2)
        PangoCairo.show_layout(cr, self.pangolayout)
        right_txt -= self.cols_width[3]
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)

        right_txt -= MARGIN + LINE
        if page_nr == 0:
            self.pangolayout.set_text(utility.LN(0), -1)
            self.credit_sum = 0
        else:
            self.pangolayout.set_text(utility.LN(self.credit_sum), -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
        cr.move_to(right_txt - (width / Pango.SCALE), TABLE_TOP +
                   (ROW_HEIGHT-(height / Pango.SCALE))/2)
        PangoCairo.show_layout(cr, self.pangolayout)
        right_txt -= self.cols_width[4]
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)

        if page_nr == 0:
            remaining = int(self.content[0][3].replace(
                ",", "")) - int(self.content[0][4].replace(",", ""))
            if self.content[0][5] == _("deb"):
                remaining -= int(self.content[0][6].replace(",", ""))
            else:
                remaining += int(self.content[0][6].replace(",", ""))
            if remaining < 0:
                self.diagnose = _("deb")
                self.remaining = utility.LN(-(remaining))
            else:
                if remaining == 0:
                    self.diagnose = _("equ")
                else:
                    self.diagnose = _("cre")
                self.remaining = utility.LN(remaining)

        right_txt -= MARGIN + LINE
        self.pangolayout.set_text(self.diagnose, -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
        cr.move_to(right_txt - (width / Pango.SCALE), TABLE_TOP +
                   (ROW_HEIGHT-(height / Pango.SCALE))/2)
        PangoCairo.show_layout(cr, self.pangolayout)
        right_txt -= self.cols_width[5]
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)

        right_txt -= MARGIN + LINE
        self.pangolayout.set_text(self.remaining, -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
        cr.move_to(right_txt - (width / Pango.SCALE), TABLE_TOP +
                   (ROW_HEIGHT-(height / Pango.SCALE))/2)
        PangoCairo.show_layout(cr, self.pangolayout)
        right_txt -= self.cols_width[6]
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)

        addh = ROW_HEIGHT + TABLE_TOP
        try:
            while offset < self.lines_per_page:
                row = self.content[rindex + offset]

                cr.move_to(RIGHT_EDGE, addh)
                cr.line_to(RIGHT_EDGE, addh+ROW_HEIGHT)

                right_txt = RIGHT_EDGE
                dindex = 0
                for data in row:
                    right_txt -= MARGIN+LINE
                    if dindex == 2:
                        fontsize -= 1
                        fdesc.set_size(fontsize * Pango.SCALE)
                        self.pangolayout.set_font_description(fdesc)
                        self.pangolayout.set_text(data, -1)
                        (width, height) = self.pangolayout.get_size()
                        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
                        cr.move_to(right_txt - (width / Pango.SCALE),
                                   addh + (ROW_HEIGHT-(height / Pango.SCALE))/2)
                        PangoCairo.show_layout(cr, self.pangolayout)
                        fontsize = share.config.contentfont
                        fdesc.set_size(fontsize * Pango.SCALE)
                        self.pangolayout.set_font_description(fdesc)
                    else:
                        self.pangolayout.set_text(data, -1)
                        (width, height) = self.pangolayout.get_size()
                        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
                        cr.move_to(right_txt - (width / Pango.SCALE),
                                   addh + (ROW_HEIGHT-(height / Pango.SCALE))/2)
                        PangoCairo.show_layout(cr, self.pangolayout)
                    right_txt -= self.cols_width[dindex]
                    cr.move_to(right_txt, addh)
                    cr.line_to(right_txt, addh + ROW_HEIGHT)

                    dindex += 1

                self.debt_sum += int(row[3].replace(",", ""))
                self.credit_sum += int(row[4].replace(",", ""))

                addh += ROW_HEIGHT
                offset += 1

        except IndexError:
            pass

        self.diagnose = self.content[rindex + offset - 1][5]
        self.remaining = self.content[rindex + offset - 1][6]

        right_txt = RIGHT_EDGE
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)

        self.pangolayout.set_text("----", -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)

        for i in range(0, 2):
            right_txt -= MARGIN + LINE
            cr.move_to(right_txt - (width / Pango.SCALE), addh +
                       (ROW_HEIGHT-(height / Pango.SCALE))/2)
            PangoCairo.show_layout(cr, self.pangolayout)
            right_txt -= self.cols_width[i]
            cr.move_to(right_txt, addh)
            cr.line_to(right_txt, addh + ROW_HEIGHT)

        right_txt -= MARGIN + LINE
        fontsize -= 1
        fdesc.set_size(fontsize * Pango.SCALE)
        self.pangolayout.set_font_description(fdesc)
        self.pangolayout.set_text(_("Sum"), -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
        cr.move_to(right_txt - (width / Pango.SCALE), addh +
                   (ROW_HEIGHT-(height / Pango.SCALE))/2)
        PangoCairo.show_layout(cr, self.pangolayout)
        right_txt -= self.cols_width[2]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)

        right_txt -= MARGIN + LINE
        fontsize = share.config.contentfont
        fdesc.set_size(fontsize * Pango.SCALE)
        self.pangolayout.set_font_description(fdesc)
        self.pangolayout.set_text(utility.LN(self.debt_sum), -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
        cr.move_to(right_txt - (width / Pango.SCALE), addh +
                   (ROW_HEIGHT-(height / Pango.SCALE))/2)
        PangoCairo.show_layout(cr, self.pangolayout)
        right_txt -= self.cols_width[3]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)

        right_txt -= MARGIN + LINE
        self.pangolayout.set_text(utility.LN(self.credit_sum), -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
        cr.move_to(right_txt - (width / Pango.SCALE), addh +
                   (ROW_HEIGHT-(height / Pango.SCALE))/2)
        PangoCairo.show_layout(cr, self.pangolayout)
        right_txt -= self.cols_width[4]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)

        right_txt -= MARGIN + LINE
        self.pangolayout.set_text(self.diagnose, -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
        cr.move_to(right_txt - (width / Pango.SCALE), addh +
                   (ROW_HEIGHT-(height / Pango.SCALE))/2)
        PangoCairo.show_layout(cr, self.pangolayout)
        right_txt -= self.cols_width[5]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)

        right_txt -= MARGIN + LINE
        self.pangolayout.set_text(self.remaining, -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
        cr.move_to(right_txt - (width / Pango.SCALE), addh +
                   (ROW_HEIGHT-(height / Pango.SCALE))/2)
        PangoCairo.show_layout(cr, self.pangolayout)
        right_txt -= self.cols_width[6]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)

        # Table top line
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(RIGHT_EDGE, TABLE_TOP)

        # Table bottom line
#        cr.move_to(self.page_margin, addh + ROW_HEIGHT)
        cr.move_to(right_txt, addh + ROW_HEIGHT)
        cr.line_to(RIGHT_EDGE, addh + ROW_HEIGHT)

        cr.stroke()

    def drawDocument(self, page_nr):
        content = self.documents[page_nr]
        docnumber = content[0][6]
        datestr = content[0][7]
        self.fields = {_("Document Number"): docnumber, _("Date"): datestr}
        self.formatHeader()
#        RIGHT_EDGE = 570  #(table width + PAGE_MARGIN)
        RIGHT_EDGE = self.page_setup.get_page_width(
            Gtk.Unit.POINTS) - share.config.rightmargin
        HEADER_HEIGHT = self.header_height
        HEADING_HEIGHT = self.heading_height
#        PAGE_MARGIN = self.page_margin
        MARGIN = self.cell_margin
        TABLE_TOP = HEADER_HEIGHT + HEADING_HEIGHT + self.cell_margin
        ROW_HEIGHT = self.row_height
        LINE = self.line

        cr = self.cairo_context
        fontsize = share.config.contentfont
        fdesc = Pango.FontDescription("Sans")
        fdesc.set_size(fontsize * Pango.SCALE)
        self.pangolayout.set_font_description(fdesc)

        self.drawTableHeading()

        # Draw table data
        offset = 0
        self.debt_sum = 0
        self.credit_sum = 0

        addh = TABLE_TOP
        for row in content:
            cr.move_to(RIGHT_EDGE, addh)
            cr.line_to(RIGHT_EDGE, addh+ROW_HEIGHT)

            right_txt = RIGHT_EDGE
            dindex = 0
            for data in row:
                right_txt -= MARGIN+LINE
                if dindex == 6 or dindex == 7 or dindex == 8 or dindex == 9:
                    break
                elif dindex == 2 or dindex == 3:
                    fontsize -= 1
                    fdesc.set_size(fontsize * Pango.SCALE)
                    self.pangolayout.set_font_description(fdesc)
                    self.pangolayout.set_text(data, -1)
                    (width, height) = self.pangolayout.get_size()
                    self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
                    cr.move_to(right_txt - (width / Pango.SCALE),
                               addh + (ROW_HEIGHT-(height / Pango.SCALE))/2)
                    PangoCairo.show_layout(cr, self.pangolayout)
                    fontsize = share.config.contentfont
                    fdesc.set_size(fontsize * Pango.SCALE)
                    self.pangolayout.set_font_description(fdesc)
                else:
                    self.pangolayout.set_text(data, -1)
                    (width, height) = self.pangolayout.get_size()
                    self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
                    cr.move_to(right_txt - (width / Pango.SCALE),
                               addh + (ROW_HEIGHT-(height / Pango.SCALE))/2)
                    PangoCairo.show_layout(cr, self.pangolayout)

                right_txt -= self.cols_width[dindex]
                cr.move_to(right_txt, addh)
                cr.line_to(right_txt, addh + ROW_HEIGHT)

                dindex += 1

#            self.debt_sum += int(row[4].replace(",", ""))
#            self.credit_sum += int(row[5].replace(",", ""))

            addh += ROW_HEIGHT
            offset += 1

        self.debt_sum = int(row[8])
        self.credit_sum = int(row[9])
        right_txt = RIGHT_EDGE
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)

        right_txt -= 4*(MARGIN + LINE) + \
            self.cols_width[0] + self.cols_width[1] + self.cols_width[2]
        self.pangolayout.set_text(_("Sum"), -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
        cr.move_to(right_txt - (width / Pango.SCALE), addh +
                   (ROW_HEIGHT-(height / Pango.SCALE))/2)
        PangoCairo.show_layout(cr, self.pangolayout)
        right_txt -= self.cols_width[3]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)

        cr.move_to(RIGHT_EDGE, addh)
        cr.line_to(right_txt, addh)

        right_txt -= MARGIN + LINE
        self.pangolayout.set_text(utility.LN(self.debt_sum), -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
        cr.move_to(right_txt - (width / Pango.SCALE), addh +
                   (ROW_HEIGHT-(height / Pango.SCALE))/2)
        PangoCairo.show_layout(cr, self.pangolayout)
        right_txt -= self.cols_width[4]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)

        right_txt -= MARGIN + LINE
        self.pangolayout.set_text(utility.LN(self.credit_sum), -1)
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
        cr.move_to(right_txt - (width / Pango.SCALE), addh +
                   (ROW_HEIGHT-(height / Pango.SCALE))/2)
        PangoCairo.show_layout(cr, self.pangolayout)
        right_txt -= self.cols_width[5]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)

        # Table top line
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(RIGHT_EDGE, TABLE_TOP)

        # Table bottom line
        cr.move_to(right_txt, addh + ROW_HEIGHT)
        cr.line_to(RIGHT_EDGE, addh + ROW_HEIGHT)

        cr.stroke()

    def drawTrialReport(self, page_nr):
        self.formatHeader()
        RIGHT_EDGE = self.page_setup.get_page_width(
            Gtk.Unit.POINTS) - share.config.rightmargin
        HEADER_HEIGHT = self.header_height
        HEADING_HEIGHT = self.heading_height
        MARGIN = self.cell_margin
        TABLE_TOP = HEADER_HEIGHT + HEADING_HEIGHT + self.cell_margin
        ROW_HEIGHT = self.row_height
        LINE = self.line

        cr = self.cairo_context
        fontsize = share.config.contentfont
        fdesc = Pango.FontDescription("Sans")
        fdesc.set_size(fontsize * Pango.SCALE)
        self.pangolayout.set_font_description(fdesc)

        self.drawTableHeading()

        # Draw table data
        rindex = page_nr * self.lines_per_page
        offset = 0
        addh = TABLE_TOP

        try:
            while offset < self.lines_per_page:
                row = self.content[rindex + offset]

                cr.move_to(RIGHT_EDGE, addh)
                cr.line_to(RIGHT_EDGE, addh+ROW_HEIGHT)

                right_txt = RIGHT_EDGE
                dindex = 0
                for data in row:
                    right_txt -= MARGIN+LINE
                    self.pangolayout.set_text(data, -1)
                    (width, height) = self.pangolayout.get_size()
                    self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
                    cr.move_to(right_txt - (width / Pango.SCALE),
                               addh + (ROW_HEIGHT-(height / Pango.SCALE))/2)
                    PangoCairo.show_layout(cr, self.pangolayout)

                    right_txt -= self.cols_width[dindex]
                    cr.move_to(right_txt, addh)
                    cr.line_to(right_txt, addh + ROW_HEIGHT)
                    dindex += 1

                addh += ROW_HEIGHT
                offset += 1
        except IndexError:
            pass

        # Table top line
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(RIGHT_EDGE, TABLE_TOP)

        # Table bottom line
        cr.move_to(right_txt, addh)
        cr.line_to(RIGHT_EDGE, addh)

        cr.stroke()

    def setDrawFunction(self, func):
        self.drawfunction = func

    def drawTableHeading(self):
        #        RIGHT_EDGE = 570  #(table width + PAGE_MARGIN)
        RIGHT_EDGE = self.page_setup.get_page_width(
            Gtk.Unit.POINTS) - share.config.rightmargin
        HEADING_HEIGHT = self.heading_height
        MARGIN = self.cell_margin
        LINE = self.line

        cr = self.cairo_context

        htop = self.header_height + MARGIN
#        #Heading top line
#        cr.move_to(self.page_margin, htop)
#        cr.line_to(RIGHT_EDGE, htop)

        cr.move_to(RIGHT_EDGE, htop)
        cr.line_to(RIGHT_EDGE, htop + HEADING_HEIGHT)

        # Draw table headings
        right_txt = RIGHT_EDGE
        dindex = 0
        for data in self.heading:
            right_txt -= MARGIN+LINE
            self.pangolayout.set_text(data, -1)
            (width, height) = self.pangolayout.get_size()
            if (width / Pango.SCALE) > self.cols_width[dindex]:
                res = data.split()
                self.pangolayout.set_text(res[0], -1)
                (width, height) = self.pangolayout.get_size()
                if (width / Pango.SCALE) < self.cols_width[dindex]:
                    # self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
                    cr.move_to(right_txt - (width / Pango.SCALE), htop +
                               (HEADING_HEIGHT/2-(height / Pango.SCALE))/2)
                    PangoCairo.show_layout(cr, self.pangolayout)
                    #
                    self.pangolayout.set_text(res[1], -1)
                    (width, height) = self.pangolayout.get_size()
                    # self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
                    cr.move_to(right_txt - (width / Pango.SCALE), htop +
                               ((HEADING_HEIGHT*3)/2-(height / Pango.SCALE))/2)
                    PangoCairo.show_layout(cr, self.pangolayout)
            else:
                # self.pangolayout.set_alignment(Pango.Alignment.RIGHT)
                cr.move_to(right_txt - (width / Pango.SCALE), htop +
                           (HEADING_HEIGHT-(height / Pango.SCALE))/2)
                PangoCairo.show_layout(cr, self.pangolayout)

            right_txt -= self.cols_width[dindex]
            cr.move_to(right_txt, htop)
            cr.line_to(right_txt, htop + HEADING_HEIGHT)

            dindex += 1

        # Heading top line
        cr.move_to(right_txt, htop)
        cr.line_to(RIGHT_EDGE, htop)

#    def dailySpecific(self, pos, page):
#        pass
#
#    def subjectSpecific(self, pos, page):
#        pass
#
#    def docSpecific(self, pos, page):
#        pass
