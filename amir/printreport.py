import pygtk
import gtk
import pango
import pangocairo

import utility

class PrintReport:
    def __init__(self, content, cols_width, heading=None):
        self.operation = gtk.PrintOperation()
        self.fontsize = 10
        self.headerfont = 12
        self.lines_per_page = 27
        self.cell_margin = 4
        self.page_margin = 5
        self.line = 2
        self.row_height = 25

        self.headerlines = 0
        self.header_height = 0
        self.heading_height = 35
        
        self.content = content
        self.cols_width = cols_width
        self.heading = heading
        self.operation.connect("begin_print", self.beginPrint)
        self.operation.connect("draw-page", self.printPage)
        self.type = 0
        self.title = ""
        self.fields = {}
    
    ##self.content = data
    def setHeader (self, title, fields):
        self.title = title
        self.fields = fields
             
    def beginPrint(self, operation, context):
        pages = ((len(self.content) - 1) / (self.lines_per_page - self.headerlines)) + 1
        operation.set_n_pages(pages)
    
    def doPrint(self):
        self.operation.run(gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG)
        
    def drawPage(self, operation, context, page_nr):
        pass
    
    def printPage(self, operation, context, page_nr):
        self.pangolayout = context.create_pango_layout()
        self.cairo_context = context.get_cairo_context()
        
        self.pangolayout.set_width(-1)
        self.pangocairo = pangocairo.CairoContext(self.cairo_context)
        
        self.formatHeader(context)
        getattr(self, self.drawfunction)(page_nr)
        #self.drawDailyNotebook(page_nr)
 
    def formatHeader(self, context):
        LINE_HEIGHT = 25
        MARGIN = self.page_margin
        cwidth = context.get_width()
        cr = self.cairo_context
        
        fdesc = pango.FontDescription("Sans")
        fdesc.set_size(self.headerfont * pango.SCALE)
        self.pangolayout.set_font_description(fdesc)
        
        if self.title != "":
            self.pangolayout.set_text(self.title)
            (width, height) = self.pangolayout.get_size()
            self.pangolayout.set_alignment(pango.ALIGN_CENTER)
            cr.move_to ((cwidth - width / pango.SCALE) / 2, (LINE_HEIGHT - (height/ pango.SCALE))/2)
            self.pangocairo.show_layout(self.pangolayout)
            
            cr.move_to((cwidth + width / pango.SCALE) / 2, LINE_HEIGHT+MARGIN)
            cr.line_to((cwidth - width / pango.SCALE) / 2, LINE_HEIGHT+MARGIN)
            
        LINE_HEIGHT = 20
        addh = LINE_HEIGHT+MARGIN
        flag = 1
        for k,v in self.fields.items():
            self.pangolayout.set_text(k + ": " + v)
            (width, height) = self.pangolayout.get_size()
            self.pangolayout.set_alignment(pango.ALIGN_CENTER)
            if flag == 1:
                addh += LINE_HEIGHT
                cr.move_to (cwidth - (width / pango.SCALE) - MARGIN, addh - (height/ pango.SCALE)/2)
                flag = 0
            else:
                cr.move_to ((width / pango.SCALE) + MARGIN, addh - (height/ pango.SCALE)/2)
                flag = 1
            self.pangocairo.show_layout(self.pangolayout)
            
        cr.stroke()
        self.header_height = addh + 8
            
            
    def drawDailyNotebook(self, page_nr):
        RIGHT_EDGE = 570  #(table width + PAGE_MARGIN)
        HEADER_HEIGHT = self.header_height
        HEADING_HEIGHT = self.heading_height
        PAGE_MARGIN = self.page_margin
        MARGIN = self.cell_margin
        TABLE_TOP = HEADER_HEIGHT + HEADING_HEIGHT + PAGE_MARGIN
        ROW_HEIGHT = self.row_height
        LINE = self.line
        
        cr = self.cairo_context
        fdesc = pango.FontDescription("Sans")
        fdesc.set_size(self.fontsize * pango.SCALE)
        self.pangolayout.set_font_description(fdesc)
        
        cr.move_to(PAGE_MARGIN, HEADER_HEIGHT+PAGE_MARGIN)
        cr.line_to(RIGHT_EDGE, HEADER_HEIGHT+PAGE_MARGIN)

        #cr.move_to(MARGIN, HEADER_HEIGHT+MARGIN);
        #cr.line_to(MARGIN, TABLE_TOP);

        cr.move_to(RIGHT_EDGE, HEADER_HEIGHT+PAGE_MARGIN)
        cr.line_to(RIGHT_EDGE, TABLE_TOP)

        cr.move_to(PAGE_MARGIN, TABLE_TOP)
        cr.line_to(RIGHT_EDGE, TABLE_TOP)
        
        #Draw table headings
        right_txt = RIGHT_EDGE
        dindex = 0
        for data in self.heading:
            right_txt -= MARGIN+LINE
            self.pangolayout.set_text(data)
            (width, height) = self.pangolayout.get_size()
            if (width / pango.SCALE) > self.cols_width[dindex]:
                res = data.split()
                self.pangolayout.set_text(res[0])
                (width, height) = self.pangolayout.get_size()
                if (width / pango.SCALE) < self.cols_width[dindex]:
                    #self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
                    cr.move_to (right_txt -(width / pango.SCALE), HEADER_HEIGHT+PAGE_MARGIN + (HEADING_HEIGHT/2-(height / pango.SCALE))/2)
                    self.pangocairo.show_layout(self.pangolayout)
                    #
                    self.pangolayout.set_text(res[1])
                    (width, height) = self.pangolayout.get_size()
                    #self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
                    cr.move_to (right_txt -(width / pango.SCALE), HEADER_HEIGHT+PAGE_MARGIN + ((HEADING_HEIGHT*3)/2-(height / pango.SCALE))/2)
                    self.pangocairo.show_layout(self.pangolayout)                    
            else:
                #self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
                cr.move_to (right_txt -(width / pango.SCALE), HEADER_HEIGHT+PAGE_MARGIN + (HEADING_HEIGHT-(height / pango.SCALE))/2)
                self.pangocairo.show_layout(self.pangolayout)
        
            right_txt -= self.cols_width[dindex]
            cr.move_to(right_txt, HEADER_HEIGHT + PAGE_MARGIN)
            cr.line_to(right_txt, TABLE_TOP)
            
            dindex += 1
            
        #Draw table data
        rindex = page_nr * self.lines_per_page
        offset = 0
        
        right_txt = RIGHT_EDGE
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
        
        self.pangolayout.set_text("----")
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        
        for i in range(0, 3):
            right_txt -= MARGIN + LINE
            cr.move_to (right_txt -(width / pango.SCALE), TABLE_TOP + (ROW_HEIGHT-(height / pango.SCALE))/2)
            self.pangocairo.show_layout(self.pangolayout)    
            right_txt -= self.cols_width[i]
            cr.move_to(right_txt, TABLE_TOP)
            cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
        
        right_txt -= MARGIN + LINE
        self.pangolayout.set_text(_("Sum of previous page"))
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), TABLE_TOP + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[3]
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
        
        right_txt -= MARGIN + LINE
        if page_nr == 0:
            self.pangolayout.set_text("0")
            self.debt_sum = 0
        else:
            self.pangolayout.set_text(utility.showNumber(self.debt_sum))
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), TABLE_TOP + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[4]
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
        
        right_txt -= MARGIN + LINE
        if page_nr == 0:
            self.pangolayout.set_text("0")
            self.credit_sum = 0
        else:
            self.pangolayout.set_text(utility.showNumber(self.credit_sum))
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), TABLE_TOP + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[5]
        cr.move_to(right_txt, TABLE_TOP)
        cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
        
        addh= ROW_HEIGHT + TABLE_TOP
        try:
            while (offset < self.lines_per_page):
                row = self.content[rindex + offset]
                
                cr.move_to(RIGHT_EDGE, addh)
                cr.line_to(RIGHT_EDGE, addh+ROW_HEIGHT)
                
                right_txt = RIGHT_EDGE
                dindex = 0
                for data in row:
                    right_txt -= MARGIN+LINE
                    self.pangolayout.set_text(data)
                    (width, height) = self.pangolayout.get_size()
                    self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
                    cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
                    self.pangocairo.show_layout(self.pangolayout)
                
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
        
        self.pangolayout.set_text("----")
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        
        for i in range(0, 3):
            right_txt -= MARGIN + LINE
            cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
            self.pangocairo.show_layout(self.pangolayout)    
            right_txt -= self.cols_width[i]
            cr.move_to(right_txt, addh)
            cr.line_to(right_txt, addh + ROW_HEIGHT)
        
        right_txt -= MARGIN + LINE
        self.pangolayout.set_text(_("Sum"))
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[3]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)
        
        right_txt -= MARGIN + LINE
        self.pangolayout.set_text(utility.showNumber(self.debt_sum))
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[4]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)
        
        right_txt -= MARGIN + LINE
        self.pangolayout.set_text(utility.showNumber(self.credit_sum))
        (width, height) = self.pangolayout.get_size()
        self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
        cr.move_to (right_txt -(width / pango.SCALE), addh + (ROW_HEIGHT-(height / pango.SCALE))/2)
        self.pangocairo.show_layout(self.pangolayout)    
        right_txt -= self.cols_width[5]
        cr.move_to(right_txt, addh)
        cr.line_to(right_txt, addh + ROW_HEIGHT)
        
        cr.move_to(self.page_margin, addh + ROW_HEIGHT)
        cr.line_to(RIGHT_EDGE, addh + ROW_HEIGHT)
            
        cr.stroke()
        
    def setDrawFunction(self, func):
        self.drawfunction = func
         
#    def dailySpecific(self, pos, page):
#        right_txt = 570
#        MARGIN = self.cell_margin
#        LINE = self.line
#        ROW_HEIGHT = self.row_height
#        TABLE_TOP = self.header_height + self.heading_height + self.page_margin
#        cr = self.cairo_context
#        
#        row_nr = page * self.lines_per_page + pos
#        try:
#            self.debt_sum += int(self.content[row_nr-1][4].replace(",", ""))
#            self.credit_sum += int(self.content[row_nr-1][5].replace(",", ""))
#        except AttributeError:
#            self.debt_sum = int(self.content[row_nr-1][4].replace(",", ""))
#            self.credit_sum = int(self.content[row_nr-1][5].replace(",", ""))
#           
#        if pos == 1 or pos == self.lines_per_page or row_nr == len(self.content):
#            if pos != 1:
#                TABLE_TOP += (pos + 1) * ROW_HEIGHT
#                cr.move_to(self.page_margin, TABLE_TOP + ROW_HEIGHT)
#                cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
#                
#            cr.move_to(right_txt, TABLE_TOP)
#            cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
#            
#            self.pangolayout.set_text("----")
#            (width, height) = self.pangolayout.get_size()
#            self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
#            
#            for i in range(0, 3):
#                right_txt -= MARGIN + LINE
#                cr.move_to (right_txt -(width / pango.SCALE), TABLE_TOP + (ROW_HEIGHT-(height / pango.SCALE))/2)
#                self.pangocairo.show_layout(self.pangolayout)    
#                right_txt -= self.cols_width[i]
#                cr.move_to(right_txt, TABLE_TOP)
#                cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
#            
#            right_txt -= MARGIN + LINE
#            if pos == 1:
#                self.pangolayout.set_text(_("Sum of previous page"))
#            else:
#                self.pangolayout.set_text(_("Sum"))    
#                
#            (width, height) = self.pangolayout.get_size()
#            self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
#            cr.move_to (right_txt -(width / pango.SCALE), TABLE_TOP + (ROW_HEIGHT-(height / pango.SCALE))/2)
#            self.pangocairo.show_layout(self.pangolayout)    
#            right_txt -= self.cols_width[3]
#            cr.move_to(right_txt, TABLE_TOP)
#            cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
#            
#            right_txt -= MARGIN + LINE
#            if page == 0 and pos == 1:
#                self.pangolayout.set_text("0")
#            else:
#                self.pangolayout.set_text(utility.showNumber(self.debt_sum))
#            (width, height) = self.pangolayout.get_size()
#            self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
#            cr.move_to (right_txt -(width / pango.SCALE), TABLE_TOP + (ROW_HEIGHT-(height / pango.SCALE))/2)
#            self.pangocairo.show_layout(self.pangolayout)    
#            right_txt -= self.cols_width[4]
#            cr.move_to(right_txt, TABLE_TOP)
#            cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
#            
#            right_txt -= MARGIN + LINE
#            if page == 0 and pos == 1:
#                self.pangolayout.set_text("0")
#            else:
#                self.pangolayout.set_text(utility.showNumber(self.credit_sum))
#            (width, height) = self.pangolayout.get_size()
#            self.pangolayout.set_alignment(pango.ALIGN_RIGHT)
#            cr.move_to (right_txt -(width / pango.SCALE), TABLE_TOP + (ROW_HEIGHT-(height / pango.SCALE))/2)
#            self.pangocairo.show_layout(self.pangolayout)    
#            right_txt -= self.cols_width[5]
#            cr.move_to(right_txt, TABLE_TOP)
#            cr.line_to(right_txt, TABLE_TOP + ROW_HEIGHT)
    
    def subjectSpecific(self, pos, page):
        pass
        
    def docSpecific(self, pos, page):
        pass
            
    